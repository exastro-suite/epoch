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
import api_service_ci
import api_service_manifest
import api_service_cd

# 設定ファイル読み込み・globals初期化
app = Flask(__name__)
app.config.from_envvar('CONFIG_API_SERVICE_PATH')
globals.init(app)

@app.route('/alive', methods=["GET"])
def alive():
    """死活監視

    Returns:
        Response: HTTP Respose
    """
    return jsonify({"result": "200", "time": str(datetime.now(globals.TZ))}), 200


@app.route('/workspace', methods=['POST','GET'])
def call_workspace():
    """workspaceCall

    Returns:
        Response: HTTP Respose
    """
    try:
        globals.logger.debug('#' * 50)
        globals.logger.debug('CALL {}: method[{}]'.format(inspect.currentframe().f_code.co_name, request.method))
        globals.logger.debug('#' * 50)

        if request.method == 'POST':
            # ワークスペース情報作成へリダイレクト
            return create_workspace()
        else:
            # ワークスペース情報一覧取得へリダイレクト
            return get_workspace_list()

    except Exception as e:
        return common.server_error(e)


@app.route('/workspace/<int:workspace_id>', methods=['GET','PUT'])
def call_workspace_by_id(workspace_id):
    """workspace/workspace_id Call

    Args:
        workspace_id (int): workspace ID

    Returns:
        Response: HTTP Respose
    """
    try:
        globals.logger.debug('#' * 50)
        globals.logger.debug('CALL {}:from[{}] workspace_id[{}]'.format(inspect.currentframe().f_code.co_name, request.method, workspace_id))
        globals.logger.debug('#' * 50)

        if request.method == 'GET':
            # ワークスペース情報取得
            return get_workspace(workspace_id)
        else:
            # ワークスペース情報更新
            return put_workspace(workspace_id)

    except Exception as e:
        return common.server_error(e)


@app.route('/workspace/<int:workspace_id>/pod', methods=['POST'])
def call_pod(workspace_id):
    """workspace/workspace_id/pod Call

    Args:
        workspace_id (int): workspace ID

    Returns:
        Response: HTTP Respose
    """
    try:
        globals.logger.debug('#' * 50)
        globals.logger.debug('CALL {}:from[{}] workspace_id[{}]'.format(inspect.currentframe().f_code.co_name, request.method, workspace_id))
        globals.logger.debug('#' * 50)

        if request.method == 'POST':
            # workspace作成
            return post_pod(workspace_id)
        else:
            # Error
            raise Exception("method not support!")

    except Exception as e:
        return common.server_error(e)


@app.route('/workspace/<int:workspace_id>/ci/pipeline', methods=['POST'])
def call_ci_pipeline(workspace_id):
    """workspace/workspace_id/ci/pipeline Call

    Args:
        workspace_id (int): workspace ID

    Returns:
        Response: HTTP Respose
    """
    try:
        globals.logger.debug('#' * 50)
        globals.logger.debug('CALL {}:from[{}] workspace_id[{}]'.format(inspect.currentframe().f_code.co_name, request.method, workspace_id))
        globals.logger.debug('#' * 50)

        if request.method == 'POST':
            # CIパイプライン情報設定
            return api_service_ci.post_ci_pipeline(workspace_id)
        else:
            # Error
            raise Exception("method not support!")

    except Exception as e:
        return common.server_error(e)


@app.route('/workspace/<int:workspace_id>/ci/pipeline/result', methods=['GET'])
def call_ci_result(workspace_id):
    """workspace/workspace_id/ci/pipeline/result Call

    Args:
        workspace_id (int): workspace ID

    Returns:
        Response: HTTP Respose
    """
    try:
        globals.logger.debug('#' * 50)
        globals.logger.debug('CALL {}:from[{}] workspace_id[{}]'.format(inspect.currentframe().f_code.co_name, request.method, workspace_id))
        globals.logger.debug('#' * 50)

        if request.method == 'GET':
            # CIパイプライン結果取得
            return api_service_ci.get_ci_pipeline_result(workspace_id)
        else:
            # Error
            raise Exception("method not support!")

    except Exception as e:
        return common.server_error(e)

@app.route('/workspace/<int:workspace_id>/ci/pipeline/result/<taskrun_name>/logs', methods=['GET'])
def call_ci_result_logs(workspace_id, taskrun_name):
    """workspace/workspace_id/ci/pipeline/result/taskrun_name/logs Call

    Args:
        workspace_id (int): workspace ID
        taskrun_name (str): tekton taskrun_name
    Returns:
        Response: HTTP Respose
    """
    try:
        globals.logger.debug('#' * 50)
        globals.logger.debug('CALL {}:from[{}] workspace_id[{}] taskrun_name[{}]'.format(inspect.currentframe().f_code.co_name, request.method, workspace_id, taskrun_name))
        globals.logger.debug('#' * 50)

        if request.method == 'GET':
            # CIパイプライン結果取得
            return api_service_ci.get_ci_pipeline_result_logs(workspace_id, taskrun_name)
        else:
            # Error
            raise Exception("method not support!")

    except Exception as e:
        return common.server_error(e)


