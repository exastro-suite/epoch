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

from django.shortcuts import render
from django.http import HttpResponse
from django.http.response import JsonResponse

from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

logger = logging.getLogger('apilog')
app_name = ""
exec_stat = ""
exec_detail = ""

@require_http_methods(['POST'])
@csrf_exempt    
def post(request):
    try:
        logger.debug("CALL pipeline post")
        app_name = "パイプライン作成:"
        exec_stat = "初期化"
        exec_detail = ""

        # ヘッダ情報
        post_headers = {
            'Content-Type': 'application/json',
        }

        # 引数をJSON形式で受け取りそのまま引数に設定
        post_data = request.body


        # 呼び出すapiInfoは、環境変数より取得
        apiInfo_cicd = "{}://{}:{}/".format(os.environ["EPOCH_CICD_PROTOCOL"], os.environ["EPOCH_CICD_HOST"], os.environ["EPOCH_CICD_PORT"])
        apiInfo_tekton = "{}://{}:{}/".format(os.environ["EPOCH_CONTROL_TEKTON_PROTOCOL"], os.environ["EPOCH_CONTROL_TEKTON_HOST"], os.environ["EPOCH_CONTROL_TEKTON_PORT"])
        apiInfo_gitlab = "{}://{}:{}/".format(os.environ["EPOCH_CONTROL_INSIDE_GITLAB_PROTOCOL"], os.environ["EPOCH_CONTROL_INSIDE_GITLAB_HOST"], os.environ["EPOCH_CONTROL_INSIDE_GITLAB_PORT"])

        output = []

        exec_stat = "パイプライン設定(GitLab Create Project)"
        # パイプライン設定(GitLab Create Project)
        request_body = json.loads(request.body)
        git_projects = []
        # アプリケーションコード
        if request_body['ci_config']['pipelines_common']['git_repositry']['housing'] == 'inner':
            for pipeline_ap in request_body['ci_config']['pipelines']:
                ap_data = {
                    'git_repositry': {
                        'user': request_body['ci_config']['pipelines_common']['git_repositry']['user'],
                        'token': request_body['ci_config']['pipelines_common']['git_repositry']['token'],
                        'url': pipeline_ap['git_repositry']['url'],
                    }
                }
                git_projects.append(ap_data)
        # IaC
        for pipeline_iac in request_body['ci_config']['environments']:
            if pipeline_iac['git_housing'] == 'inner':
                iac_data = {
                    'git_repositry': {
                        'user': pipeline_iac['git_user'],
                        'token': pipeline_iac['git_token'],
                        'url': pipeline_iac['git_url'],
                    }
                }
                git_projects.append(iac_data)
        # create project
        for proj_data in git_projects:
            request_response = requests.post( apiInfo_gitlab + "workspace/1/gitlab/repos", headers=post_headers, data=json.dumps(proj_data))
            logger.debug("workspace/1/gitlab/repos:" + request_response.text)
            ret = json.loads(request_response.text)
            logger.debug(ret["result"])
            if ret["result"] == "200" or ret["result"] == "201":
                output.append(ret["output"])
            else:
                if "errorDetail" in ret:
                    exec_detail = ret["errorDetail"]
                else:
                    exec_detail = ""
                raise Exception

        if request_body['ci_config']['pipelines_common']['git_repositry']['housing'] == 'inner':
            exec_stat = "パイプライン設定(GitHub webhooks)"
            # パイプライン設定(Github webhooks)
            request_response = requests.post( apiInfo_cicd + "github/webhooks", headers=post_headers, data=post_data)
            logger.debug("github/webhooks:" + request_response.text)
            ret = json.loads(request_response.text)
            logger.debug(ret["result"])
            if ret["result"] == "200" or ret["result"] == "201":
                output.append(ret["output"])
            else:
                if "errorDetail" in ret:
                    exec_detail = ret["errorDetail"]
                else:
                    exec_detail = ""
                raise Exception
        else:
            exec_stat = "パイプライン設定(GitLab webhooks)"
            # パイプライン設定(GitLab webhooks)
            for pipeline_ap in request_body['ci_config']['pipelines']:
                ap_data = {
                    'git_repositry': {
                        'user': request_body['ci_config']['pipelines_common']['git_repositry']['user'],
                        'token': request_body['ci_config']['pipelines_common']['git_repositry']['token'],
                        'url': pipeline_ap['git_repositry']['url'],
                    }
                }
                request_response = requests.post( apiInfo_gitlab + "workspace/1/gitlab/webhooks", headers=post_headers, data=ap_data)
                logger.debug("workspace/1/gitlab/webhooks:" + request_response.text)
                ret = json.loads(request_response.text)
                logger.debug(ret["result"])
                if ret["result"] == "200" or ret["result"] == "201":
                    output.append(ret["output"])
                else:
                    if "errorDetail" in ret:
                        exec_detail = ret["errorDetail"]
                    else:
                        exec_detail = ""
                    raise Exception

        exec_stat = "パイプライン設定(TEKTON)"
        # パイプライン設定(TEKTON)
        request_response = requests.post( apiInfo_tekton + "workspace/1/tekton/pipeline", headers=post_headers, data=post_data)
        logger.debug("tekton/pipeline:response:" + request_response.text)
        ret = json.loads(request_response.text)
        #ret = request_response.text
        logger.debug(ret["result"])
        if ret["result"] == "200" or ret["result"] == "201":
            output.append(ret)
        else:
            if "errorDetail" in ret:
                exec_detail = ret["errorDetail"]
            else:
                exec_detail = ""
            raise Exception

        exec_stat = "パイプライン設定(ITA - 初期化設定)"
        # パイプライン設定(ITA - 初期化設定)
        request_response = requests.post( apiInfo_cicd + "ita/initialize", headers=post_headers, data=post_data)
        logger.debug("ita/initialize:response:" + request_response.text)
        ret = json.loads(request_response.text)
        logger.debug(ret["result"])
        if ret["result"] == "200" or ret["result"] == "201":
            output.append(ret["output"])
        else:
            if "errorDetail" in ret:
                exec_detail = ret["errorDetail"]
            else:
                exec_detail = ""
            raise Exception

        exec_stat = "パイプライン設定(ITA - Git環境情報設定)"
        # パイプライン設定(ITA - Git環境情報設定)
        request_response = requests.post( apiInfo_cicd + "ita/manifestGitEnv", headers=post_headers, data=post_data)
        logger.debug("ita/manifestGitEnv:response:" + request_response.text)
        ret = json.loads(request_response.text)
        logger.debug(ret["result"])
        if ret["result"] == "200" or ret["result"] == "201":
            output.append(ret["items"])
        else:
            if "errorDetail" in ret:
                exec_detail = ret["errorDetail"]
            else:
                exec_detail = ""
            raise Exception

        exec_stat = "パイプライン設定(ArgoCD)"
        # パイプライン設定(ArgoCD)
        request_response = requests.post( apiInfo_cicd + "argocd/pipeline", headers=post_headers, data=post_data)
        logger.debug("argocd/pipeline:response:" + request_response.text)
        ret = json.loads(request_response.text)
        if ret["result"] == "200" or ret["result"] == "201":
            output.append(ret["output"])
        else:
            if "errorDetail" in ret:
                exec_detail = ret["errorDetail"]
            else:
                exec_detail = ""
            raise Exception

        response = {
            "result":"200",
            "output" : output,
        }
        return JsonResponse(response, status=200)

    except Exception as e:
        response = {
            "result":"500",
            "returncode": "0101",
            "errorStatement": app_name + exec_stat,
            "errorDetail": exec_detail,
            "args": e.args,
            "output": e.args,
            "traceback": traceback.format_exc(),
        }
        return JsonResponse(response, status=500)


