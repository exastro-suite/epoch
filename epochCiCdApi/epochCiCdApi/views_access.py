#   Copyright 2021 NEC Corporation
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
import random
import string

from django.shortcuts import render
from django.http import HttpResponse
from django.http.response import JsonResponse

from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

logger = logging.getLogger("apilog")

@csrf_exempt
def index(request, workspace_id):

    logger.debug ("CALL workspace.access : method:{}, workspace_id:{}".format(request.method, workspace_id))

    if request.method == "POST":
        return post(request, workspace_id)
    elif request.method == "GET":
        return get(request, workspace_id)
    else:
        return ""

@csrf_exempt    
def post(request, workspace_id):
    try:

        # ユーザー・パスワードの初期値設定
        info = {
            "ARGOCD_USER" : "admin",
            "ARGOCD_PASSWORD" : random_str(20),
            "ARGOCD_EPOCH_USER" : "epoch_user",
            "ARGOCD_EPOCH_PASSWORD" : random_str(20),
            "ITA_USER" : "administrator",
            "ITA_PASSWORD" : random_str(20),
            "ITA_EPOCH_USER" : "epoch_user",
            "ITA_EPOCH_PASSWORD" : random_str(20),
            "SONARQUBE_USER" : "admin",
            "SONARQUBE_PASSWORD" : random_str(20),
            "SONARQUBE_EPOCH_USER" : "epoch_user",
            "SONARQUBE_EPOCH_PASSWORD" : random_str(20),
        }

        # ヘッダ情報
        post_headers = {
            'Content-Type': 'application/json',
        }

        apiInfo = "{}://{}:{}".format(os.environ['EPOCH_RS_WORKSPACE_PROTOCOL'], os.environ['EPOCH_RS_WORKSPACE_HOST'], os.environ['EPOCH_RS_WORKSPACE_PORT'])
        logger.debug ("workspace_access {}/workspace/{}/access".format(apiInfo, workspace_id))

        # 引数をJSON形式で受け取りそのまま引数に設定
        post_data = json.dumps(info)

        # 内部のアクセスなのでProxyを退避して解除
        http_proxy = os.environ['HTTP_PROXY']
        https_proxy = os.environ['HTTPS_PROXY']
        os.environ['HTTP_PROXY'] = ""
        os.environ['HTTPS_PROXY'] = ""

        # アクセス情報取得
        # Select送信（workspace_access取得）
        logger.debug ("workspace_access get call: worksapce_id:{}".format(workspace_id))
        request_response = requests.get("{}/workspace/{}/access".format(apiInfo, workspace_id))
        # logger.debug (request_response)

        # 情報が存在する場合は、更新、存在しない場合は、登録
        if request_response.status_code == 200:
            # PUT送信（workspace_access更新）
            logger.debug ("workspace_access put call: worksapce_id:{}".format(workspace_id))
            request_response = requests.put("{}/workspace/{}/access".format(apiInfo, workspace_id), headers=post_headers, data=post_data)
            # エラーの際は処理しない
            if request_response.status_code != 200:
                raise Exception(request_response.text)

        elif request_response.status_code == 404:
            # POST送信（workspace_access登録）
            logger.debug ("workspace_access post call: worksapce_id:{}".format(workspace_id))
            request_response = requests.post("{}/workspace/{}/access".format(apiInfo, workspace_id), headers=post_headers, data=post_data)
            # エラーの際は処理しない
            if request_response.status_code != 200:
                raise Exception(request_response.text)

        else:
            raise Exception("workspace_access post error status:{}, responce:{}".format(request_response.status_code, request_response.text))

        # 退避したProxyを戻す
        os.environ['HTTP_PROXY'] = http_proxy
        os.environ['HTTPS_PROXY'] = https_proxy

        response = {
            "result":"200",
            "output": "post Complete!",
        }
        return JsonResponse(response, status=200)

    except Exception as e:
        logger.debug("Exception workspace.access")
        logger.debug("- traceback.format_exc")
        logger.debug(traceback.format_exc())

        response = {
            "result": "500",
            "output": traceback.format_exc(),
        }
        return JsonResponse(response, status=500)

@csrf_exempt    
def get(request, workspace_id):
    try:
        ret = get_access_info(workspace_id)
        logger.debug (ret["ARGOCD_USER"])

        response = {
            "result":"200",
            "output": "get Complete!",
        }
        return JsonResponse(response, status=200)

    except Exception:
        logger.debug("Exception workspace.access")
        logger.debug("- traceback.format_exc")
        logger.debug(traceback.format_exc())

        response = {
            "result": "500",
            "output": traceback.format_exc(),
        }
        return JsonResponse(response, status=500)

@csrf_exempt    
def get_access_info(workspace_id):
    """ワークスペースアクセス情報取得

    Args:
        workspace_id (int): ワークスペースID

    Returns:
        json: アクセス情報
    """
    try:
        # url設定
        api_info = "{}://{}:{}".format(os.environ['EPOCH_RS_WORKSPACE_PROTOCOL'], os.environ['EPOCH_RS_WORKSPACE_HOST'], os.environ['EPOCH_RS_WORKSPACE_PORT'])

        # 内部のアクセスなのでProxyを退避して解除
        http_proxy = os.environ['HTTP_PROXY']
        https_proxy = os.environ['HTTPS_PROXY']
        os.environ['HTTP_PROXY'] = ""
        os.environ['HTTPS_PROXY'] = ""

        # アクセス情報取得
        # Select送信（workspace_access取得）
        logger.debug ("workspace_access get call: worksapce_id:{}".format(workspace_id))
        request_response = requests.get( "{}/workspace/{}/access".format(api_info, workspace_id))
        # logger.debug (request_response)

        # 退避したProxyを戻す
        os.environ['HTTP_PROXY'] = http_proxy
        os.environ['HTTPS_PROXY'] = https_proxy

        # 情報が存在する場合は、更新、存在しない場合は、登録
        if request_response.status_code == 200:
            ret = json.loads(request_response.text)
        else:
            raise Exception("workspace_access get error status:{}, responce:{}".format(request_response.status_code, request_response.text))

        return ret

    except Exception as e:
        logger.debug ("get_access_info Exception:{}".format(e.args))
        raise # 再スロー

@csrf_exempt    
def random_str(n):
    """ランダム文字列の作成

    Args:
        n (int): ランダム文字列の長さ

    Returns:
        str: ランダムで生成された文字列
    """

    # string.ascii_letters
    # 後述の ascii_lowercase と ascii_uppercase を合わせたもの。この値はロケールに依存しません。
    # string.ascii_lowercase
    # 小文字 "abcdefghijklmnopqrstuvwxyz" 。この値はロケールに依存せず、固定です。
    # string.ascii_uppercase
    # 大文字 "ABCDEFGHIJKLMNOPQRSTUVWXYZ" 。この値はロケールに依存せず、固定です。
    # string.digits

    return "".join(random.choices(string.ascii_letters + string.digits, k=n))