@app.route('/workspace/<int:workspace_id>/cd/pipeline', methods=['POST'])
def call_cd_pipeline(workspace_id):
    """workspace/workspace_id/cd/pipeline Call

    Args:
        workspace_id (int): workspace ID

    Returns:
        Response: HTTP Respose
    """
    try:
        globals.logger.debug('#' * 50)
        globals.logger.debug('CALL {}:from[{}] workspace_id[{}]'.format(inspect.currentframe().f_code.co_name, request.method, workspace_id))
        globals.logger.debug('#' * 50)

        if request.method == 'POST':
            # CDパイプライン情報設定
            return api_service_cd.post_cd_pipeline(workspace_id)
        else:
            # Error
            raise Exception("method not support!")

    except Exception as e:
        return common.server_error(e)


@app.route('/workspace/<int:workspace_id>/manifest/parameter', methods=['POST'])
def call_manifest_parameter(workspace_id):
    """workspace/workspace_id/manifest/parameter Call

    Args:
        workspace_id (int): workspace ID

    Returns:
        Response: HTTP Respose
    """
    try:
        globals.logger.debug('#' * 50)
        globals.logger.debug('CALL {}:from[{}] workspace_id[{}]'.format(inspect.currentframe().f_code.co_name, request.method, workspace_id))
        globals.logger.debug('#' * 50)

        if request.method == 'POST':
            # manifest parameter setting (post)
            return api_service_manifest.post_manifest_parameter(workspace_id)
        else:
            # Error
            raise Exception("method not support!")

    except Exception as e:
        return common.server_error(e)


@app.route('/workspace/<int:workspace_id>/manifest/template', methods=['POST','GET'])
def call_manifest_template(workspace_id):
    """workspace/workspace_id/manifest/template Call

    Args:
        workspace_id (int): workspace ID

    Returns:
        Response: HTTP Respose
    """
    try:
        globals.logger.debug('#' * 50)
        globals.logger.debug('CALL {}:from[{}] workspace_id[{}]'.format(inspect.currentframe().f_code.co_name, request.method, workspace_id))
        globals.logger.debug('#' * 50)

        if request.method == 'POST':
            # manifest template setting (post)
            return api_service_manifest.post_manifest_template(workspace_id)
        elif request.method == 'GET':
            # get manifest template list (put)
            return api_service_manifest.get_manifest_template_list(workspace_id)
        else:
            # Error
            raise Exception("method not support!")

    except Exception as e:
        return common.server_error(e)


@app.route('/workspace/<int:workspace_id>/manifest/template/<int:file_id>', methods=['DELETE'])
def call_manifest_template_id(workspace_id, file_id):
    """workspace/workspace_id/manifest/template/file_id Call

    Args:
        workspace_id (int): workspace ID
        file_id (int): file ID

    Returns:
        Response: HTTP Respose
    """
    try:
        globals.logger.debug('#' * 50)
        globals.logger.debug('CALL {}:from[{}] workspace_id[{}] file_id[{}]'.format(inspect.currentframe().f_code.co_name, request.method, workspace_id, file_id))
        globals.logger.debug('#' * 50)

        if request.method == 'DELETE':
            # manifest parameter setting (post)
            return api_service_manifest.delete_manifest_template(workspace_id, file_id)
        else:
            # Error
            raise Exception("method not support!")

    except Exception as e:
        return common.server_error(e)


@app.route('/workspace/<int:workspace_id>/cd/exec', methods=['POST'])
def call_cd_exec(workspace_id):
    """workspace/workspace_id/cd/exec Call

    Args:
        workspace_id (int): workspace ID

    Returns:
        Response: HTTP Respose
    """
    try:
        globals.logger.debug('#' * 50)
        globals.logger.debug('CALL {}:from[{}] workspace_id[{}]'.format(inspect.currentframe().f_code.co_name, request.method, workspace_id))
        globals.logger.debug('#' * 50)

        if request.method == 'POST':
            # cd execute (post)
            return api_service_cd.cd_execute(workspace_id)
        else:
            # Error
            raise Exception("method not support!")

    except Exception as e:
        return common.server_error(e)

