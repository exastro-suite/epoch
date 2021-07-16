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

from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

logger = logging.getLogger('apilog')

@require_http_methods(['POST'])
@csrf_exempt
def index(request, workspace_id):
    logger.debug("manifestParameter:{}, workspace_id:{}".format(request.method, workspace_id))

    if request.method == 'POST':
        return post(request, workspace_id)
    else:
        return ""

@csrf_exempt    
def post(request, workspace_id):
    try:

        # ヘッダ情報
        post_headers = {
            'Content-Type': 'application/json',
        }

        # 引数をJSON形式で受け取りそのまま引数に設定
        post_data = request.body

        # PUT送信（workspace更新）
        apiInfo = "{}://{}:{}".format(os.environ['EPOCH_RS_WORKSPACE_PROTOCOL'], os.environ['EPOCH_RS_WORKSPACE_HOST'], os.environ['EPOCH_RS_WORKSPACE_PORT'])
        logger.debug ("workspace put call: worksapce_id:{}".format(workspace_id))
        request_response = requests.put( "{}/workspace/{}/manifestParameter".format(apiInfo, workspace_id), headers=post_headers, data=post_data)
        # エラーの際は処理しない
        if request_response.status_code != 200:
            raise Exception(request_response.text)

        # ヘッダ情報
        post_headers = {
            'Content-Type': 'application/json',
        }

        # 引数をJSON形式で受け取りそのまま引数に設定
        post_data = request.body

        # 呼び出すapiInfoは、環境変数より取得
        apiInfo = "{}://{}:{}".format(os.environ["EPOCH_CICD_PROTOCOL"], os.environ["EPOCH_CICD_HOST"], os.environ["EPOCH_CICD_PORT"])
        logger.debug ("apiInfo:" + apiInfo)

        output = []
        # Manifestパラメータ設定(ITA)
        logger.debug ("ita/manifestParameter post call: worksapce_id:{}".format(workspace_id))
        request_response = requests.post( "{}/ita/manifestParameter".format(apiInfo), headers=post_headers, data=post_data)
        logger.debug("ita/manifestParameter:response:" + request_response.text.encode().decode('unicode-escape'))
        ret = json.loads(request_response.text)
        #ret = request_response.text
        logger.debug(ret["result"])
        if request_response.status_code == 200:
            output.append(ret["output"])
        else:
            raise Exception(request_response.text)

        response = {
            "result":"200",
            "output" : output,
        }
        
        return JsonResponse(response, status=200)

    except Exception as e:
        response = {
            "result":"500",
            "returncode": "0601",
            "args": e.args,
            "output": e.args,
            "traceback": traceback.format_exc(),
        }
        return JsonResponse(response, status=500)


