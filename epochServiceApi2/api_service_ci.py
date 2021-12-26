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

from flask import Flask, request, abort, jsonify, render_template
from datetime import datetime
import inspect
import os
import json
import tempfile
import subprocess
import time
import re
from urllib.parse import urlparse
import base64
import requests
from requests.auth import HTTPBasicAuth
import traceback
from datetime import timedelta, timezone

import globals
import common
import multi_lang

# 設定ファイル読み込み・globals初期化
app = Flask(__name__)
app.config.from_envvar('CONFIG_API_SERVICE_PATH')
globals.init(app)

def post_ci_pipeline(workspace_id):
    """CIパイプライン情報設定

    Args:
        workspace_id (int): workspace ID

    Returns:
        Response: HTTP Respose
    """

    app_name = "ワークスペース情報:"
    exec_stat = "CIパイプライン情報設定"
    error_detail = ""

    try:
        globals.logger.debug('#' * 50)
        globals.logger.debug('CALL {}'.format(inspect.currentframe().f_code.co_name))
        globals.logger.debug('#' * 50)

        # ヘッダ情報
        post_headers = {
            'Content-Type': 'application/json',
        }

        # 引数をJSON形式で受け取りそのまま引数に設定
        post_data = request.json.copy()

        # epoch-control-inside-gitlab-api の呼び先設定
        api_url_gitlab = "{}://{}:{}/workspace/{}/gitlab".format(os.environ["EPOCH_CONTROL_INSIDE_GITLAB_PROTOCOL"], 
                                                                 os.environ["EPOCH_CONTROL_INSIDE_GITLAB_HOST"], 
                                                                 os.environ["EPOCH_CONTROL_INSIDE_GITLAB_PORT"],
                                                                 workspace_id)

        # epoch-control-github-api の呼び先設定
        api_url_github = "{}://{}:{}/workspace/{}/github/webhooks".format(os.environ["EPOCH_CONTROL_GITHUB_PROTOCOL"], 
                                                                          os.environ["EPOCH_CONTROL_GITHUB_HOST"], 
                                                                          os.environ["EPOCH_CONTROL_GITHUB_PORT"],
                                                                          workspace_id)

        # epoch-control-tekton-api の呼び先設定
        api_url_tekton = "{}://{}:{}/workspace/{}/tekton/pipeline".format(os.environ["EPOCH_CONTROL_TEKTON_PROTOCOL"], 
                                                                          os.environ["EPOCH_CONTROL_TEKTON_HOST"], 
                                                                          os.environ["EPOCH_CONTROL_TEKTON_PORT"],
                                                                          workspace_id)

        # パイプライン設定(GitLab Create Project)
        request_body = json.loads(request.data)
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
        # if request_body['cd_config']['environments_common']['git_repositry']['housing'] == 'inner':
        #     for pipeline_iac in request_body['cd_config']['environments']:
        #         ap_data = {
        #             'git_repositry': {
        #                 'user': request_body['cd_config']['environments_common']['git_repositry']['user'],
        #                 'token': request_body['cd_config']['environments_common']['git_repositry']['token'],
        #                 'url': pipeline_iac['git_repositry']['url'],
        #             }
        #         }
        #         git_projects.append(ap_data)


        for proj_data in git_projects:
            # gitlab/repos post送信
            response = requests.post('{}/repos'.format(api_url_gitlab), headers=post_headers, data=json.dumps(proj_data))
            globals.logger.debug("post gitlab/repos response:{}".format(response.text))

            if response.status_code != 200 and response.status_code != 201:
                error_detail = 'gitlab/repos post処理に失敗しました'
                raise common.UserException(error_detail)

        if request_body['ci_config']['pipelines_common']['git_repositry']['housing'] == 'outer':
            # github/webhooks post送信
            response = requests.post( api_url_github, headers=post_headers, data=json.dumps(post_data))
            globals.logger.debug("post github/webhooks response:{}".format(response.text))

            if response.status_code != 200:
                error_detail = 'github/webhooks post処理に失敗しました'
                raise common.UserException(error_detail)
        else:
            # パイプライン設定(GitLab webhooks)
            for pipeline_ap in request_body['ci_config']['pipelines']:
                ap_data = {
                    'git_repositry': {
                        'user': request_body['ci_config']['pipelines_common']['git_repositry']['user'],
                        'token': request_body['ci_config']['pipelines_common']['git_repositry']['token'],
                        'url': pipeline_ap['git_repositry']['url'],
                    },
                    'webhooks_url': pipeline_ap['webhooks_url'],
                }

                response = requests.post('{}/webhooks'.format(api_url_gitlab), headers=post_headers, data=json.dumps(ap_data))
                globals.logger.debug("post gitlab/webhooks response:{}".format(response.text))

                if response.status_code != 200:
                    error_detail = 'gitlab/webhooks post処理に失敗しました'
                    raise common.UserException(error_detail)

        # listener post送信
        response = requests.post(api_url_tekton, headers=post_headers, data=json.dumps(post_data))
        globals.logger.debug("post tekton/pipeline response:{}".format(response.text))

        if response.status_code != 200:
            error_detail = 'tekton/pipeline post処理に失敗しました'
            raise common.UserException(error_detail)

        ret_status = 200

        # 戻り値をそのまま返却        
        return jsonify({"result": ret_status}), ret_status

    except common.UserException as e:
        return common.server_error_to_message(e, app_name + exec_stat, error_detail)
    except Exception as e:
        return common.server_error_to_message(e, app_name + exec_stat, error_detail)