def create_workspace():
    """ワークスペース作成

    Returns:
        Response: HTTP Respose
    """

    app_name = "ワークスペース情報:"
    exec_stat = "作成"
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

        # workspace put送信
        api_url = "{}://{}:{}/workspace".format(os.environ['EPOCH_RS_WORKSPACE_PROTOCOL'],
                                                os.environ['EPOCH_RS_WORKSPACE_HOST'],
                                                os.environ['EPOCH_RS_WORKSPACE_PORT'])

        response = requests.post(api_url, headers=post_headers, data=json.dumps(post_data))

        if response.status_code == 200:
            # 正常時は戻り値がレコードの値なのでそのまま返却する
            ret = json.loads(response.text)
            rows = ret['rows']
        else:
            if common.is_json_format(response.text):
                ret = json.loads(response.text)
                # 詳細エラーがある場合は詳細を設定
                if ret["errorDetail"] is not None:
                    error_detail = ret["errorDetail"]

            raise common.UserException("{} Error post workspace db status:{}".format(inspect.currentframe().f_code.co_name, response.status_code))

        ret_status = response.status_code

        # 戻り値をそのまま返却        
        return jsonify({"result": ret_status, "rows": rows}), ret_status

    except common.UserException as e:
        return common.server_error_to_message(e, app_name + exec_stat, error_detail)
    except Exception as e:
        return common.server_error_to_message(e, app_name + exec_stat, error_detail)


def get_workspace_list():
    """ワークスペース情報一覧取得

    Returns:
        Response: HTTP Respose
    """

    app_name = "ワークスペース情報:"
    exec_stat = "一覧取得"
    error_detail = ""

    try:
        globals.logger.debug('#' * 50)
        globals.logger.debug('CALL {}'.format(inspect.currentframe().f_code.co_name))
        globals.logger.debug('#' * 50)

        # ヘッダ情報
        post_headers = {
            'Content-Type': 'application/json',
        }

        # ワークスペース情報取得
        api_url = "{}://{}:{}/workspace".format(os.environ['EPOCH_RS_WORKSPACE_PROTOCOL'],
                                                os.environ['EPOCH_RS_WORKSPACE_HOST'],
                                                os.environ['EPOCH_RS_WORKSPACE_PORT'])
        response = requests.get(api_url + '', headers=post_headers)

        rows = []
        if response.status_code == 200 and common.is_json_format(response.text):
            # 取得した情報で必要な部分のみを編集して返却する
            ret = json.loads(response.text)
            for data_row in ret["rows"]:
                row = {
                    "workspace_id": data_row["workspace_id"],
                    "workspace_name": data_row["common"]["name"],
                    "workspace_remarks": data_row["common"]["note"],
                    "update_at": data_row["update_at"],
                }
                rows.append(row)

        elif not response.status_code == 404:
            # 404以外の場合は、エラー、404はレコードなしで返却（エラーにはならない）
            raise Exception('{} Error:{}'.format(inspect.currentframe().f_code.co_name, response.status_code))

        return jsonify({"result": "200", "rows": rows}), 200

    except common.UserException as e:
        return common.server_error_to_message(e, app_name + exec_stat, error_detail)
    except Exception as e:
        return common.server_error_to_message(e, app_name + exec_stat, error_detail)


def get_workspace(workspace_id):
    """ワークスペース情報取得

    Args:
        workspace_id (int): workspace ID

    Returns:
        Response: HTTP Respose
    """

    app_name = "ワークスペース情報:"
    exec_stat = "取得"
    error_detail = ""

    try:
        globals.logger.debug('#' * 50)
        globals.logger.debug('CALL {}'.format(inspect.currentframe().f_code.co_name))
        globals.logger.debug('#' * 50)

        # ヘッダ情報
        post_headers = {
            'Content-Type': 'application/json',
        }

        # workspace GET送信
        api_url = "{}://{}:{}/workspace/{}".format(os.environ['EPOCH_RS_WORKSPACE_PROTOCOL'],
                                                    os.environ['EPOCH_RS_WORKSPACE_HOST'],
                                                    os.environ['EPOCH_RS_WORKSPACE_PORT'],
                                                    workspace_id)
        response = requests.get(api_url, headers=post_headers)

        if response.status_code == 200 and common.is_json_format(response.text):
            # 取得したJSON結果が正常でない場合、例外を返す
            ret = json.loads(response.text)
            rows = ret["rows"]
            ret_status = response.status_code
        elif response.status_code == 404:
            # 情報が取得できない場合は、0件で返す
            rows = []
            ret_status = response.status_code
        else:
            if response.status_code == 500 and common.is_json_format(response.text):
                # 戻り値がJsonの場合は、値を取得
                ret = json.loads(response.text)
                # 詳細エラーがある場合は詳細を設定
                if ret["errorDetail"] is not None:
                    error_detail = ret["errorDetail"]

            raise common.UserException("{} Error get workspace db status:{}".format(inspect.currentframe().f_code.co_name, response.status_code))

        return jsonify({"result": ret_status, "rows": rows}), ret_status

    except common.UserException as e:
        return common.server_error_to_message(e, app_name + exec_stat, error_detail)
    except Exception as e:
        return common.server_error_to_message(e, app_name + exec_stat, error_detail)

