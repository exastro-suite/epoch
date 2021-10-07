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

from epochCiCdApi.views_access import get_access_info

ita_host = os.environ['EPOCH_ITA_HOST']
ita_port = os.environ['EPOCH_ITA_PORT']

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
    'image' : 'パラメータ/固定パラメータ/image',
    'image_tag' : 'パラメータ/固定パラメータ/image_tag',
    'param01' : 'パラメータ/汎用パラメータ/param01',
    'param02' : 'パラメータ/汎用パラメータ/param02',
    'param03' : 'パラメータ/汎用パラメータ/param03',
    'param04' : 'パラメータ/汎用パラメータ/param04',
    'param05' : 'パラメータ/汎用パラメータ/param05',
    'param06' : 'パラメータ/汎用パラメータ/param06',
    'param07' : 'パラメータ/汎用パラメータ/param07',
    'param08' : 'パラメータ/汎用パラメータ/param08',
    'param09' : 'パラメータ/汎用パラメータ/param09',
    'param10' : 'パラメータ/汎用パラメータ/param10',
    'param11' : 'パラメータ/汎用パラメータ/param11',
    'param12' : 'パラメータ/汎用パラメータ/param12',
    'param13' : 'パラメータ/汎用パラメータ/param13',
    'param14' : 'パラメータ/汎用パラメータ/param14',
    'param15' : 'パラメータ/汎用パラメータ/param15',
    'param16' : 'パラメータ/汎用パラメータ/param16',
    'param17' : 'パラメータ/汎用パラメータ/param17',
    'param18' : 'パラメータ/汎用パラメータ/param18',
    'param19' : 'パラメータ/汎用パラメータ/param19',
    'param20' : 'パラメータ/汎用パラメータ/param20',
    'template_name' : 'パラメータ/固定パラメータ/template_name',
    'lastupdate' : '更新用の最終更新日時',
}

param_value_host= os.environ['EPOCH_ITA_WORKER_HOST']
param_value_method_entry='登録'
param_value_method_update='更新'
param_value_method_delete='廃止'

ita_restapi_endpoint='http://' + ita_host + ':' + ita_port + '/default/menu/07_rest_api_ver1.php'

logger = logging.getLogger('apilog')

