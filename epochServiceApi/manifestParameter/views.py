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

from django.shortcuts import render
from django.http import HttpResponse
from django.http.response import JsonResponse

from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def index(request):
    if request.method == 'POST':
        return post(request)
    else:
        return ""

@csrf_exempt    
def post(request):
    try:

        print ("pipelineParameter post")

        # ヘッダ情報
        post_headers = {
            'Content-Type': 'application/json',
        }

        # 引数をJSON形式で受け取りそのまま引数に設定
        post_data = request.body

        # 呼び出すapiInfoは、clusterInfo情報より取得
#        print (request.body)
        request_json = json.loads(request.body)
        apiInfo = request_json["clusterInfo"]["apiInfo"]
        print ("apiInfo:" + apiInfo)

        output = []
        # Manifestパラメータ設定(ITA)
        request_response = requests.post( apiInfo + "ita/manifestParameter", headers=post_headers, data=post_data)
        print("ita/manifestParameter:response:" + request_response.text)
        ret = json.loads(request_response.text)
        #ret = request_response.text
        print(ret["result"])
        if request_response.status_code == 200:
            output.append(ret["items"])
        else:
            raise Exception(request_response.text)

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

