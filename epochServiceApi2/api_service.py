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
import api_service_workspace
import api_service_ci
import api_service_manifest
import api_service_cd
import api_service_member
import api_service_current

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
            return api_service_workspace.create_workspace()
        else:
            # ワークスペース情報一覧取得へリダイレクト
            return api_service_workspace.get_workspace_list()

    except Exception as e:
        return common.server_error(e)


@app.route('/workspace/<int:workspace_id>', methods=['GET','PUT','PATCH'])
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
            return api_service_workspace.get_workspace(workspace_id)
        else:
            # ワークスペース情報更新
            return api_service_workspace.put_workspace(workspace_id)

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
            return api_service_workspace.post_pod(workspace_id)
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
            # get manifest template list (get)
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
            # parameter template delete (delete)
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

@app.route('/member', methods=['GET'])
def call_members():
    """member Call

    Returns:
        Response: HTTP Respose
    """
    try:
        globals.logger.debug('#' * 50)
        globals.logger.debug('CALL {}:from[{}]'.format(inspect.currentframe().f_code.co_name, request.method))
        globals.logger.debug('#' * 50)

        if request.method == 'GET':
            # all users get
            return api_service_member.get_users()
        else:
            # Error
            raise Exception("method not support!")

    except Exception as e:
        return common.server_error(e)

@app.route('/user/current', methods=['GET'])
def call_user_current():
    """current_user Call

    Returns:
        Response: HTTP Respose
    """
    try:
        globals.logger.debug('#' * 50)
        globals.logger.debug('CALL {}:from[{}]'.format(inspect.currentframe().f_code.co_name, request.method))
        globals.logger.debug('#' * 50)

        if request.method == 'GET':
            # all users get
            return api_service_current.current_user_get()
        else:
            # Error
            raise Exception("method not support!")

    except Exception as e:
        return common.server_error(e)

@app.route('/workspace/<int:workspace_id>/member', methods=['GET','POST'])
def call_workspace_member(workspace_id):
    """workspace member Call

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
            # all workspace members get
            return api_service_member.get_workspace_members(workspace_id)
        elif request.method == 'POST':
            # workspace members merge
            return api_service_member.merge_workspace_members(workspace_id)
        else:
            # Error
            raise Exception("method not support!")

    except Exception as e:
        return common.server_error(e)

@app.route('/workspace/<int:workspace_id>/leave', methods=['POST'])
def call_workspace_leave(workspace_id):
    """Exit from a member of the workspace - ワークスペースのメンバーから抜けます

    Args:
        workspace_id (int): workspace ID

    Returns:
        Response: HTTP Respose
    """
    try:
        globals.logger.debug('#' * 50)
        globals.logger.debug('CALL {}:from[{}] workspace_id[{}]'.format(inspect.currentframe().f_code.co_name, request.method, workspace_id))
        globals.logger.debug('#' * 50)


        return api_service_member.leave_workspace(workspace_id)

    except Exception as e:
        return common.server_error(e)


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('API_SERVICE_PORT', '8000')), threaded=True)
