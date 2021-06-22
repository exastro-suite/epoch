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

from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse
from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from django.views.decorators.csrf import csrf_exempt
from kubernetes import client, config

logger = logging.getLogger('apilog')

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

        logger.debug ("CALL argocd.pipelineParameter post")

        # 引数で指定されたCD環境を取得
        logger.debug (request.body)
        request_json = json.loads(request.body)
        #print (request_json)
        request_ci_env = request_json["ci_config"]["environments"]
        request_cd_env = request_json["cd_config"]["environments"]

        try:
            # argocdにloginする
            stdout_cd = subprocess.check_output(["argocd","login",settings.ARGO_SVC,"--insecure","--username",settings.ARGO_ID,"--password",settings.ARGO_PASSWORD],stderr=subprocess.STDOUT)
            logger.debug ("argocd login:" + str(stdout_cd))

        except subprocess.CalledProcessError as e:
            response = {
                "result": e.returncode,
                "returncode": "0401",
                "command": e.cmd,
                "output": e.output.decode('utf-8'),
                "traceback": traceback.format_exc(),
            }
            return JsonResponse(response)

        # 環境群数分処理を実行
        output = ""
        # keyList = request_deploy["enviroments"].keys()
        # for key in keyList:
        #     logger.debug ("KEY:" + key)
        #     env_name = key
        #     env_value = request_deploy["enviroments"][key]
        #     gitUrl = env_value["git"]["url"]
        #     cluster = env_value["cluster"]
        #     namespace = env_value["namespace"]
        for env in request_cd_env:
            env_name = env["name"]
            cluster = env["deploy_destination"]["cluster_url"]
            namespace = env["deploy_destination"]["namespace"]
            gitUrl = ""
            # manifest git urlは、ci_configより取得
            for ci_env in request_ci_env:
                if ci_env["environment_id"] = env["environment_id"]:
                    gitUrl = ci_env["git_url"]
                    break

            try:
                # argocd app create catalogue \
                # --repo [repogitory URL] \
                # --path ./ \
                # --dest-server https://kubernetes.default.svc \
                # --dest-namespace [namespace] \
                # --auto-prune \
                # --sync-policy automated
                # アプリケーション情報を追加
                stdout_cd = subprocess.check_output(["argocd","app","create",env_name,
                    "--repo",gitUrl,
                    "--path","./",
                    "--dest-server",cluster,
                    "--dest-namespace",namespace,
                    "--auto-prune",
                    "--sync-policy","automated",
                    ],stderr=subprocess.STDOUT)

                logger.debug ("argocd app create:" + str(stdout_cd))

                output += env_name + "{" + stdout_cd.decode('utf-8') + "},"

            except subprocess.CalledProcessError as e:
                response = {
                    "result": e.returncode,
                    "returncode": "0402",
                    "command": e.cmd,
                    "output": e.output.decode('utf-8'),
                    "traceback": traceback.format_exc(),
                }
                return JsonResponse(response)


        response = {
            "result":"201",
            "output" : [ output
                #stdout_ns.decode('utf-8'),
                #stdout_cd.decode('utf-8'),
            ],
        }
        return JsonResponse(response)

    except Exception as e:
        response = {
            "result":"500",
            "returncode": "0403",
            "args": e.args,
            "output": e.args,
            "traceback": traceback.format_exc(),
        }
        return JsonResponse(response)

# subprocess.check_outputの実行
# 戻り値
def execCommand(*args):
    try:
        # レポジトリの情報を追加
        stdout_cd = subprocess.check_output([args],stderr=subprocess.STDOUT)

    except subprocess.CalledProcessError as e:
        response = {
            "result": e.returncode,
            "returncode": "0404",
            "command": e.cmd,
            "output": e.output.decode('utf-8'),
            "traceback": traceback.format_exc(),
        }
        return JsonResponse(response)


@csrf_exempt    
def get(request):
    try:

        logger.debug ("CALL argocd.pipelineParameter get")

        # 引数で指定されたCD環境を取得
        logger.debug (request.body)
        request_json = json.loads(request.body)
        #print (request_json)
        request_ci_env = request_json["ci_config"]["environments"]
        request_cd_env = request_json["cd_config"]["environments"]

        try:
            # argocdにloginする
            stdout_cd = subprocess.check_output(["argocd","login",settings.ARGO_SVC,"--insecure","--username",settings.ARGO_ID,"--password",settings.ARGO_PASSWORD],stderr=subprocess.STDOUT)

            logger.debug ("argocd login:" + str(stdout_cd))

        except subprocess.CalledProcessError as e:
            response = {
                "result": e.returncode,
                "returncode": "0405",
                "command": e.cmd,
                "output": e.output.decode('utf-8'),
                "traceback": traceback.format_exc(),
            }
            return JsonResponse(response)

        output = ""
        # 環境群数分処理を実行
        # keyList = request_deploy["enviroments"].keys()
        # for key in keyList:
        #     logger.debug ("KEY:" + key)
        #     env_name = key
        #     env_value = request_deploy["enviroments"][key]
        #     gitUrl = env_value["git"]["url"]
        #     cluster = env_value["cluster"]
        #     namespace = env_value["namespace"]
        for env in request_cd_env:
            env_name = env["name"]

            try:
                # レポジトリの情報を追加
                stdout_cd = subprocess.check_output(["argocd","app","get",env_name],stderr=subprocess.STDOUT)

                logger.debug ("argocd app get:" + str(stdout_cd))

                output += "{" + stdout_cd.decode('utf-8') + "},"

            except subprocess.CalledProcessError as e:
                response = {
                    "result": e.returncode,
                    "returncode": "0406",
                    "command": e.cmd,
                    "output": e.output.decode('utf-8'),
                    "traceback": traceback.format_exc(),
                }
                return JsonResponse(response)

        response = {
            "result":"200",
            "output" : [output
                #stdout_ns.decode('utf-8'),
                #stdout_cd.decode('utf-8'),
            ],
        }

        return JsonResponse(response)

    except Exception as e:
        response = {
            "result":"500",
            "returncode": "0407",
            "args": e.args,
            "output": e.args,
            "traceback": traceback.format_exc(),
        }
        return JsonResponse(response)

