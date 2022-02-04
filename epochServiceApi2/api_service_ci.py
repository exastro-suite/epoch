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
import const
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

        # # 引数をJSON形式で受け取りそのまま引数に設定
        # post_data = request.json.copy()
        # workspace get
        api_url = "{}://{}:{}/workspace/{}".format(os.environ['EPOCH_RS_WORKSPACE_PROTOCOL'],
                                                    os.environ['EPOCH_RS_WORKSPACE_HOST'],
                                                    os.environ['EPOCH_RS_WORKSPACE_PORT'],
                                                    workspace_id)
        response = requests.get(api_url)

        if response.status_code != 200:
            error_detail = multi_lang.get_test("EP020-0013", "ワークスペース情報の取得に失敗しました")
            globals.logger.debug(error_detail)
            raise common.UserException(error_detail)

        # 取得したワークスペース情報を退避 Save the acquired workspace information
        ret = json.loads(response.text)
        # 取得したworkspace情報をパラメータとして受け渡す Pass the acquired workspace information as a parameter
        post_data = ret["rows"][0]

        # ワークスペース状態の取得 Get workspace status
        api_url = "{}://{}:{}/workspace/{}/status".format(os.environ['EPOCH_RS_WORKSPACE_PROTOCOL'],
                                                    os.environ['EPOCH_RS_WORKSPACE_HOST'],
                                                    os.environ['EPOCH_RS_WORKSPACE_PORT'],
                                                    workspace_id)
        response = requests.get(api_url)

        if response.status_code != 200:
            error_detail = multi_lang.get_test("EP020-0026", "ワークスペース状態情報の取得に失敗しました")
            globals.logger.debug(error_detail)
            raise common.UserException(error_detail)

        # 取得したワークスペース状態を退避 Save the acquired workspace status
        get_workspace_status = json.loads(response.text)
        # 更新で使用する項目のみを展開する Expand only the items used in the update
        workspace_status = {
            const.STATUS_CI_SETTING : get_workspace_status[const.STATUS_CI_SETTING] 
        }

        # 前回の結果が正常終了しているかチェックする
        # Be sure to execute CI settings except OK
        if workspace_status[const.STATUS_CI_SETTING] == const.STATUS_OK:
            # 更新前ワークスペース情報取得 Get workspace before update
            api_url = "{}://{}:{}/workspace/{}/before".format(os.environ['EPOCH_RS_WORKSPACE_PROTOCOL'],
                                                        os.environ['EPOCH_RS_WORKSPACE_HOST'],
                                                        os.environ['EPOCH_RS_WORKSPACE_PORT'],
                                                        workspace_id)
            response = requests.get(api_url)

            if response.status_code == 200:
                # 取得したワークスペース情報を退避 Save the acquired workspace information
                ret = json.loads(response.text)
                # 取得したworkspace情報をパラメータとして受け渡す Pass the acquired workspace information as a parameter
                before_data = ret["rows"][0]
            elif response.status_code == 404:
                before_data = None
            elif response.status_code != 200:
                error_detail = multi_lang.get_test("EP020-0013", "ワークスペース情報の取得に失敗しました")
                globals.logger.debug(error_detail)
                raise common.UserException(error_detail)
        else:
            # OK以外は、必ずCI設定を実行
            # Be sure to execute CI settings except OK
            before_data = None

        ci_config_json_after = post_data["ci_config"].copy()
        if before_data is not None:
            ci_config_json_before = before_data["ci_config"].copy()
        # environmentsの情報は比較に必要ないのでJsonから削除
        # The environment information is not needed for comparison, so delete it from Json
        if "environments" in ci_config_json_after:
            ci_config_json_after.pop("environments")
        if before_data is not None:
            if "environments" in ci_config_json_before:
                ci_config_json_before.pop("environments")

        ci_config_str_after = json.dumps(ci_config_json_after)
        if before_data is not None:
            ci_config_str_before = json.dumps(ci_config_json_before)
        else:
            ci_config_str_before = None

        # 更新前、更新後が一致しない場合にCIパイプラインの設定を行なう
        # Set up the CI pipeline when the pre-update and post-update do not match
        if ci_config_str_after != ci_config_str_before:
            globals.logger.debug("changed ci_config parameter!")

            # 実行前はNGで更新 Update with NG before execution
            workspace_status[const.STATUS_CI_SETTING] = const.STATUS_NG
            # workspace 状態更新 workspace status update
            api_url = "{}://{}:{}/workspace/{}/status".format(os.environ['EPOCH_RS_WORKSPACE_PROTOCOL'],
                                                                os.environ['EPOCH_RS_WORKSPACE_HOST'],
                                                                os.environ['EPOCH_RS_WORKSPACE_PORT'],
                                                                workspace_id)

            response = requests.put(api_url, headers=post_headers, data=json.dumps(workspace_status))

            if response.status_code != 200:
                error_detail = multi_lang.get_test("EP020-0027", "ワークスペース状態情報の更新に失敗しました")
                globals.logger.debug(error_detail)
                raise common.UserException(error_detail)

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
            # request_body = json.loads(request.data)
            request_body = post_data
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

                    if response.status_code != 200 and response.status_code != 201:
                        error_detail = 'gitlab/webhooks post処理に失敗しました'
                        raise common.UserException(error_detail)

            # listener post送信
            response = requests.post(api_url_tekton, headers=post_headers, data=json.dumps(post_data))
            globals.logger.debug("post tekton/pipeline response:{}".format(response.text))

            if response.status_code != 200:
                error_detail = 'tekton/pipeline post処理に失敗しました'
                raise common.UserException(error_detail)

            # 実行後はOKで更新 Update with OK after execution
            workspace_status[const.STATUS_CI_SETTING] = const.STATUS_OK
            # workspace 状態更新 workspace status update
            api_url = "{}://{}:{}/workspace/{}/status".format(os.environ['EPOCH_RS_WORKSPACE_PROTOCOL'],
                                                                os.environ['EPOCH_RS_WORKSPACE_HOST'],
                                                                os.environ['EPOCH_RS_WORKSPACE_PORT'],
                                                                workspace_id)

            response = requests.put(api_url, headers=post_headers, data=json.dumps(workspace_status))

            if response.status_code != 200:
                error_detail = multi_lang.get_test("EP020-0027", "ワークスペース状態情報の更新に失敗しました")
                globals.logger.debug(error_detail)
                raise common.UserException(error_detail)

        ret_status = 200

        # 戻り値をそのまま返却        
        return jsonify({"result": ret_status}), ret_status

    except common.UserException as e:
        return common.server_error_to_message(e, app_name + exec_stat, error_detail)
    except Exception as e:
        return common.server_error_to_message(e, app_name + exec_stat, error_detail)

