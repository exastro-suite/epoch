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
import datetime, pytz
import time
import shutil
import logging

from django.shortcuts import render
from django.http import HttpResponse
from django.http.response import JsonResponse
from django.views.decorators.http import require_http_methods

from django.views.decorators.csrf import csrf_exempt

from kubernetes import client, config

logger = logging.getLogger('apilog')
AppNme = ""
execstat = ""

@require_http_methods(['POST'])
@csrf_exempt
def post(request):
    try:
        logger.debug("CALL workspace post")
        AppName = "ワークスペース作成 : "
        execstat = "初期化 error"

        # ヘッダ情報
        headers = {
            'Content-Type': 'application/json',
        }

        # データ情報
        data = '{}'

        # パラメータ情報(JSON形式)
        payload = json.loads(request.body)

        # CiCd Api の呼び先設定
        apiInfo = "{}://{}:{}/".format(os.environ["EPOCH_CICD_PROTOCOL"], os.environ["EPOCH_CICD_HOST"], os.environ["EPOCH_CICD_PORT"])
        output = []

        # post送信（argocd/pod作成）
        execstat = "ArgoCDデプロイ"
        response = requests.post(apiInfo + 'argocd/pod', headers=headers, data=data, params=payload)

        if isJsonFormat(response.text):
            # 取得したJSON結果が正常でない場合、例外を返す
            ret = json.loads(response.text)
            if ret["result"] == "OK":
                output.append(ret["output"])
            else:
                execstat = "ArgoCDデプロイ失敗\nError info : " + ret["errorStatement"]
                raise Exception
        else:
            response = {
                "result": {
                    "code": "500",
                    "detailcode": "",
                    "errorStatement": AppName + execstat,
                    "output": response.text,
                    "datetime": datetime.datetime.now(pytz.timezone('Asia/Tokyo')).strftime('%Y/%m/%d %H:%M:%S'),
                }
            }
            return JsonResponse(response,status=500)

        # post送信（ita/pod作成）
        execstat = "Exastro IT Automationデプロイ"
        response = requests.post(apiInfo + 'ita/', headers=headers, data=data, params=payload)

        # 取得したJSON結果が正常でない場合、例外を返す
        ret = json.loads(response.text)
        if ret["result"] == "OK":
            output.append(ret["output"])
        else:
            raise Exception

        response = {
            "result": {
                "code": "200",
                "detailcode": "",
                "errorStatement": AppName + execstat,
                "output": output,
                "datetime": datetime.datetime.now(pytz.timezone('Asia/Tokyo')).strftime('%Y/%m/%d %H:%M:%S'),
            }
        }
        return JsonResponse(response)

    except Exception as e:
        response = {
            "result": {
                "code": "500",
                "detailcode": "",
                "errorStatement": AppName + execstat,
                "output": traceback.format_exc(),
                "datetime": datetime.datetime.now(pytz.timezone('Asia/Tokyo')).strftime('%Y/%m/%d %H:%M:%S'),
            }
        }
        return JsonResponse(response,status=500)

def isJsonFormat(line):
    try:
        json.loads(line)
    except json.JSONDecodeError as e:
        logger.debug(sys.exc_info())
        logger.debug(e)
        return False
    # 以下の例外でも捕まえるので注意
    except ValueError as e:
        logger.debug(sys.exc_info())
        logger.debug(e)
        return False
    except Exception as e:
        logger.debug(sys.exc_info())
        logger.debug(e)
        return False
    return True

# @csrf_exempt
# def conv(template_yaml, dest_yaml):

#     # 実行yamlの保存
#     shutil.copy(template_yaml, dest_yaml)

#     # 実行yamlを読み込む
#     with open(dest_yaml, encoding="utf-8") as f:
#         data_lines = f.read()

#     epochImage = os.environ['EPOCH_CICD_IMAGE']
#     epochPort = os.environ['EPOCH_CICD_PORT']

#     # 文字列置換
#     data_lines = data_lines.replace("<__epoch_cicd_api_image__>", epochImage)
#     data_lines = data_lines.replace("<__epoch_cicd_api_port__>", epochPort)

#     # 同じファイル名で保存
#     with open(dest_yaml, mode="w", encoding="utf-8") as f:
#         f.write(data_lines)


@require_http_methods(['GET','POST'])
@csrf_exempt
def info_all(request):
    """ワークスペース情報

    Args:
       request ([json]): 画面項目

    Returns:
        dict : workspace情報
    """
    if request.method == 'POST':
        return info_all_post(request)
    else:
        return info_all_get(request)

