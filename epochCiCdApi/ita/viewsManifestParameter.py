#   Copyright 2019 NEC Corporation
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import cgi # CGIモジュールのインポート
import cgitb
import sys
import requests
import json
import subprocess
import traceback
import os
import datetime, pytz
import base64
import io
import logging

from django.shortcuts import render
from django.http import HttpResponse
from django.http.response import JsonResponse

from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

ita_host = os.environ['EPOCH_ITA_HOST']
ita_port = os.environ['EPOCH_ITA_PORT']
ita_user = os.environ['EPOCH_ITA_USER']
ita_pass = os.environ['EPOCH_ITA_PASSWORD']

# メニューID
ite_menu_operation = '2100000304'
ita_menu_manifest_param = '0000000001'

# 共通項目
column_indexes_common = {
    "method": 0,    # 実行処理種別
    "delete": 1,    # 廃止
    "record_no": 2, # No
}
column_names_opelist = {
    'operation_id': 'オペレーションID',
    'operation_name': 'オペレーション名',
    'operation_date': '実施予定日時',
    'remarks': '備考',
}
# 項目名リスト
column_names_manifest_param = {
    'host' : 'ホスト名',
    'operation_id' : 'オペレーション/ID',
    'operation' : 'オペレーション/オペレーション',
    'indexes' : '代入順序',
    'replicas' : 'パラメータ/replicas',
    'image' : 'パラメータ/image',
    'image_tag' : 'パラメータ/image_tag',
    'template_name' : 'パラメータ/template_name',
    'lastupdate' : '更新用の最終更新日時',
}

param_value_host= os.environ['EPOCH_ITA_WORKER_HOST']
param_value_method_entry='登録'
param_value_method_update='更新'

ita_restapi_endpoint='http://' + ita_host + ':' + ita_port + '/default/menu/07_rest_api_ver1.php'

logger = logging.getLogger('apilog')

