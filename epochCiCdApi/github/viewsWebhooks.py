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
import re

from django.shortcuts import render
from django.http import HttpResponse
from django.http.response import JsonResponse

from django.views.decorators.csrf import csrf_exempt

logger = logging.getLogger('apilog')

# github webhook base url
github_webhook_base_url = 'https://api.github.com/repos/'
github_webhook_base_hooks = '/hooks'


@csrf_exempt
def index(request):

    logger.debug ("CALL github.webhooks : {}".format(request.method))

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
        logger.debug (request.body)
        request_json = json.loads(request.body)
        request_ci_confg = request_json["ci_config"]

        output = ""
        # パイプライン数分繰り返し
        for pipeline in request_ci_confg["pipelines"]:
            gitRepos = re.sub('\\.git$','',re.sub('^https?://[^/][^/]*/','',pipeline["git_repositry"]["url"]))
            webHooksUrl = pipeline["webhooks_url"]
            token = request_ci_confg["pipelines_common"]["git_repositry"]["token"]

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
            logger.debug('- github.webhooks setting to git')
            logger.debug('- reequest URL:' + github_webhook_base_url + gitRepos + github_webhook_base_hooks)
            request_response = requests.post( github_webhook_base_url + gitRepos + github_webhook_base_hooks, headers=post_headers, data=post_data)

            logger.debug('- response headers')
            logger.debug(request_response.headers)
            logger.debug('- response body')
            logger.debug(request_response.text)

            output += "{" + request_response.text + "},"

        response = {
            "result":"201",
            "output": output,
        }
        return JsonResponse(response)

    except Exception as e:
        logger.debug('Exception github.webhooks')
        logger.debug('- traceback.format_exc')
        logger.debug(traceback.format_exc())

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
        logger.debug (request.body)
        request_json = json.loads(request.body)
        request_ci_confg = request_json["ci_config"]

        output = ""
        # パイプライン数分繰り返し
        for pipeline in request_ci_confg["pipelines"]:
            gitRepos = re.sub('\\.git$','',re.sub('^https?://[^/][^/]*/','',pipeline["git_repositry"]["url"]))
            webHooksUrl = pipeline["webhooks_url"]
            token = request_ci_confg["pipelines_common"]["git_repositry"]["token"]

            # GitHubへGET送信
            # ヘッダ情報
            request_headers = {
                'Authorization': 'token ' + token,
                'Accept': 'application/vnd.github.v3+json',
            }

            logger.debug (gitRepos)
            # GETリクエスト送信
            request_response = requests.get( github_webhook_base_url + gitRepos + github_webhook_base_hooks, headers=request_headers)

            output += "{" + request_response.text + "},"

        response = {
            "result":"200",
            "output" : output,
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