@csrf_exempt
def info_all_post(request):
    """ワークスペース情報(POST)

    Args:
        request ([json]): 画面項目

    Returns:
        dict : workspace情報
    """
    try:
        logger.debug ("CALL " + __name__)
        # ヘッダ情報
        post_headers = {
            'Content-Type': 'application/json',
        }

        # 引数をJSON形式で受け取りそのまま引数に設定
        post_data = request.body

        # 呼び出すapiInfoは、環境変数より取得
        apiInfo = "{}://{}:{}/".format(os.environ["EPOCH_RS_WORKSPACE_PROTOCOL"], os.environ["EPOCH_RS_WORKSPACE_HOST"], os.environ["EPOCH_RS_WORKSPACE_PORT"])

        # ワークスペース情報保存
        request_response = requests.post( apiInfo + "workspace", headers=post_headers, data=post_data)
        logger.debug("workspace:" + request_response.text)
        ret = json.loads(request_response.text)
        #print(ret)
        # 戻り値をそのまま返却        
        return JsonResponse(ret, status=request_response.status_code)

    except Exception as e:
        response = {
            "result": {
                "output": traceback.format_exc(),
                "datetime": datetime.datetime.now(pytz.timezone('Asia/Tokyo')).strftime('%Y/%m/%d %H:%M:%S'),
            }
        }
        return JsonResponse(response, status=500)

def info_all_get(request):
    # sample
    response = {
        "result": {
            "code": "200",
            "detailcode": "",
            "output": "Hello World. (Sample)",
            "datetime": datetime.datetime.now(pytz.timezone('Asia/Tokyo')).strftime('%Y/%m/%d %H:%M:%S'),
        }
    }
    return JsonResponse(response)

@require_http_methods(['GET','PUT'])
@csrf_exempt
def info(request, workspace_id):
    """ワークスペース詳細取得(id指定)

    Args:
        request (HttpRequest): HTTP request
        workspace_id (int): ワークスペースID

    Returns:
        response: HTTP Respose
    """
    if request.method == 'PUT':
        return info_put(request, workspace_id)
    else:
        return info_get(request, workspace_id)

@csrf_exempt
def info_put(request, workspace_id):
    """ワークスペース詳細取得

    Args:
        request (HttpRequest): HTTP request
        workspace_id (int): ワークスペースID

    Returns:
        response: HTTP Respose
    """
    try:
        # ヘッダ情報
        headers = {
            'Content-Type': 'application/json',
        }

        # 引数をJSON形式で受け取りそのまま引数に設定
        post_data = request.body

        # PUT送信（更新）
        resourceProtocol = os.environ['EPOCH_RS_WORKSPACE_PROTOCOL']
        resourceHost = os.environ['EPOCH_RS_WORKSPACE_HOST']
        resourcePort = os.environ['EPOCH_RS_WORKSPACE_PORT']
        apiInfo = "{}://{}:{}/".format(resourceProtocol, resourceHost, resourcePort)
        request_response = requests.put(apiInfo + 'workspace/' + str(workspace_id), headers=headers, data=post_data)
        ret = json.loads(request_response.text)

        # 戻り値をそのまま返却        
        return JsonResponse(ret, status=request_response.status_code)

    except Exception as e:
        response = {
            "result": {
                "code": "500",
                "detailcode": "",
                "output": traceback.format_exc(),
                "datetime": datetime.datetime.now(pytz.timezone('Asia/Tokyo')).strftime('%Y/%m/%d %H:%M:%S'),
            }
        }
        return JsonResponse(response, status=500)

@csrf_exempt
def info_get(request, workspace_id):
    """ワークスペース詳細取得

    Args:
        request (HttpRequest): HTTP request
        workspace_id (int): ワークスペースID

    Returns:
        response: HTTP Respose
    """
    try:
        # ヘッダ情報
        headers = {
            'Content-Type': 'application/json',
        }

        # GET送信（作成）
        resourceProtocol = os.environ['EPOCH_RS_WORKSPACE_PROTOCOL']
        resourceHost = os.environ['EPOCH_RS_WORKSPACE_HOST']
        resourcePort = os.environ['EPOCH_RS_WORKSPACE_PORT']
        apiInfo = "{}://{}:{}/".format(resourceProtocol, resourceHost, resourcePort)
        response = requests.get(apiInfo + 'workspace/' + str(workspace_id), headers=headers)

        output = []
        if response.status_code == 200 and isJsonFormat(response.text):
            # 取得したJSON結果が正常でない場合、例外を返す
            ret = json.loads(response.text)
            output = ret["rows"]
        elif response.status_code == 404:
            response = {
                "result": {
                    "detailcode": "",
                    "output": response.text,
                    "datetime": datetime.datetime.now(pytz.timezone('Asia/Tokyo')).strftime('%Y/%m/%d %H:%M:%S'),
                }
            }
            return JsonResponse(response, status=404)
        else:
            response = {
                "result": {
                    "detailcode": "",
                    "output": response.text,
                    "datetime": datetime.datetime.now(pytz.timezone('Asia/Tokyo')).strftime('%Y/%m/%d %H:%M:%S'),
                }
            }
            return JsonResponse(response, status=500)

        response = {
            "result": {
                "detailcode": "",
                "output": output,
                "datetime": datetime.datetime.now(pytz.timezone('Asia/Tokyo')).strftime('%Y/%m/%d %H:%M:%S'),
            }
        }
        return JsonResponse(response, status=200)

    except Exception as e:
        response = {
            "result": {
                "code": "500",
                "detailcode": "",
                "output": traceback.format_exc(),
                "datetime": datetime.datetime.now(pytz.timezone('Asia/Tokyo')).strftime('%Y/%m/%d %H:%M:%S'),
            }
        }
        return JsonResponse(response)