@require_http_methods(['POST'])
@csrf_exempt
def post(request):

    logger.debug("CALL " + __name__)

    try:

        # ワークスペース複数化するまでは1固定
        workspace_id = 1

        # ワークスペースアクセス情報取得
        access_info = get_access_info(workspace_id)

        ita_user = access_info['ITA_USER']
        ita_pass = access_info['ITA_PASSWORD']

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
        logger.debug(maniparam_json)

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

                image = None
                image_tag = None
                param01 = None
                param02 = None
                param03 = None
                param04 = None
                param05 = None
                param06 = None
                param07 = None
                param08 = None
                param09 = None
                param10 = None
                param11 = None
                param12 = None
                param13 = None
                param14 = None
                param15 = None
                param16 = None
                param17 = None
                param18 = None
                param19 = None
                param20 = None
                # parameters成型
                for key, value in row_manifile['parameters'].items():
                    if key == 'image':
                        image = value
                    elif key == 'image_tag':
                        image_tag = value
                    elif key == 'param01':
                        param01 = value
                    elif key == 'param02':
                        param02 = value
                    elif key == 'param03':
                        param03 = value
                    elif key == 'param04':
                        param04 = value
                    elif key == 'param05':
                        param05 = value
                    elif key == 'param06':
                        param06 = value
                    elif key == 'param07':
                        param07 = value
                    elif key == 'param08':
                        param08 = value
                    elif key == 'param09':
                        param09 = value
                    elif key == 'param10':
                        param10 = value
                    elif key == 'param11':
                        param11 = value
                    elif key == 'param12':
                        param12 = value
                    elif key == 'param13':
                        param13 = value
                    elif key == 'param14':
                        param14 = value
                    elif key == 'param15':
                        param15 = value
                    elif key == 'param16':
                        param16 = value
                    elif key == 'param17':
                        param17 = value
                    elif key == 'param18':
                        param18 = value
                    elif key == 'param19':
                        param19 = value
                    elif key == 'param20':
                        param20 = value

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
                            str(column_indexes_maniparam['image']) : image,
                            str(column_indexes_maniparam['image_tag']) : image_tag,
                            str(column_indexes_maniparam['param01']) : param01,
                            str(column_indexes_maniparam['param02']) : param02,
                            str(column_indexes_maniparam['param03']) : param03,
                            str(column_indexes_maniparam['param04']) : param04,
                            str(column_indexes_maniparam['param05']) : param05,
                            str(column_indexes_maniparam['param06']) : param06,
                            str(column_indexes_maniparam['param07']) : param07,
                            str(column_indexes_maniparam['param08']) : param08,
                            str(column_indexes_maniparam['param09']) : param09,
                            str(column_indexes_maniparam['param10']) : param10,
                            str(column_indexes_maniparam['param11']) : param11,
                            str(column_indexes_maniparam['param12']) : param12,
                            str(column_indexes_maniparam['param13']) : param13,
                            str(column_indexes_maniparam['param14']) : param14,
                            str(column_indexes_maniparam['param15']) : param15,
                            str(column_indexes_maniparam['param16']) : param16,
                            str(column_indexes_maniparam['param17']) : param17,
                            str(column_indexes_maniparam['param18']) : param18,
                            str(column_indexes_maniparam['param19']) : param19,
                            str(column_indexes_maniparam['param20']) : param20,
                            str(column_indexes_maniparam['template_name']) : '"{{ TPF_epoch_template_yaml' + str(idx_manifile + 1) + ' }}"',
                        }
                    )
                    logger.debug('---- Manifest Parameters Item(Add) ----')
                    logger.debug(maniparam_edit[len(maniparam_edit) -1])

                else:
                    # 更新処理
                    maniparam_edit.append(
                        {
                            str(column_indexes_common['method']) : param_value_method_update,
                            str(column_indexes_common['record_no']) : maniparam_id,
                            str(column_indexes_maniparam['host']) : maniparam_json['resultdata']['CONTENTS']['BODY'][idx_maniparam][column_indexes_maniparam['host']],
                            str(column_indexes_maniparam['operation']) : maniparam_json['resultdata']['CONTENTS']['BODY'][idx_maniparam][column_indexes_maniparam['operation']],
                            str(column_indexes_maniparam['indexes']) : maniparam_json['resultdata']['CONTENTS']['BODY'][idx_maniparam][column_indexes_maniparam['indexes']],
                            str(column_indexes_maniparam['image']) : image,
                            str(column_indexes_maniparam['image_tag']) : image_tag,
                            str(column_indexes_maniparam['param01']) : param01,
                            str(column_indexes_maniparam['param02']) : param02,
                            str(column_indexes_maniparam['param03']) : param03,
                            str(column_indexes_maniparam['param04']) : param04,
                            str(column_indexes_maniparam['param05']) : param05,
                            str(column_indexes_maniparam['param06']) : param06,
                            str(column_indexes_maniparam['param07']) : param07,
                            str(column_indexes_maniparam['param08']) : param08,
                            str(column_indexes_maniparam['param09']) : param09,
                            str(column_indexes_maniparam['param10']) : param10,
                            str(column_indexes_maniparam['param11']) : param11,
                            str(column_indexes_maniparam['param12']) : param12,
                            str(column_indexes_maniparam['param13']) : param13,
                            str(column_indexes_maniparam['param14']) : param14,
                            str(column_indexes_maniparam['param15']) : param15,
                            str(column_indexes_maniparam['param16']) : param16,
                            str(column_indexes_maniparam['param17']) : param17,
                            str(column_indexes_maniparam['param18']) : param18,
                            str(column_indexes_maniparam['param19']) : param19,
                            str(column_indexes_maniparam['param20']) : param20,
                            str(column_indexes_maniparam['template_name']) : maniparam_json['resultdata']['CONTENTS']['BODY'][idx_maniparam][column_indexes_maniparam['template_name']],
                            str(column_indexes_maniparam['lastupdate']) : maniparam_json['resultdata']['CONTENTS']['BODY'][idx_maniparam][column_indexes_maniparam['lastupdate']],
                        }
                    )
                    logger.debug('---- Manifest Parameters Item(Update) ----')
                    logger.debug(maniparam_edit[len(maniparam_edit) -1])

        logger.debug('---- Deleting Manifest Parameters Setting ----')
        # 既存データをすべて廃止する
        for idx_maniparam, row_maniparam in enumerate(maniparam_json['resultdata']['CONTENTS']['BODY']):
            # 1行目無視する
            if idx_maniparam == 0:
                continue
            flgExists = False
            for idx_edit, row_edit in enumerate(maniparam_edit):
                # 該当するrecord_noがあれば、チェックする
                if str(column_indexes_common['record_no']) in row_edit:
                    if row_edit[str(column_indexes_common['record_no'])] == row_maniparam[column_indexes_common['record_no']]:
                        flgExists = True
                        break
            
            # 該当するレコードがない場合は、廃止として追加する
            if not flgExists:
                # 削除用のデータ設定
                maniparam_edit.append(
                    {
                        str(column_indexes_common['method']) : param_value_method_delete,
                        str(column_indexes_common['record_no']) : row_maniparam[column_indexes_common['record_no']],
                        str(column_indexes_maniparam['lastupdate']) : row_maniparam[column_indexes_maniparam['lastupdate']],
                    }
                )

        logger.debug('---- Updating Manifest Parameters ----')
        logger.debug(json.dumps(maniparam_edit))

        manuparam_edit_resp = requests.post(ita_restapi_endpoint + '?no=' + ita_menu_manifest_param, headers=edit_headers, data=json.dumps(maniparam_edit))
        maniparam_json = json.loads(manuparam_edit_resp.text)

        logger.debug('---- Manifest Parameters Post Response ----')
        # logger.debug(manuparam_edit_resp.text)
        logger.debug(maniparam_json)

        if maniparam_json["status"] != "SUCCEED" or maniparam_json["resultdata"]["LIST"]["NORMAL"]["error"]["ct"] != 0:
            raise Exception(manuparam_edit_resp.text.encode().decode('unicode-escape'))

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
