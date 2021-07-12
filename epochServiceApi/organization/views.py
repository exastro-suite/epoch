#    Copyright 2019 NEC Corporation
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
# import userException

from django.shortcuts import render
from django.http import HttpResponse
from django.http.response import JsonResponse

from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

logger = logging.getLogger('apilog')

@require_http_methods(['POST'])
@csrf_exempt
def index(request):
    logger.debug("organization:{}".format(request.method))

    if request.method == 'POST':
        return post(request)
    else:
        return ""

@csrf_exempt    
def post(request):
    try:
        # raise UserError("test")
        # ヘッダ情報
        post_headers = {
            'Content-Type': 'application/json',
        }

        # 引数をJSON形式で受け取りそのまま引数に設定
        post_data = request.body

        output = []
        # POST送信（organization登録）
        apiInfo = "{}://{}:{}".format(os.environ['EPOCH_RESOURCE_PROTOCOL'], os.environ['EPOCH_RESOURCE_HOST'], os.environ['EPOCH_RESOURCE_PORT'])

        logger.debug ("organization post call start")
        request_response = requests.post( "{}/organization".format(apiInfo), headers=post_headers, data=post_data )
        logger.debug ("organization post call end")
        # 戻り値の内容をJson形式で設定
        ret = json.loads(request_response.text)

        # 登録したオーガナイゼーションの情報Rowを返却
        if request_response.status_code == 200:
            output.append(ret["rows"])
        # else:
            # エラーの際は処理しない
            # raise UserError(ret["message"])

        response = {
            "result":"200",
            "output" : output,
        }
        
        return JsonResponse(response, status=200)

    # except UserError as e:
    #     logger.error (e)

    except Exception as e:
        response = {
            "result":"500",
            # "message": e.xxxx,
            "args": e.args,
            "output": e.args,
            "traceback": traceback.format_exc(),
        }
        return JsonResponse(response, status=500)