@require_http_methods(['POST'])
@csrf_exempt
def post(request):

    logger.debug("CALL " + __name__)
    try:
        # HTTPヘッダの生成
        filter_headers = {
            'host': ita_host + ':' + ita_port,
            'Content-Type': 'application/json',
            'Authorization': base64.b64encode((ita_user + ':' + ita_pass).encode()),
            'X-Command': 'FILTER',
        }

        edit_headers = {
            'host': ita_host + ':' + ita_port,
            'Content-Type': 'application/json',
            'Authorization': base64.b64encode((ita_user + ':' + ita_pass).encode()),
            'X-Command': 'EDIT',
        }

        logger.debug(json.loads(request.body))

        #
        # オペレーションの取得
        #
        opelist_resp = requests.post(ita_restapi_endpoint + '?no=' + ite_menu_operation, headers=filter_headers)
        opelist_json = json.loads(opelist_resp.text)
        logger.debug('---- Operation ----')
        # logger.debug(opelist_resp.text)
        # logger.debug(opelist_json)

        # 項目位置の取得
        column_indexes_opelist = column_indexes(column_names_opelist, opelist_json['resultdata']['CONTENTS']['BODY'][0])
        logger.debug('---- Operation Index ----')
        # logger.debug(column_indexes_opelist)

        #
        # マニフェスト環境パラメータの取得
        #
        content = {
            "1": {
                "NORMAL": "0"
            }
        }
        maniparam_resp = requests.post(ita_restapi_endpoint + '?no=' + ita_menu_manifest_param, headers=filter_headers, data=json.dumps(content))
        maniparam_json = json.loads(maniparam_resp.text)
        logger.debug('---- Current Manifest Parameters ----')
        # logger.debug(maniparam_resp.text)
        # logger.debug(maniparam_json)

        # 項目位置の取得
        column_indexes_maniparam = column_indexes(column_names_manifest_param, maniparam_json['resultdata']['CONTENTS']['BODY'][0])
        logger.debug('---- Manifest Parameters Index ----')
        # logger.debug(column_indexes_maniparam)

        # Responseデータの初期化
        response = {"result":"200",}

        # マニフェスト環境パラメータのデータ成型
        maniparam_edit = []
        for environment in json.loads(request.body)['ci_config']['environments']:

            idx_ope = search_opration(opelist_json['resultdata']['CONTENTS']['BODY'], column_indexes_opelist, environment['git_url'])

            # ITAからオペレーション(=環境)が取得できなければ異常
            if idx_ope == -1:
                response = {
                    "result": "400",
                    "output": "CD環境が設定されていません。",
                    "datetime": datetime.datetime.now(pytz.timezone('Asia/Tokyo')).strftime('%Y/%m/%d %H:%M:%S'),
                }
                return JsonResponse(response, status=400)

                
            req_maniparam_operation_id = opelist_json['resultdata']['CONTENTS']['BODY'][idx_ope][column_indexes_common['record_no']]

            for idx_manifile, row_manifile in enumerate(environment['manifests']):

                # parameters成型
                for key, value in row_manifile['parameters'].items():
                    if key == 'replicas':
                        replicas = value
                    elif key == 'image':
                        image = value
                    elif key == 'image_tag':
                        image_tag = value

                # 既存データ確認
                maniparam_id = -1
                for idx_maniparam, row_maniparam in enumerate(maniparam_json['resultdata']['CONTENTS']['BODY']):
                    current_maniparam_operation_id = row_maniparam[column_indexes_maniparam['operation_id']]
                    current_maniparam_include_index = row_maniparam[column_indexes_maniparam['indexes']]
                    if current_maniparam_operation_id == req_maniparam_operation_id and \
                            current_maniparam_include_index == str(idx_manifile + 1):
                        maniparam_id = row_maniparam[column_indexes_common['record_no']]
                        break

                if maniparam_id == -1:
                    # 追加処理データの設定
                    maniparam_edit.append(
                        {
                            str(column_indexes_common['method']) : param_value_method_entry,
                            str(column_indexes_maniparam['host']) : param_value_host,
                            str(column_indexes_maniparam['operation']) : format_opration_info(opelist_json['resultdata']['CONTENTS']['BODY'][idx_ope], column_indexes_opelist),
                            str(column_indexes_maniparam['indexes']) : idx_manifile + 1,
                            str(column_indexes_maniparam['replicas']) : replicas,
                            str(column_indexes_maniparam['image']) : image,
                            str(column_indexes_maniparam['image_tag']) : image_tag,
                            str(column_indexes_maniparam['template_name']) : '"{{ TPF_epoch_template_yaml' + str(idx_manifile + 1) + ' }}"',
                        }
                    )
                    logger.debug('---- Manifest Parameters Item(Add) ----')
                    # logger.debug(maniparam_edit[len(maniparam_edit) -1])

                else:
                    # 更新処理
                    maniparam_edit.append(
                        {
                            str(column_indexes_common['method']) : param_value_method_update,
                            str(column_indexes_common['record_no']) : maniparam_id,
                            str(column_indexes_maniparam['host']) : maniparam_json['resultdata']['CONTENTS']['BODY'][idx_maniparam][column_indexes_maniparam['host']],
                            str(column_indexes_maniparam['operation']) : maniparam_json['resultdata']['CONTENTS']['BODY'][idx_maniparam][column_indexes_maniparam['operation']],
                            str(column_indexes_maniparam['indexes']) : maniparam_json['resultdata']['CONTENTS']['BODY'][idx_maniparam][column_indexes_maniparam['indexes']],
                            str(column_indexes_maniparam['replicas']) : replicas,
                            str(column_indexes_maniparam['image']) : image,
                            str(column_indexes_maniparam['image_tag']) : image_tag,
                            str(column_indexes_maniparam['template_name']) : maniparam_json['resultdata']['CONTENTS']['BODY'][idx_maniparam][column_indexes_maniparam['template_name']],
                            str(column_indexes_maniparam['lastupdate']) : maniparam_json['resultdata']['CONTENTS']['BODY'][idx_maniparam][column_indexes_maniparam['lastupdate']],
                        }
                    )
                    logger.debug('---- Manifest Parameters Item(Update) ----')
                    # logger.debug(maniparam_edit[len(maniparam_edit) -1])

        logger.debug('---- Updating Manifest Parameters ----')
        # logger.debug(json.dumps(maniparam_edit))

        manuparam_edit_resp = requests.post(ita_restapi_endpoint + '?no=' + ita_menu_manifest_param, headers=edit_headers, data=json.dumps(maniparam_edit))
        maniparam_json = json.loads(manuparam_edit_resp.text)

        logger.debug('---- Manifest Parameters Post Response ----')
        # logger.debug(manuparam_edit_resp.text)
        # logger.debug(maniparam_json)

        # response['ita_response'] = maniparam_json
        response = {
            "result": "200",
            # "output": maniparam_json['resultdata'],
            "output": "登録に成功しました。",
            "datetime": datetime.datetime.now(pytz.timezone('Asia/Tokyo')).strftime('%Y/%m/%d %H:%M:%S'),
        }

        return JsonResponse(response, status=200)

    except Exception as e:
        logger.debug(e)
        logger.debug("traceback:" + traceback.format_exc())
        response = {
            "result": "500",
            "output": traceback.format_exc(),
            "datetime": datetime.datetime.now(pytz.timezone('Asia/Tokyo')).strftime('%Y/%m/%d %H:%M:%S'),
        }
        return JsonResponse(response, status=500)

