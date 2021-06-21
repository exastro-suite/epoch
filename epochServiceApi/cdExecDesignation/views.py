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

logger = logging.getLogger('apilog')

@csrf_exempt
def index(request):
    if request.method == 'POST':
        return post(request)
    else:
        return ""

@csrf_exempt    
def post(request):
    try:

        logger.debug("cdExecDesignation post")

        # ヘッダ情報
        post_headers = {
            'Content-Type': 'application/json',
        }

        # 引数をJSON形式で受け取りそのまま引数に設定
        post_data = request.body

        # 呼び出すapiInfoは環境変数より取得
        apiInfo = "{}://{}:{}/".format(os.environ["EPOCH_CICD_PROTOCOL"], os.environ["EPOCH_CICD_HOST"], os.environ["EPOCH_CICD_PORT"])
        logger.debug ("apiInfo:" + apiInfo)

        output = []
        # CD実行(ITA)
        request_response = requests.post( apiInfo + "ita/cdExec", headers=post_headers, data=post_data)
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
        return JsonResponse(response)

    except Exception as e:
        response = {
            "result":"500",
            "returncode": "0201",
            "args": e.args,
            "output": e.args,
            "traceback": traceback.format_exc(),
        }
        return JsonResponse(response)