def put_workspace(workspace_id):
    """ワークスペース情報更新

    Args:
        workspace_id (int): workspace ID

    Returns:
        Response: HTTP Respose
    """

    app_name = "ワークスペース情報:"
    exec_stat = "更新"
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

        # workspace put送信
        api_url = "{}://{}:{}/workspace/{}".format(os.environ['EPOCH_RS_WORKSPACE_PROTOCOL'],
                                                    os.environ['EPOCH_RS_WORKSPACE_HOST'],
                                                    os.environ['EPOCH_RS_WORKSPACE_PORT'],
                                                    workspace_id)
        response = requests.put(api_url, headers=post_headers, data=json.dumps(post_data))

        if response.status_code == 200:
            # 正常時は戻り値がレコードの値なのでそのまま返却する
            ret = json.loads(response.text)
            rows = ret['rows']
        else:
            if common.is_json_format(response.text):
                ret = json.loads(response.text)
                # 詳細エラーがある場合は詳細を設定
                if ret["errorDetail"] is not None:
                    error_detail = ret["errorDetail"]

            raise common.UserException("{} Error put workspace db status:{}".format(inspect.currentframe().f_code.co_name, response.status_code))

        ret_status = response.status_code

        # 戻り値をそのまま返却        
        return jsonify({"result": ret_status}), ret_status

    except common.UserException as e:
        return common.server_error_to_message(e, app_name + exec_stat, error_detail)
    except Exception as e:
        return common.server_error_to_message(e, app_name + exec_stat, error_detail)


def post_pod(workspace_id):
    """ワークスペース作成

    Args:
        workspace_id (int): workspace ID

    Returns:
        Response: HTTP Respose
    """

    app_name = "ワークスペース情報:"
    exec_stat = "作成"
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

        # workspace post送信
        api_url = "{}://{}:{}/workspace/{}".format(os.environ['EPOCH_CONTROL_WORKSPACE_PROTOCOL'],
                                                   os.environ['EPOCH_CONTROL_WORKSPACE_HOST'],
                                                   os.environ['EPOCH_CONTROL_WORKSPACE_PORT'],
                                                   workspace_id)
        response = requests.post(api_url, headers=post_headers, data=json.dumps(post_data))
        globals.logger.debug("post workspace response:{}".format(response.text))
        
        if response.status_code != 200:
            error_detail = 'workspace post処理に失敗しました'
            raise common.UserException(error_detail)

        # argocd post送信
        api_url = "{}://{}:{}/workspace/{}/argocd".format(os.environ['EPOCH_CONTROL_ARGOCD_PROTOCOL'],
                                                          os.environ['EPOCH_CONTROL_ARGOCD_HOST'],
                                                          os.environ['EPOCH_CONTROL_ARGOCD_PORT'],
                                                          workspace_id)
        response = requests.post(api_url, headers=post_headers, data=json.dumps(post_data))
        globals.logger.debug("post argocd response:{}".format(response.text))

        if response.status_code != 200:
            error_detail = 'argocd post処理に失敗しました'
            raise common.UserException(error_detail)

        # ita post送信
        api_url = "{}://{}:{}/workspace/{}/it-automation".format(os.environ['EPOCH_CONTROL_ITA_PROTOCOL'],
                                                                 os.environ['EPOCH_CONTROL_ITA_HOST'],
                                                                 os.environ['EPOCH_CONTROL_ITA_PORT'],
                                                                 workspace_id)
        response = requests.post(api_url, headers=post_headers, data=json.dumps(post_data))
        globals.logger.debug("post it-automation response:{}".format(response.text))

        if response.status_code != 200:
            error_detail = 'it-automation post処理に失敗しました'
            raise common.UserException(error_detail)

        # epoch-control-ita-api の呼び先設定
        api_url = "{}://{}:{}/workspace/{}/it-automation/settings".format(os.environ['EPOCH_CONTROL_ITA_PROTOCOL'],
                                                                            os.environ['EPOCH_CONTROL_ITA_HOST'],
                                                                            os.environ['EPOCH_CONTROL_ITA_PORT'],
                                                                            workspace_id)

        # it-automation/settings post送信
        response = requests.post(api_url, headers=post_headers, data=json.dumps(post_data))
        globals.logger.debug("post it-automation/settings response:{}".format(response.text))

        if response.status_code != 200:
            error_detail = 'it-automation/settings post処理に失敗しました'
            raise common.UserException(error_detail)

        ret_status = 200

        # 戻り値をそのまま返却        
        return jsonify({"result": ret_status}), ret_status

    except common.UserException as e:
        return common.server_error_to_message(e, app_name + exec_stat, error_detail)
    except Exception as e:
        return common.server_error_to_message(e, app_name + exec_stat, error_detail)


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('API_SERVICE_PORT', '8000')), threaded=True)