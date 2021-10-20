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
app_name = ""
exec_stat = ""
exec_detail = ""

@require_http_methods(['POST'])
@csrf_exempt
def post(request):
    try:
        logger.debug("CALL workspace post")
        app_name = "ワークスペース作成:"
        exec_stat = "初期化"
        exec_detail = ""

        # ワークスペース複数化までは1固定
        workspace_id = 1

        # ヘッダ情報
        headers = {
            'Content-Type': 'application/json',
        }

        # データ情報
        data = '{}'

        output = []

        # CiCd Api の呼び先設定
        apiInfo = "{}://{}:{}/".format(os.environ["EPOCH_CICD_PROTOCOL"], os.environ["EPOCH_CICD_HOST"], os.environ["EPOCH_CICD_PORT"])

        # post送信（アクセス情報生成）
        exec_stat = "ワークスペースアクセス情報生成"
        response = requests.post(apiInfo + 'workspace/{}/initData'.format(workspace_id))
        # 正常時以外はExceptionを発行して終了する
        if response.status_code != 200:
            raise Exception("ワークスペースアクセス情報の生成に失敗しました。 {}".format(response.status_code))
        
        # パラメータ情報(JSON形式)
        payload = json.loads(request.body)

        # exastro platform authentication infra Api の呼び先設定
        apiInfo_epai = "{}://{}:{}/".format(os.environ["EPOCH_EPAI_API_PROTOCOL"], os.environ["EPOCH_EPAI_API_HOST"], os.environ["EPOCH_EPAI_API_PORT"])

        # ヘッダ情報
        headers = {
            'Content-Type': 'application/json',
        }

        # postする情報
        clients = [
            {
                "client_id" :   'epoch-ws-{}-ita'.format(workspace_id),
                "client_host" : os.environ["EPOCH_EPAI_HOST"],
                "client_protocol" : "https",
                "client_port" : "31183",
                "conf_template" : "epoch-ws-ita-template.conf",
                "backend_url" : "http://it-automation.epoch-workspace.svc:8084/",
            },
            {
                "client_id" :   'epoch-ws-{}-argocd'.format(workspace_id),
                "client_host" : os.environ["EPOCH_EPAI_HOST"],
                "client_protocol" : "https",
                "client_port" : "31184",
                "conf_template" : "epoch-ws-argocd-template.conf",
                "backend_url" : "https://argocd-server.epoch-workspace.svc/",
            },
            {
                "client_id" :   'epoch-ws-{}-sonarqube'.format(workspace_id),
                "client_host" : os.environ["EPOCH_EPAI_HOST"],
                "client_protocol" : "https",
                "client_port" : "31185",
                "conf_template" : "epoch-ws-sonarqube-template.conf",
                "backend_url" : "http://sonarqube.epoch-tekton-pipeline-1.svc:9000/",
            },
        ]

        # post送信（アクセス情報生成）
        exec_stat = "認証基盤 初期情報設定"
        for client in clients:
            response = requests.post("{}{}/{}/{}".format(apiInfo_epai, 'settings', os.environ["EPOCH_EPAI_REALM_NAME"], 'clients'), headers=headers, data=json.dumps(client))

            # 正常時以外はExceptionを発行して終了する
            if response.status_code != 200:
                raise Exception("認証基盤 初期情報設定の生成に失敗しました。 {}".format(response.status_code))

        exec_stat = "認証基盤 設定読み込み"
        response = requests.put("{}{}".format(apiInfo_epai, 'apply_settings'))

        # 正常時以外はExceptionを発行して終了する
        if response.status_code != 200:
            raise Exception("認証基盤 設定読み込みに失敗しました。 {}".format(response.status_code))

        # パラメータ情報(JSON形式)
        payload = json.loads(request.body)

        # post送信（argocd/pod作成）
        exec_stat = "ArgoCDデプロイ"
        response = requests.post(apiInfo + 'argocd/pod', headers=headers, data=data, params=payload)

        if isJsonFormat(response.text):
            # 取得したJSON結果が正常でない場合、例外を返す
            ret = json.loads(response.text)
            if ret["result"] == "OK":
                output.append(ret["output"])
            else:
                # 詳細エラーがある場合は詳細を設定
                if ret["errorDetail"] is not None:
                    exec_detail = ret["errorDetail"]
                raise Exception
        else:
            response = {
                "result": {
                    "code": "500",
                    "detailcode": "",
                    "errorStatement": app_name + exec_stat,
                    "errorDetail": exec_detail,
                    "output": response.text,
                    "datetime": datetime.datetime.now(pytz.timezone('Asia/Tokyo')).strftime('%Y/%m/%d %H:%M:%S'),
                }
            }
            return JsonResponse(response,status=500)

        # post送信（ita/pod作成）
        exec_stat = "Exastro IT Automationデプロイ"
        response = requests.post(apiInfo + 'ita/', headers=headers, data=data, params=payload)

        # 取得したJSON結果が正常でない場合、例外を返す
        ret = json.loads(response.text)
        if ret["result"] == "OK":
            output.append(ret["output"])
        else:
            # 詳細エラーがある場合は詳細を設定
            if ret["errorDetail"] is not None:
                exec_detail = ret["errorDetail"]
            raise Exception

        response = {
            "result": {
                "code": "200",
                "detailcode": "",
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
                "errorStatement": app_name + exec_stat,
                "errorDetail": exec_detail,
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

        app_name = "ワークスペース情報:"
        exec_stat = "初期化"
        exec_detail = ""

        # ヘッダ情報
        post_headers = {
            'Content-Type': 'application/json',
        }

        # 引数をJSON形式で受け取りそのまま引数に設定
        post_data = request.body

        # 呼び出すapiInfoは、環境変数より取得
        apiInfo = "{}://{}:{}/".format(os.environ["EPOCH_RS_WORKSPACE_PROTOCOL"], os.environ["EPOCH_RS_WORKSPACE_HOST"], os.environ["EPOCH_RS_WORKSPACE_PORT"])

        # ワークスペース情報保存
        exec_stat = "保存"
        request_response = requests.post( apiInfo + "workspace", headers=post_headers, data=post_data)
        logger.debug("workspace:" + request_response.text)
        ret = json.loads(request_response.text)
        #print(ret)
        if request_response.status_code == 500:
            # 詳細エラーがある場合は詳細を設定
            if ret["errorDetail"] is not None:
                exec_detail = ret["errorDetail"]
            raise Exception
            
        # 戻り値をそのまま返却        
        return JsonResponse(ret, status=request_response.status_code)

    except Exception as e:
        response = {
            "result": {
                "output": traceback.format_exc(),
                "errorStatement": app_name + exec_stat,
                "errorDetail": exec_detail,
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
        app_name = "ワークスペース情報:"
        exec_stat = "初期化"
        exec_detail = ""

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

        if request_response.status_code == 500:
            # 詳細エラーがある場合は詳細を設定
            if ret["errorDetail"] is not None:
                exec_detail = ret["errorDetail"]
            raise Exception

        # 戻り値をそのまま返却        
        return JsonResponse(ret, status=request_response.status_code)

    except Exception as e:
        response = {
            "result": {
                "code": "500",
                "detailcode": "",
                "output": traceback.format_exc(),
                "errorStatement": app_name + exec_stat,
                "errorDetail": exec_detail,
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
            if response.status_code == 500 and isJsonFormat(response.text):
                # 戻り値がJsonの場合は、値を取得
                ret = json.loads(response.text)
                # 詳細エラーがある場合は詳細を設定
                if ret["errorDetail"] is not None:
                    exec_detail = ret["errorDetail"]

            response = {
                "result": {
                    "detailcode": "",
                    "output": response.text,
                    "errorStatement": app_name + exec_stat,
                    "errorDetail": exec_detail,
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
                "errorStatement": app_name + exec_stat,
                "errorDetail": exec_detail,
                "datetime": datetime.datetime.now(pytz.timezone('Asia/Tokyo')).strftime('%Y/%m/%d %H:%M:%S'),
            }
        }
        return JsonResponse(response, status=500)
