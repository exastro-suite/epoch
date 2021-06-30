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
import logging

from django.shortcuts import render
from django.http import HttpResponse
from django.http.response import JsonResponse
from rest_framework import status

from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

# 項目名リスト
column_names_opelist = {
    'operation_id': 'オペレーションID',
    'operation_name': 'オペレーション名',
    'operation_date': '実施予定日時',
    'remarks': '備考',
}

COND_CLASS_NO_CD_EXEC = 2

logger = logging.getLogger('apilog')

@require_http_methods(['POST'])
@csrf_exempt
def index(request):
    logger.debug("cdExecDesignation:{}".format(request.method))
    if request.method == 'POST':
        return post(request)
    else:
        return ""

@csrf_exempt    
def post(request):
    try:

        # ヘッダ情報
        post_headers = {
            'Content-Type': 'application/json',
        }

        # 呼び出すapiInfoは環境変数より取得
        apiInfo = "{}://{}:{}".format(os.environ["EPOCH_CICD_PROTOCOL"], os.environ["EPOCH_CICD_HOST"], os.environ["EPOCH_CICD_PORT"])
        logger.debug ("cicd url:" + apiInfo)

        # オペレーション一覧の取得(ITA)
        request_response = requests.get( apiInfo + "/ita/operations", headers=post_headers)
        logger.debug("ita/cdExec:operations:" + request_response.text)
        ret = json.loads(request_response.text)

        # 項目位置の取得
        column_indexes_opelist = column_indexes(column_names_opelist, ret['resultdata']['CONTENTS']['BODY'][0])
        logger.debug('---- Operation Index ----')
        logger.debug(column_indexes_opelist)

        # 引数のgit urlをもとにオペレーションIDを取得
        ope_id = search_opration_id(ret['resultdata']['CONTENTS']['BODY'], column_indexes_opelist, row_req['git_url'])
        if ope_id is None:
            raise Exception("Operation ID Not found!")

        # CD実行の引数を設定
        post_data = {
            "operation_id" : ope_id,
            "conductor_class_no" : COND_CLASS_NO_CD_EXEC,
            "preserve_datetime" : request.body["preserveDatetime"]
        }

        output = []
        # CD実行(ITA)
        request_response = requests.post( apiInfo + "/ita/cdExec", headers=post_headers, data=post_data)
        logger.debug("ita/cdExec:response:" + request_response.text)
        ret = json.loads(request_response.text)
        #ret = request_response.text
        logger.debug(ret["result"])
        if ret["result"] == "200" or ret["result"] == "201":
            output.append(ret["output"])
        else:
            return (request_response.text)

        response = {
            "result":"200",
            "output" : output,
        }
        return JsonResponse(response, status=status.HTTP_200_OK)

    except Exception as e:
        logger.debug(traceback.format_exc())
        response = {
            "result":"500",
            "returncode": "0201",
            "args": e.args,
            "output": e.args,
            "traceback": traceback.format_exc(),
        }
        return JsonResponse(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#
# オペレーションの検索
#
def search_opration_id(opelist, column_indexes, git_url):
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
            return row[column_indexes['operation_id']

    # 存在しないとき
    return None