def get_ci_pipeline_result(workspace_id):
    """Get CI pipeline results (CIパイプライン結果取得)

    Args:
        workspace_id (int): WORKSPACE ID

    Returns:
        Response: HTTP Respose
    """
    app_name = "ワークスペース情報:"
    exec_stat = "CIパイプライン結果取得"
    error_detail = ""

    try:
        globals.logger.debug('#' * 50)
        globals.logger.debug('CALL {}'.format(inspect.currentframe().f_code.co_name))
        globals.logger.debug('#' * 50)

        # Get Query Parameter
        latest = request.args.get('latest', default='False')

        # ヘッダ情報
        post_headers = {
            'Content-Type': 'application/json',
        }

        # epoch-control-tekton-api の呼び先設定
        api_url_tekton = "{}://{}:{}/workspace/{}/tekton/pipelinerun".format(os.environ["EPOCH_CONTROL_TEKTON_PROTOCOL"], 
                                                                          os.environ["EPOCH_CONTROL_TEKTON_HOST"], 
                                                                          os.environ["EPOCH_CONTROL_TEKTON_PORT"],
                                                                          workspace_id)
        # TEKTONパイプライン情報取得
        exec_stat = "pipelinerun情報取得"
        request_response = requests.get(api_url_tekton, params={"latest": latest})

        ret = json.loads(request_response.text)

        if request_response.status_code != 200:
            if "errorDetail" in ret:
                exec_detail = ret["errorDetail"]
            else:
                exec_detail = ""
            raise common.UserException(error_detail)

        response = {
            "result":"200",
            "rows" : ret["rows"],
        }
        ret_status = 200

        # 戻り値をそのまま返却        
        return jsonify(response), ret_status

    except common.UserException as e:
        return common.server_error_to_message(e, app_name + exec_stat, error_detail)
    except Exception as e:
        return common.server_error_to_message(e, app_name + exec_stat, error_detail)


def get_ci_pipeline_result_logs(workspace_id, taskrun_name):

    app_name = "TEKTONタスク実行ログ:"
    exec_stat = "情報取得"
    error_detail = ""

    try:
        globals.logger.debug('#' * 50)
        globals.logger.debug('CALL {}'.format(inspect.currentframe().f_code.co_name))
        globals.logger.debug('#' * 50)

        # Get Query Parameter
        latest = request.args.get('latest', default='False')

        # ヘッダ情報
        post_headers = {
            'Content-Type': 'application/json',
        }

        # epoch-control-tekton-api の呼び先設定
        api_url_tekton = "{}://{}:{}/workspace/{}/tekton/taskrun/{}/logs".format(
                                                                        os.environ["EPOCH_CONTROL_TEKTON_PROTOCOL"], 
                                                                        os.environ["EPOCH_CONTROL_TEKTON_HOST"], 
                                                                        os.environ["EPOCH_CONTROL_TEKTON_PORT"],
                                                                        workspace_id,
                                                                        taskrun_name)
        # TEKTONタスク実行ログ情報取得
        exec_stat = "taskrunログ情報取得"
        request_response = requests.get(api_url_tekton, params={"latest": latest})

        ret = json.loads(request_response.text)

        if request_response.status_code != 200:
            if "errorDetail" in ret:
                error_detail = ret["errorDetail"]
            else:
                error_detail = ""
            raise common.UserException(error_detail)

        response = {
            "result":"200",
            "log" : ret["log"],
        }
        ret_status = 200

        # 戻り値をそのまま返却        
        return jsonify(response), ret_status

    except common.UserException as e:
        return common.server_error_to_message(e, app_name + exec_stat, error_detail)
    except Exception as e:
        return common.server_error_to_message(e, app_name + exec_stat, error_detail)