def get_git_commits(workspace_id):
    """Get git commit history - gitコミット履歴取得

    Args:
        workspace_id (int): workspace ID
    Returns:
        Response: HTTP Respose
    """
    app_name = "ワークスペース情報:"
    exec_stat = "CIパイプラインgit履歴取得"
    error_detail = ""

    try:
        globals.logger.debug('#' * 50)
        globals.logger.debug('CALL {}'.format(inspect.currentframe().f_code.co_name))
        globals.logger.debug('#' * 50)

        response = {
            "result":"200",
            "rows" : [
                {
                "branch": "master",
                "commit_id": "0000100000000000000000000000000000000001",
                "name": "dummyuser-1",
                "date": "2021-11-29T08:07:10Z",
                "message": "commit-message-1",
                "html_url": "https://localhost/",
                },
                {
                "branch": "master",
                "commit_id": "0000200000000000000000000000000000000002",
                "name": "dummyuser-2",
                "date": "2021-11-29T08:07:10Z",
                "message": "commit-message-2",
                "html_url": "https://localhost/",
                }
            ],
        }
        ret_status = 200

        return jsonify(response), ret_status

    except common.UserException as e:
        return common.server_error_to_message(e, app_name + exec_stat, error_detail)
    except Exception as e:
        return common.server_error_to_message(e, app_name + exec_stat, error_detail)

def get_git_hooks(workspace_id):
    """Get webhook history - webhook履歴取得

    Args:
        workspace_id (int): workspace ID
    Returns:
        Response: HTTP Respose
    """
    app_name = "ワークスペース情報:"
    exec_stat = "CIパイプラインwebhook履歴取得"
    error_detail = ""

    try:
        globals.logger.debug('#' * 50)
        globals.logger.debug('CALL {}'.format(inspect.currentframe().f_code.co_name))
        globals.logger.debug('#' * 50)

        response = {
            "result":"200",
            "rows" : [
                {
                "branch": "master",
                "url": "https://localhost/api/listener/1",
                "date": "2021-11-30T02:09:25Z",
                "status": "OK",
                "status_code": 202,
                "event": "push",
                },
                {
                "branch": "master",
                "url": "https://localhost/api/listener/2",
                "date": "2021-11-30T02:09:25Z",
                "status": "failed to connect to host",
                "status_code": 502,
                "event": "push",
                }
            ],
        }
        ret_status = 200

        return jsonify(response), ret_status

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
