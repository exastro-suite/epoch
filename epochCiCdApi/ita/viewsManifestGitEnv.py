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
import base64
import io
import logging

from django.shortcuts import render
from django.http import HttpResponse
from django.http.response import JsonResponse

from django.views.decorators.csrf import csrf_exempt


ita_host = os.environ['EPOCH_ITA_HOST']
ita_port = os.environ['EPOCH_ITA_PORT']
ita_user = os.environ['EPOCH_ITA_USER']
ita_pass = os.environ['EPOCH_ITA_PASSWORD']

# メニューID
ite_menu_operation = '2100000304'
ita_menu_gitenv_param = '0000000004'

# 共通項目
column_indexes_common = {
    "method": 0,    # 実行処理種別
    "delete": 1,    # 廃止
    "record_no": 2, # No
}
# 項目名リスト
column_names_opelist = {
    'operation_id': 'オペレーションID',
    'operation_name': 'オペレーション名',
    'operation_date': '実施予定日時',
    'remarks': '備考',
}
column_names_gitlist = {
    'host' : 'ホスト名',
    'operation_id' : 'オペレーション/ID',
    'operation' : 'オペレーション/オペレーション',
    'git_url' : 'パラメータ/Git URL',
    'git_user' : 'パラメータ/Git User',
    'git_password' : 'パラメータ/Git Password',
    'lastupdate' : '更新用の最終更新日時',
}

param_value_host= os.environ['EPOCH_ITA_WORKER_HOST']
param_value_method_entry='登録'
param_value_method_update='更新'
param_value_operation_date='2999/12/31 23:59'
param_value_operation_name_prefix='CD実行:'

ita_restapi_endpoint='http://' + ita_host + ':' + ita_port + '/default/menu/07_rest_api_ver1.php'

logger = logging.getLogger('apilog')

@csrf_exempt
def index(request):
#   sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    logger.debug("CALL " + __name__ + ":{}".format(request.method))

    if request.method == 'POST':
        return post(request)
    else:
        return ""

