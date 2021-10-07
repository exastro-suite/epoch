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
import time

from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse
from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from django.views.decorators.csrf import csrf_exempt
from kubernetes import client, config

logger = logging.getLogger('apilog')
app_name = ""
exec_stat = ""
exec_detail = ""

WAIT_APPLICATION_DELETE = 180 # アプリケーションが削除されるまでの最大待ち時間

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
        app_name = "パイプラインパラメータ設定(ArgoCD):"
        exec_stat = "初期化"
        exec_detail = ""

        # 引数で指定されたCD環境を取得
        # logger.debug (request.body)
        request_json = json.loads(request.body)
        #print (request_json)
        request_ci_env = request_json["ci_config"]["environments"]
        request_cd_env = request_json["cd_config"]["environments"]

        try:
            # argocdにloginする
            exec_stat = "ログイン"
            stdout_cd = subprocess.check_output(["argocd","login",settings.ARGO_SVC,"--insecure","--username",settings.ARGO_ID,"--password",settings.ARGO_PASSWORD],stderr=subprocess.STDOUT)
            logger.debug ("argocd login:" + str(stdout_cd))

        except subprocess.CalledProcessError as e:
            logger.debug("CalledProcessError:\n" + traceback.format_exc())
            response = {
                "result": e.returncode,
                "returncode": "0401",
                "errorStatement": app_name + exec_stat,
                "errorDetail": exec_detail,
                # "command": e.cmd,
                "output": e.output.decode('utf-8'),
                "traceback": traceback.format_exc(),
            }
            return JsonResponse(response)

        # 設定済みのアプリケーション情報をクリア
        try:
            # アプリケーション情報の一覧を取得する
            logger.debug("execute : argocd app list")
            exec_stat = "アプリケーション一覧取得"
            stdout_cd = subprocess.check_output(["argocd","app","list","-o","json"],stderr=subprocess.STDOUT)
            # logger.debug("result : argocd app list:" + str(stdout_cd))

            # アプリケーション情報を削除する
            app_list = json.loads(stdout_cd)
            for app in app_list:
                logger.debug('execute : argocd app delete:' + app['metadata']['name'])
                exec_stat = "アプリケーション削除"
                stdout_cd = subprocess.check_output(["argocd","app","delete",app['metadata']['name'],"-y"],stderr=subprocess.STDOUT)

            # アプリケーションが消えるまでWaitする
            logger.debug("wait : argocd app list clean")

            for i in range(WAIT_APPLICATION_DELETE):
                # アプリケーションの一覧を取得し、結果が0件になるまでWaitする
                exec_stat = "アプリケーション削除完了確認"
                stdout_cd = subprocess.check_output(["argocd","app","list","-o","json"],stderr=subprocess.STDOUT)
                app_list = json.loads(stdout_cd)
                if len(app_list) == 0:
                    break
                time.sleep(1) # 1秒ごとに確認

        except subprocess.CalledProcessError as e:
            logger.debug("CalledProcessError:\n" + traceback.format_exc())
            response = {
                "result": e.returncode,
                "returncode": "0405",
                "errorStatement": app_name + exec_stat,
                "errorDetail": exec_detail,
                # "command": e.cmd,
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
                if ci_env["environment_id"] == env["environment_id"]:
                    gitUrl = ci_env["git_url"]
                    break

            try:
                # namespaceの存在チェック
                exec_stat = "namespace存在確認"
                ret = getNamespace(namespace)
                if ret is None:
                    # namespaceの作成
                    exec_stat = "namespace作成"
                    ret = createNamespace(namespace)

                # namespaceの作成に失敗した場合
                if ret is None:
                    response = {
                        "result":"500",
                        "returncode": "0404",
                        "errorStatement": app_name + exec_stat,
                        "errorDetail": exec_detail,
                        "args": "",
                        "output": "",
                        "traceback": traceback.format_exc(),
                    }
                    return JsonResponse(response)

                # argocd app create catalogue \
                # --repo [repogitory URL] \
                # --path ./ \
                # --dest-server https://kubernetes.default.svc \
                # --dest-namespace [namespace] \
                # --auto-prune \
                # --sync-policy automated
                # アプリケーション情報を追加
                exec_stat = "アプリケーション作成"
                exec_detail = "ArgoCDの入力内容を確認してください"
                stdout_cd = subprocess.check_output(["argocd","app","create",env_name,
                    "--repo",gitUrl,
                    "--path","./",
                    "--dest-server",cluster,
                    "--dest-namespace",namespace,
                    "--auto-prune",
                    "--sync-policy","automated",
                    ],stderr=subprocess.STDOUT)

                exec_detail = ""

                logger.debug ("argocd app create:" + str(stdout_cd))

                output += env_name + "{" + stdout_cd.decode('utf-8') + "},"

            except subprocess.CalledProcessError as e:
                logger.debug("CalledProcessError:\n" + traceback.format_exc())
                response = {
                    "result": e.returncode,
                    "returncode": "0402",
                    "errorStatement": app_name + exec_stat,
                    "errorDetail": exec_detail,
                    # "command": e.cmd,
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
        logger.debug("Exception:\n" + traceback.format_exc())
        response = {
            "result":"500",
            "returncode": "0403",
            "errorStatement": app_name + exec_stat,
            "errorDetail": exec_detail,
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
            # "command": e.cmd,
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
        argo_host = settings.ARGO_SVC
        argo_id = settings.ARGO_ID
        argo_password = settings.ARGO_PASSWORD
        #argo_id, argo_password = get_workspace_initial_data()

        try:
            # argocdにloginする
            stdout_cd = subprocess.check_output(["argocd","login",argo_host,"--insecure","--username",argo_id,"--password",argo_password],stderr=subprocess.STDOUT)

            logger.debug ("argocd login:" + str(stdout_cd))

        except subprocess.CalledProcessError as e:
            response = {
                "result": e.returncode,
                "returncode": "0405",
                # "command": e.cmd,
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
                    # "command": e.cmd,
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

# namespaceの情報取得
# 戻り値：namespaceの情報、存在しない場合はNone
def getNamespace(name):
    try:

        config.load_incluster_config()
        # 使用するAPIの宣言
        v1 = client.CoreV1Api()
        
        # 引数の設定
        pretty = '' # str | If 'true', then the output is pretty printed. (optional)
        exact = True # bool | Should the export be exact.  Exact export maintains cluster-specific fields like 'Namespace'. Deprecated. Planned for removal in 1.18. (optional)
        export = True # bool | Should this value be exported.  Export strips fields that a user can not specify. Deprecated. Planned for removal in 1.18. (optional)

        # namespaceの情報取得
        ret = v1.read_namespace(name=name)
        logger.debug("ret: %s" % (ret))

        return ret 

    except Exception as e:
        logger.debug("Except: %s" % (e))
        return None 
      
# namespaceの作成
# 戻り値：作成時の情報、失敗時はNone
def createNamespace(name):
    try:

        config.load_incluster_config()
        # 使用するAPIの宣言
        v1 = client.CoreV1Api()
        
        # 引数の設定
        body = client.V1Namespace(metadata=client.V1ObjectMeta(name=name))
        # api_instance = kubernetes.client.CoreV1Api(api_client)
        # body = kubernetes.client.V1Namespace() # V1Namespace | 
        #pretty = '' # str | If 'true', then the output is pretty printed. (optional)
        #dry_run = '' # str | When present, indicates that modifications should not be persisted. An invalid or unrecognized dryRun directive will result in an error response and no further processing of the request. Valid values are: - All: all dry run stages will be processed (optional)
        #field_manager = '' # str | fieldManager is a name associated with the actor or entity that is making these changes. The value must be less than or 128 characters long, and only contain printable characters, as defined by https://golang.org/pkg/unicode/#IsPrint. (optional)

        # namespaceの作成
        #ret = v1.create_namespace(body=body, pretty=pretty, dry_run=dry_run, field_manager=field_manager)
        ret = v1.create_namespace(body=body)

        logger.debug("ret: %s" % (ret))

        return ret 

    except Exception as e:
        logger.debug("Except: %s" % (e))
        return None


# def get_workspace_initial_data():

#     argo_id = ""
#     argo_password = ""

#     return argo_id, argo_password