#
# 項目位置の取得
#
def column_indexes(column_names, row_header):
    column_indexes = {}
    for idx in column_names:
        column_indexes[idx] = row_header.index(column_names[idx])
    return column_indexes

#
# オペレーションの検索
#
def search_opration(opelist, column_indexes, git_url):
    for idx, row in enumerate(opelist):
        if idx == 0:
            # 1行目はヘッダなので読み飛ばし
            continue

        if row[column_indexes_common["delete"]] != "":
            # 削除は無視
            continue

        if row[column_indexes['remarks']] is None:
            # 備考設定なしは無視
            continue

        logger.debug('git_url:' + git_url)
        logger.debug('row[column_indexes[remarks]]:' + row[column_indexes['remarks']])
        if git_url == row[column_indexes['remarks']]:
            # 備考にgit_urlが含まれているとき
            logger.debug('find: (idx) ' + str(idx))
            return idx

    # 存在しないとき
    logger.debug('not found: -1')
    return -1

#
# GitUrlの検索
#
def search_git_url(opelist, column_indexes, operation_id):
    for idx, row in enumerate(opelist):
        if idx == 0:
            # 1行目はヘッダなので読み飛ばし
            continue

        if row[column_indexes_common["delete"]] != "":
            # 削除は無視
            continue

        # logger.debug('operation_id:')
        # logger.debug(operation_id)
        # logger.debug('row[column_indexes[remarks]]:')
        # logger.debug(row[column_indexes['remarks']])
        if operation_id == row[column_indexes['operation_id']]:
            # 備考にgit_urlが含まれているとき
            logger.debug('find:' + str(idx))
            return row[column_indexes['remarks']]

    # 存在しないとき
    return -1

#
# オペレーション選択文字列の生成
#
def format_opration_info(operow, column_indexes):
    return operow[column_indexes['operation_date']] + '_' + operow[column_indexes['operation_id']] + ':' + operow[column_indexes['operation_name']]

#
# git情報の検索
#
def search_maniparam(maniparam, column_indexes, git_url):
    for idx, row in enumerate(maniparam):
        if idx == 0:
            # 1行目はヘッダなので読み飛ばし
            continue

        if row[column_indexes_common["delete"]] != "":
            # 削除は無視
            continue

        if git_url == row[column_indexes['git_url']]:
            # git_urlが存在したとき
            return idx

    # 存在しないとき
    return -1