@csrf_exempt
def post(request):

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

        #
        # オペレーションの取得
        #
        opelist_resp = requests.post(ita_restapi_endpoint + '?no=' + ite_menu_operation, headers=filter_headers)
        opelist_json = json.loads(opelist_resp.text)
        logger.debug('---- Operation ----')
        #logger.debug(opelist_resp.text.encode().decode('unicode-escape'))
        logger.debug(opelist_resp.text)

        # 項目位置の取得
        column_indexes_opelist = column_indexes(column_names_opelist, opelist_json['resultdata']['CONTENTS']['BODY'][0])
        logger.debug('---- Operation Index ----')
        logger.debug(column_indexes_opelist)

        #
        # オペレーションの追加処理
        #
        opelist_edit = []
        for idx_req, row_req in enumerate(json.loads(request.body)['ci_config']['environments']):
            if search_opration(opelist_json['resultdata']['CONTENTS']['BODY'], column_indexes_opelist, row_req['git_url']) == -1:
                # オペレーションになければ、追加データを設定
                opelist_edit.append(
                    {
                        str(column_indexes_common['method']) : param_value_method_entry,
                        str(column_indexes_opelist['operation_name']) : param_value_operation_name_prefix + row_req['git_url'],
                        str(column_indexes_opelist['operation_date']) : param_value_operation_date,
                        str(column_indexes_opelist['remarks']) : row_req['git_url'],
                    }
                )

        if len(opelist_edit) > 0:
            #
            # オペレーションの追加がある場合
            #
            ope_add_resp = requests.post(ita_restapi_endpoint + '?no=' + ite_menu_operation, headers=edit_headers, data=json.dumps(opelist_edit))

            logger.debug('---- ope_add_resp ----')
            #logger.debug(ope_add_resp.text.encode().decode('unicode-escape'))
            logger.debug(ope_add_resp.text)

            # 追加後再取得(オペレーションIDが決定する)
            opelist_resp = requests.post(ita_restapi_endpoint + '?no=' + ite_menu_operation, headers=filter_headers)        
            opelist_json = json.loads(opelist_resp.text)
            logger.debug('---- Operation ----')
            #logger.debug(opelist_resp.text.encode().decode('unicode-escape'))

        #
        # Git環境情報の取得
        #
        gitlist_resp = requests.post(ita_restapi_endpoint + '?no=' + ita_menu_gitenv_param, headers=filter_headers)
        gitlist_json = json.loads(gitlist_resp.text)
        logger.debug('---- Git Environments ----')
        #logger.debug(gitlist_resp.text.encode().decode('unicode-escape'))
        logger.debug(gitlist_resp.text)

        # 項目位置の取得
        column_indexes_gitlist = column_indexes(column_names_gitlist, gitlist_json['resultdata']['CONTENTS']['BODY'][0])
        logger.debug('---- Git Environments Index ----')
        logger.debug(column_indexes_gitlist)

        # Responseデータの初期化
        response = {"result":"200", "items":[]}
        # Git環境情報の追加・更新
        gitlist_edit = []
        for idx_req, row_req in enumerate(json.loads(request.body)['ci_config']['environments']):
            idx_git = search_gitlist(gitlist_json['resultdata']['CONTENTS']['BODY'], column_indexes_gitlist, row_req['git_url'])
            if idx_git == -1:
                # リストになければ、追加データを設定
                # 追加対象のURLのオペレーション
                idx_ope = search_opration(opelist_json['resultdata']['CONTENTS']['BODY'], column_indexes_opelist, row_req['git_url'])

                # 追加処理データの設定
                gitlist_edit.append(
                    {
                        str(column_indexes_common['method']) : param_value_method_entry,
                        str(column_indexes_gitlist['host']) : param_value_host,
                        str(column_indexes_gitlist['operation_id']) : opelist_json['resultdata']['CONTENTS']['BODY'][idx_ope][column_indexes_opelist['operation_id']],
                        str(column_indexes_gitlist['operation']) : format_opration_info(opelist_json['resultdata']['CONTENTS']['BODY'][idx_ope], column_indexes_opelist),
                        str(column_indexes_gitlist['git_url']) : row_req['git_url'],
                        str(column_indexes_gitlist['git_user']) : row_req['git_user'],
                        str(column_indexes_gitlist['git_password']) : row_req['git_password'],
                    }
                )

                # レスポンスデータの設定
                response["items"].append(
                    {
                        'operation_id' : opelist_json['resultdata']['CONTENTS']['BODY'][idx_ope][column_indexes_opelist['operation_id']],
                        'git_url' : row_req['git_url'],
                        'git_user' : row_req['git_user'],
                        'git_password' : row_req['git_password'],
                    }
                )

            else:
                # リストにあれば、更新データを設定
                gitlist_edit.append(
                    {
                        str(column_indexes_common['method']) : param_value_method_update,
                        str(column_indexes_common['record_no']) : gitlist_json['resultdata']['CONTENTS']['BODY'][idx_git][column_indexes_common['record_no']],
                        str(column_indexes_gitlist['host']) : gitlist_json['resultdata']['CONTENTS']['BODY'][idx_git][column_indexes_gitlist['host']],
                        str(column_indexes_gitlist['operation']) : gitlist_json['resultdata']['CONTENTS']['BODY'][idx_git][column_indexes_gitlist['operation']],
                        str(column_indexes_gitlist['git_url']) : row_req['git_url'],
                        str(column_indexes_gitlist['git_user']) : row_req['git_user'],
                        str(column_indexes_gitlist['git_password']) : row_req['git_password'],
                        str(column_indexes_gitlist['lastupdate']) : gitlist_json['resultdata']['CONTENTS']['BODY'][idx_git][column_indexes_gitlist['lastupdate']],
                    }
                )

                # レスポンスデータの設定
                response["items"].append(
                    {
                        'operation_id' : gitlist_json['resultdata']['CONTENTS']['BODY'][idx_git][column_indexes_gitlist['operation_id']],
                        'git_url' : row_req['git_url'],
                        'git_user' : row_req['git_user'],
                        'git_password' : row_req['git_password'],
                    }
                )

        logger.debug('---- Git Environments Post ----')
        #logger.debug(json.dumps(gitlist_edit).encode().decode('unicode-escape'))
        logger.debug(json.dumps(gitlist_edit))

        gitlist_edit_resp = requests.post(ita_restapi_endpoint + '?no=' + ita_menu_gitenv_param, headers=edit_headers, data=json.dumps(gitlist_edit))

        logger.debug('---- Git Environments Post Response ----')
        #logger.debug(gitlist_edit_resp.text.encode().decode('unicode-escape'))
        logger.debug(gitlist_edit_resp.text)

        return JsonResponse(response)

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

        logger.debug('git_url:'+git_url)
        logger.debug('row[column_indexes[remarks]]:'+row[column_indexes['remarks']])
        if git_url == row[column_indexes['remarks']]:
            # 備考にgit_urlが含まれているとき
            logger.debug('find:' + str(idx))
            return idx

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
def search_gitlist(gitlist, column_indexes, git_url):
    for idx, row in enumerate(gitlist):
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

