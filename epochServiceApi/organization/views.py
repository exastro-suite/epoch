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

@require_http_methods(['GET','POST'])
@csrf_exempt
def info_all(request):
    logger.debug("organization:{}".format(request.method))

    if request.method == 'POST':
        return info_all_post(request)
    elif request.method == 'GET':
        return info_all_get(request)
    else:
        return ""

@csrf_exempt    
def info_all_post(request):
    """organization 情報登録

    Args:
        request[json]: 登録する内容のjson形式
    Returns:
        [json]: 登録した organization の row情報のJson形式
    """

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
        apiInfo = "{}://{}:{}".format(os.environ['EPOCH_RS_ORGANIZATION_PROTOCOL'], os.environ['EPOCH_RS_ORGANIZATION_HOST'], os.environ['EPOCH_RS_ORGANIZATION_PORT'])

        logger.debug ("organization post call start")
        request_response = requests.post( "{}/organization".format(apiInfo), headers=post_headers, data=post_data )
        logger.debug ("organization post call end")
        # 戻り値の内容をJson形式で設定
        ret = json.loads(request_response.text)

        # 登録したオーガナイゼーションの情報Rowを返却
        if request_response.status_code == 200:
            output.append(ret["rows"])
        else:
            # エラーの際は処理しない
            raise Exception(ret["message"])

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
            "args": e.args,
            "output": e.args,
            "traceback": traceback.format_exc(),
        }
        return JsonResponse(response, status=500)

@csrf_exempt    
def info_all_get(request):
    """organization 一覧情報取得

    Args:
         request[json]: 特になし

    Returns:
        [json]: organization の rowsを配列としたJson形式
    """
    try:
        # ヘッダ情報
        post_headers = {
            'Content-Type': 'application/json',
        }

        # 引数をJSON形式で受け取りそのまま引数に設定
        post_data = request.body

        output = []
        # GET送信（organization一覧取得）
        apiInfo = "{}://{}:{}".format(os.environ['EPOCH_RS_ORGANIZATION_PROTOCOL'], os.environ['EPOCH_RS_ORGANIZATION_HOST'], os.environ['EPOCH_RS_ORGANIZATION_PORT'])

        logger.debug ("organization get call start")
        request_response = requests.get( "{}/organization".format(apiInfo), headers=post_headers )
        logger.debug ("organization get call end")
        # 戻り値の内容をJson形式で設定
        ret = json.loads(request_response.text)

        # 登録したオーガナイゼーションの情報Rowを返却
        if request_response.status_code == 200:
            output.append(ret["rows"])
        else:
            # エラーの際は処理しない
            raise Exception(ret["message"])

        response = {
            "result":"200",
            "output" : output,
        }
        
        return JsonResponse(response, status=200)

    except Exception as e:
        response = {
            "result":"500",
            "args": e.args,
            "output": e.args,
            "traceback": traceback.format_exc(),
        }
        return JsonResponse(response, status=500)
