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
    elif request.method == 'GET':
        return get(request)
    else:
        return ""

@csrf_exempt    
def post(request):
    try:
        # 引数で指定されたCD環境を取得
        print (request.body)
        request_json = json.loads(request.body)
        request_build = request_json["build"]
        gitRepos = request_build["git"]["repos"]
        webHooksUrl = request_build["git"]["WebHooksUrl"]
        token = request_build["git"]["token"]

        # GitHubへPOST送信
        # ヘッダ情報
        post_headers = {
            'Authorization': 'token ' + token,
            'Accept': 'application/vnd.github.v3+json',
        }

        # 引数をJSON形式で構築
        post_data = json.dumps({
            "config":{
                "url": webHooksUrl,
                "content_type":"json",
                "secret":"",
                "insecure_ssl":"0",
                "token":"token",
                "digest":"digest",
            }
        })

        # hooksのPOST送信
        request_response = requests.post( "https://api.github.com/repos/" + gitRepos + "/hooks", headers=post_headers, data=post_data)

        response = {
            "result":"201",
            "output": request_response.text,
        }
        return JsonResponse(response)

    except Exception as e:
        response = {
            "result": e.returncode,
            "returncode": "0801",
            "args": e.args,
            "output": e.args,
            "traceback": traceback.format_exc(),
        }
        return JsonResponse(response)

@csrf_exempt    
def get(request):
    try:
        # 引数で指定されたCD環境を取得
        print (request.body)
        request_json = json.loads(request.body)
        print (request_json)
        request_build = request_json["build"]
        gitRepos = request_build["git"]["repos"]
        webHooksUrl = request_build["git"]["WebHooksurl"]
        token = request_build["git"]["token"]

        # GitHubへGET送信
        # ヘッダ情報
        request_headers = {
            'Authorization': 'token ' + token,
            'Accept': 'application/vnd.github.v3+json',
        }

        print (gitRepos)
        # GETリクエスト送信
        request_response = requests.get( "https://api.github.com/repos/" + gitRepos + "/hooks", headers=request_headers)

        response = {
            "result":"200",
            "output" : request_response.text,
        }
        return JsonResponse(response)

    except Exception as e:
        response = {
            "result": e.returncode,
            "returncode": "0802",
            "args": e.args,
            "output": e.args,
            "traceback": traceback.format_exc(),
        }
        return JsonResponse(response)

