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
ita_menu_manifest_template = '2100040704'

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


@require_http_methods(['POST'])
@csrf_exempt
def post(request):

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

    print(json.loads(request.body))

    #
    # マニフェストテンプレートの取得
    #
    content = {
        "1": {
            "NORMAL": "0"
        },
        "3": {
            "NORMAL": "TPF_epoch_template_yaml"
        },
    }
    manitpl_resp = requests.post(ita_restapi_endpoint + '?no=' + ita_menu_manifest_template, headers=filter_headers, data=json.dumps(content))
    manitpl_json = json.loads(manitpl_resp.text)
    print('---- Current Manifest Templates ----')
    # print(manitpl_resp.text)
    print(manitpl_json)

    req_data = json.loads(request.body)['manifests']
    mani_req_len = len(req_data)
    mani_ita_len = manitpl_json['resultdata']['CONTENTS']['RECORD_LENGTH']
    max_loop_cnt = max(mani_req_len, mani_ita_len)
    print("max_loop_cnt: " + str(max_loop_cnt))

    ita_data = manitpl_json['resultdata']['CONTENTS']["BODY"]
    ita_data.pop(0)
    print(ita_data)

    edit_data = {
        "UPLOAD_FILE": []
    }
    tpl_cnt = 0
    for i in range(max_loop_cnt):

        # ITAを廃止
        if i > mani_req_len - 1:
            tmp_data = []
            for j, item in enumerate(ita_data[i]):
                if j == 0:
                    tmp_data.append('廃止')
                else:
                    tmp_data.append(item)

            edit_data[str(i)] = tmp_data

        # ITAに新規登録する
        elif i > mani_ita_len - 1:
            tpl_cnt += 1
            tmp_data = {}
            tmp_data['0'] = "登録"
            tmp_data['3'] = "TPF_epoch_template_yaml" + str(tpl_cnt)
            tmp_data['4'] = req_data[i]["file_name"]
            tmp_data['5'] = "VAR_replicas:\n"\
                            "VAR_image:\n"\
                            "VAR_image_tag:"

            edit_data[str(i)] = tmp_data
            edit_data["UPLOAD_FILE"].append({"4": base64.b64encode(req_data[i]["file_text"].encode()).decode()})

        # ITAを更新する
        else:
            tpl_cnt += 1
            tmp_data = ita_data[i]
            tmp_data[0] = "更新"
            tmp_data[3] = "TPF_epoch_template_yaml" + str(tpl_cnt)
            tmp_data[4] = req_data[i]["file_name"]
            tmp_data[5] = "VAR_replicas:\n"\
                          "VAR_image:\n"\
                          "VAR_image_tag:"

            edit_data[str(i)] = tmp_data
            edit_data["UPLOAD_FILE"].append({"4": base64.b64encode(req_data[i]["file_text"].encode()).decode()})

    print(edit_data)

    # ITAへREST実行
    manutemplate_edit_resp = requests.post(ita_restapi_endpoint + '?no=' + ita_menu_manifest_template, headers=edit_headers, data=json.dumps(edit_data))
    manitemplate_json = json.loads(manutemplate_edit_resp.text)

    print(manitemplate_json)

    response = {
        "result": "200",
        "output": "登録に成功しました。",
        "datetime": datetime.datetime.now(pytz.timezone('Asia/Tokyo')).strftime('%Y/%m/%d %H:%M:%S'),
    }

    return JsonResponse(response, status=200)

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

        print('git_url:' + git_url)
        print('row[column_indexes[remarks]]:' + row[column_indexes['remarks']])
        if git_url == row[column_indexes['remarks']]:
            # 備考にgit_urlが含まれているとき
            print('find: (idx) ' + str(idx))
            return idx

    # 存在しないとき
    print('not found: -1')
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

        # print('operation_id:')
        # print(operation_id)
        # print('row[column_indexes[remarks]]:')
        # print(row[column_indexes['remarks']])
        if operation_id == row[column_indexes['operation_id']]:
            # 備考にgit_urlが含まれているとき
            print('find:' + str(idx))
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
def search_manitpl(manitpl, column_indexes, git_url):
    for idx, row in enumerate(manitpl):
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
