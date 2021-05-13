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
from django.views.decorators.http import require_http_methods

@require_http_methods(['POST'])
@csrf_exempt    
def post(request):
    try:

        print ("pipeline post")
        # ヘッダ情報
        post_headers = {
            'Content-Type': 'application/json',
        }

        # 引数をJSON形式で受け取りそのまま引数に設定
        post_data = request.body

        # 呼び出すapiInfoは、clusterInfo情報より取得
        #print (request.body)
        request_json = json.loads(request.body)
        apiInfo = request_json["clusterInfo"]["apiInfo"]

        output = []
        # パイプライン設定(Github webhooks)
        request_response = requests.post( apiInfo + "github/webhooks", headers=post_headers, data=post_data)
        print("github/webhooks:" + request_response.text)
        ret = json.loads(request_response.text)
        print(ret["result"])
        if ret["result"] == "200" or ret["result"] == "201":
            output.append(ret["output"])
        else:
            return (request_response.text)

        # # 再有効化は、後日
        # # パイプライン設定(TEKTON)
        # request_response = requests.post( apiInfo + "tekton/pipeline", headers=post_headers, data=post_data)
        # print("tekton/pipeline:response:" + request_response.text)
        # ret = json.loads(request_response.text)
        # #ret = request_response.text
        # print(ret["result"])
        # if ret["result"] == "200" or ret["result"] == "201":
        #     output.append(ret["output"])
        # else:
        #     return (request_response.text)

        # パイプライン設定(ITA - 初期化設定)
        request_response = requests.post( apiInfo + "ita/initialize", headers=post_headers, data=post_data)
        print("ita/initialize:response:" + request_response.text)
        ret = json.loads(request_response.text)
        print(ret["result"])
        if ret["result"] == "200" or ret["result"] == "201":
            output.append(ret["items"])
        else:
            return (request_response.text)

        # パイプライン設定(ITA - Git環境情報設定)
        request_response = requests.post( apiInfo + "ita/manifestGitEnv", headers=post_headers, data=post_data)
        print("ita/manifestGitEnv:response:" + request_response.text)
        ret = json.loads(request_response.text)
        print(ret["result"])
        if ret["result"] == "200" or ret["result"] == "201":
            output.append(ret["items"])
        else:
            return (request_response.text)

        # パイプライン設定(ArgoCD)
        request_response = requests.post( apiInfo + "argocd/pipeline", headers=post_headers, data=post_data)
        print("argocd/pipeline:response:" + request_response.text)
        ret = json.loads(request_response.text)
        if ret["result"] == "200" or ret["result"] == "201":
            output.append(ret["output"])
        else:
            return (request_response.text)

        response = {
            "result":"200",
            "output" : output,
        }
        return JsonResponse(response, code=200)

    except Exception as e:
        response = {
            "result":"500",
            "returncode": "0101",
            "args": e.args,
            "output": e.args,
            "traceback": traceback.format_exc(),
        }
        return JsonResponse(response, code=500)


