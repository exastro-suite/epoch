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

from django.shortcuts import render
from django.http import HttpResponse
from django.http.response import JsonResponse

from django.views.decorators.csrf import csrf_exempt

logger = logging.getLogger('apilog')
app_name = ""
exec_stat = ""
exec_detail = ""

@csrf_exempt
def pipelinerun(request, workspace_id):
    """TEKTONパイプライン情報

    Args:
        request (json): リクエスト情報
        workspace_id (int): ワークスペースID

    Returns:
        json: 戻り値(result:リターンコード、rows:取得情報)
    """

    logger.debug("CALL pipelinerun [{}]: workspace_id:{}".format(request.method, workspace_id))

    if request.method == 'GET':
        return get_pipelinerun(request, workspace_id)
    else:
        return ""

@csrf_exempt    
def get_pipelinerun(request, workspace_id):
    """TEKTONパイプライン情報取得

    Args:
        request (json): リクエスト情報
        workspace_id (int): ワークスペースID

    Returns:
        json: 戻り値(result:リターンコード、rows:取得情報)
    """
    try:

        app_name = "TEKTONパイプライン情報取得:"
        exec_stat = "情報取得"
        exec_detail = ""

        latest = request.GET.get(key="latest", default="False")

        # パラメータ情報
        get_param = {
            'latest': latest,
        }

        # 呼び出すapiInfoは、環境変数より取得
        apiInfo = "{}://{}:{}/".format(os.environ["EPOCH_CONTROL_TEKTON_PROTOCOL"], os.environ["EPOCH_CONTROL_TEKTON_HOST"], os.environ["EPOCH_CONTROL_TEKTON_PORT"])

        # TEKTONパイプライン情報取得
        exec_stat = "pipelinerun情報取得"
        request_response = requests.get(apiInfo + "/workspace/{}/tekton/pipelinerun".format(workspace_id), params=get_param)

        ret = json.loads(request_response.text)

        if request_response.status_code != 200:
            if "errorDetail" in ret:
                exec_detail = ret["errorDetail"]
            else:
                exec_detail = ""
            raise Exception

        response = {
            "result":"200",
            "rows" : ret["rows"],
        }

        return JsonResponse(response, status=200)

    except Exception as e:
        response = {
            "result":"500",
            "returncode": "1001",
            "errorStatement": app_name + exec_stat,
            "errorDetail": exec_detail,
            "args": e.args,
            "output": e.args,
            "traceback": traceback.format_exc(),
        }
        return JsonResponse(response, status=500)


@csrf_exempt
def taskrun_logs(request, workspace_id, taskrun_name):
    """TEKTONタスク実行ログ情報

    Args:
        request (json): リクエスト情報
        workspace_id (int): ワークスペースID
        taskrun_name (string): タスク名

    Returns:
        json: 戻り値(result:リターンコード、rows:取得情報)
    """

    logger.debug("CALL taskrun_logs [{}]: workspace_id:{} taskrun_name:{}".format(request.method, workspace_id, taskrun_name))

    if request.method == 'GET':
        return get_taskrun_logs(request, workspace_id, taskrun_name)
    else:
        return ""

@csrf_exempt    
def get_taskrun_logs(request, workspace_id, taskrun_name):
    """TEKTONタスク実行ログ情報取得

    Args:
        request (json): リクエスト情報
        workspace_id (int): ワークスペースID
        taskrun_name (string): タスク名

    Returns:
        json: 戻り値(result:リターンコード、rows:取得情報)
    """
    try:

        app_name = "TEKTONタスク実行ログ:"
        exec_stat = "情報取得"
        exec_detail = ""

        latest = request.GET.get(key="latest", default="False")

        # パラメータ情報
        get_param = {
            'latest': latest,
        }

        # 呼び出すapiInfoは、環境変数より取得
        apiInfo = "{}://{}:{}/".format(os.environ["EPOCH_CONTROL_TEKTON_PROTOCOL"], os.environ["EPOCH_CONTROL_TEKTON_HOST"], os.environ["EPOCH_CONTROL_TEKTON_PORT"])

        # TEKTONタスク実行ログ情報取得
        exec_stat = "taskrunログ情報取得"
        request_response = requests.get(apiInfo + "/workspace/{}/tekton/taskrun/{}/logs".format(workspace_id, taskrun_name), params=get_param)

        if request_response.status_code != 200:
            if "errorDetail" in ret:
                exec_detail = ret["errorDetail"]
            else:
                exec_detail = ""
            raise Exception

        ret = json.loads(request_response.text)

        response = {
            "result":"200",
            "log" : ret["log"],
        }
        return JsonResponse(response, status=200)

    except Exception as e:
        response = {
            "result":"500",
            "returncode": "1002",
            "errorStatement": app_name + exec_stat,
            "errorDetail": exec_detail,
            "args": e.args,
            "output": e.args,
            "traceback": traceback.format_exc(),
        }
        return JsonResponse(response, status=500)


