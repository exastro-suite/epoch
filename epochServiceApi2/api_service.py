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
import logging
from logging.config import dictConfig as dictLogConf

import globals
import common
import api_service_workspace
import api_service_ci
import api_service_manifest
import api_service_cd
import api_service_member
import api_service_current
from exastro_logging import *


# 設定ファイル読み込み・globals初期化
app = Flask(__name__)
app.config.from_envvar('CONFIG_API_SERVICE_PATH')
globals.init(app)


org_factory = logging.getLogRecordFactory()
logging.setLogRecordFactory(ExastroLogRecordFactory(org_factory, request))
globals.logger = logging.getLogger('root')
dictLogConf(LOGGING)


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
        globals.logger.info('Create or Get workspace information. method={}'.format(request.method))

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
        globals.logger.info('Get or Update workspace information. method={}, workspace_id={}'.format(request.method, workspace_id))

        if request.method == 'GET':
            # ワークスペース情報取得 Workspace info. get
            return api_service_workspace.get_workspace(workspace_id)
        elif request.method == 'PUT':
            # ワークスペース情報更新 Workspace info. put
            return api_service_workspace.put_workspace(workspace_id)
        else:
            # ワークスペース情報一部更新 Workspace info. patch
            return api_service_workspace.patch_workspace(workspace_id)

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
        globals.logger.info('Create workspace pod. method={}, workspace_id={}'.format(request.method, workspace_id))

        if request.method == 'POST':
            # workspace作成
            return api_service_workspace.post_pod(workspace_id)
        else:
            # Error
            raise Exception('method not support! request_method={}, expect_method={}'.format(request.method, 'POST'))

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
        globals.logger.info('Set CI pipeline information. method={}, workspace_id={}'.format(request.method, workspace_id))

        if request.method == 'POST':
            # CIパイプライン情報設定
            return api_service_ci.post_ci_pipeline(workspace_id)
        else:
            # Error
            raise Exception('method not support! request_method={}, expect_method={}'.format(request.method, 'POST'))

    except Exception as e:
        return common.server_error(e)


@app.route('/workspace/<int:workspace_id>/ci/pipeline/git/commits', methods=['GET'])
def call_git_commits(workspace_id):
    """/workspace/workspace_id/ci/pipeline/git/commits Call

    Args:
        workspace_id (int): workspace ID

    Returns:
        Response: HTTP Respose
    """
    try:
        globals.logger.info('Get CI commit list in code repository. method={}, workspace_id={}'.format(request.method, workspace_id))

        if request.method == 'GET':
            return api_service_ci.get_git_commits(workspace_id)
        else:
            raise Exception('method not support! request_method={}, expect_method={}'.format(request.method, 'GET'))
    except Exception as e:
        return common.server_error(e)


@app.route('/workspace/<int:workspace_id>/ci/pipeline/git/hooks', methods=['GET'])
def call_git_hooks(workspace_id):
    """workspace/workspace_id/ci/pipeline/git/hooks Call

    Args:
        workspace_id (int): workspace ID

    Returns:
        Response: HTTP Respose
    """
    try:
        globals.logger.info('Get webhook execution history. method={}, workspace_id={}'.format(request.method, workspace_id))

        if request.method == 'GET':
            return api_service_ci.get_git_hooks(workspace_id)
        else:
            raise Exception('method not support! request_method={}, expect_method={}'.format(request.method, 'GET'))
    except Exception as e:
        return common.server_error(e)


@app.route('/workspace/<int:workspace_id>/ci/pipeline/registry', methods=['GET'])
def call_registry(workspace_id):
    """workspace/workspace_id/ci/pipeline/registry Call

    Args:
        workspace_id (int): workspace ID

    Returns:
        Response: HTTP Respose
    """
    try:
        globals.logger.info('Get container registry information. method={}, workspace_id={}'.format(request.method, workspace_id))

        if request.method == 'GET':
            # Get container registry information - コンテナレジストリ情報取得
            return api_service_ci.get_registry(workspace_id)
        else:
            raise Exception('method not support! request_method={}, expect_method={}'.format(request.method, 'GET'))
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
        globals.logger.info('Get CI pipeline result. method={}, workspace_id={}'.format(request.method, workspace_id))

        if request.method == 'GET':
            # CIパイプライン結果取得
            return api_service_ci.get_ci_pipeline_result(workspace_id)
        else:
            # Error
            raise Exception('method not support! request_method={}, expect_method={}'.format(request.method, 'GET'))

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
        # globals.logger.info('Get CI pipeline result. method={}, workspace_id={}, taskrun_name={}'.format(request.method, workspace_id, taskrun_name))

        if request.method == 'GET':
            # CIパイプライン結果取得
            return api_service_ci.get_ci_pipeline_result_logs(workspace_id, taskrun_name)
        else:
            # Error
            raise Exception('method not support! request_method={}, expect_method={}'.format(request.method, 'GET'))

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
        globals.logger.info('Set CD pipeline information. method={}, workspace_id={}'.format(request.method, workspace_id))

        if request.method == 'POST':
            # CDパイプライン情報設定
            return api_service_cd.post_cd_pipeline(workspace_id)
        else:
            # Error
            raise Exception('method not support! request_method={}, expect_method={}'.format(request.method, 'POST'))

    except Exception as e:
        return common.server_error(e)


@app.route('/workspace/<int:workspace_id>/cd/pipeline/argocd', methods=['GET'])
def call_cd_pipeline_argocd(workspace_id):
    """workspace/workspace_id/cd/pipeline/argocd Call

    Args:
        workspace_id (int): workspace ID

    Returns:
        Response: HTTP Respose
    """
    try:
        globals.logger.info('Get CD pipeline (ArgoCD) information. method={}, workspace_id={}'.format(request.method, workspace_id))

        if request.method == 'GET':
            # Get CD pipeline (ArgoCD) information - CDパイプライン(ArgoCD)情報取得
            return api_service_cd.get_cd_pipeline_argocd(workspace_id)
        else:
            # Error
            raise Exception('method not support! request_method={}, expect_method={}'.format(request.method, 'GET'))

    except Exception as e:
        return common.server_error(e)


@app.route('/workspace/<int:workspace_id>/cd/pipeline/it-automation', methods=['GET'])
def call_cd_pipeline_ita(workspace_id):
    """workspace/workspace_id/cd/pipeline/it-automation Call

    Args:
        workspace_id (int): workspace ID

    Returns:
        Response: HTTP Respose
    """
    try:
        globals.logger.info('Get CD pipeline (it-automation) information. method={}, workspace_id={}'.format(request.method, workspace_id))

        if request.method == 'GET':
            # Get CD pipeline (ArgoCD) information - CDパイプライン(ArgoCD)情報取得
            return api_service_cd.get_cd_pipeline_ita(workspace_id)
        else:
            # Error
            raise Exception('method not support! request_method={}, expect_method={}'.format(request.method, 'GET'))

    except Exception as e:
        return common.server_error(e)



@app.route('/workspace/<int:workspace_id>/cd/pipeline/git/commits', methods=['GET'])
def call_cd_pipeline_git_commits(workspace_id):
    """/workspace/workspace_id/cd/pipeline/git/commits Call

    Args:
        workspace_id (int): workspace ID

    Returns:
        Response: HTTP Respose
    """
    try:
        globals.logger.info("Get CD commit list in manifest repository. method={}, workspace_id={}".format(request.method, workspace_id))

        if request.method == 'GET':
            return api_service_cd.get_git_commits(workspace_id)
        else:
            raise Exception('method not support! request_method={}, expect_method={}'.format(request.method, 'GET'))
    except Exception as e:
        return common.server_error(e)



@app.route('/workspace/<int:workspace_id>/cd/pipeline/argocd/sync', methods=['POST'])
def call_cd_pipeline_argocd_sync(workspace_id):
    """workspace/workspace_id/cd/pipeline/argocd/sync Call

    Args:
        workspace_id (int): workspace ID

    Returns:
        Response: HTTP Respose
    """
    try:
        globals.logger.info('Synchronize CD pipeline (ArgoCD). method={}, workspace_id={}'.format(request.method, workspace_id))

        if request.method == 'POST':
            # Post CD pipeline (ArgoCD) sync - CDパイプライン(ArgoCD)同期
            return api_service_cd.post_cd_pipeline_argocd_sync(workspace_id)
        else:
            # Error
            raise Exception('method not support! request_method={}, expect_method={}'.format(request.method, 'POST'))

    except Exception as e:
        return common.server_error(e)


@app.route('/workspace/<int:workspace_id>/cd/pipeline/argocd/rollback', methods=['POST'])
def call_cd_pipeline_argocd_rollback(workspace_id):
    """workspace/workspace_id/cd/pipeline/argocd/rollback Call

    Args:
        workspace_id (int): workspace ID

    Returns:
        Response: HTTP Respose
    """
    try:
        globals.logger.info('Rollback CD pipeline (ArgoCD). method={}, workspace_id={}'.format(request.method, workspace_id))

        if request.method == 'POST':
            # Post CD pipeline (ArgoCD) Rollback - CDパイプライン(ArgoCD)Rollback
            return api_service_cd.post_cd_pipeline_argocd_rollback(workspace_id)
        else:
            # Error
            raise Exception('method not support! request_method={}, expect_method={}'.format(request.method, 'POST'))

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
        globals.logger.info('Set manifest parameter. method={}, workspace_id={}'.format(request.method, workspace_id))

        if request.method == 'POST':
            # manifest parameter setting (post)
            return api_service_manifest.post_manifest_parameter(workspace_id)
        else:
            # Error
            raise Exception('method not support! request_method={}, expect_method={}'.format(request.method, 'POST'))

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
        globals.logger.info('Get or Set manifest template. method={}, workspace_id={}'.format(request.method, workspace_id))

        if request.method == 'POST':
            # manifest template setting (post)
            return api_service_manifest.post_manifest_template(workspace_id)
        elif request.method == 'GET':
            # get manifest template list (get)
            return api_service_manifest.get_manifest_template_list(workspace_id)
        else:
            # Error
            raise Exception('method not support! request_methods={}, expect_methods=[{}, {}]'.format(request.method, 'POST', 'GET'))

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
        globals.logger.info('Delete manifest template. method={}, workspace_id={}, file_id={}'.format( request.method, workspace_id, file_id))


        if request.method == 'DELETE':
            # parameter template delete (delete)
            return api_service_manifest.delete_manifest_template(workspace_id, file_id)
        else:
            # Error
            raise Exception('method not support! request_method={}, expect_method={}'.format(request.method, 'DELETE'))

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
        globals.logger.info('Execute CD. method={}, workspace_id={}'.format(request.method, workspace_id))

        if request.method == 'POST':
            # cd execute (post)
            return api_service_cd.cd_execute(workspace_id)
        else:
            # Error
            raise Exception('method not support! request_method={}, expect_method={}'.format(request.method, 'POST'))

    except Exception as e:
        return common.server_error(e)



@app.route('/workspace/<int:workspace_id>/cd/exec/<string:trace_id>', methods=['DELETE'])
def call_cd_exec_trace_id(workspace_id, trace_id):
    """workspace/workspace_id/cd/exec Call

    Args:
        workspace_id (int): workspace ID
        trace_id (str): trace id

    Returns:
        Response: HTTP Respose
    """
    try:
        globals.logger.info('Delete CD execution reservation. method={}, workspace_id={}, trace_id={}'.format(request.method, workspace_id, trace_id))

        if request.method == 'DELETE':
            # cd execute (post)
            return api_service_cd.cd_execute_cancel(workspace_id, trace_id)
        else:
            # Error
            raise Exception('method not support! request_method={}, expect_method={}'.format(request.method, 'DELETE'))

    except Exception as e:
        return common.server_error(e)


@app.route('/workspace/<int:workspace_id>/cd/environment', methods=['GET'])
def call_cd_environment(workspace_id):
    """workspace/workspace_id/cd/environment Call

    Args:
        workspace_id (int): workspace ID

    Returns:
        Response: HTTP Respose
    """
    try:
        globals.logger.info('Get CD environment. method={}, workspace_id={}'.format(request.method, workspace_id))

        if request.method == 'GET':
            # cd execute (post)
            return api_service_cd.cd_environment_get(workspace_id)
        else:
            # Error
            raise Exception('method not support! request_method={}, expect_method={}'.format(request.method, 'GET'))

    except Exception as e:
        return common.server_error(e)

@app.route('/member', methods=['GET'])
def call_members():
    """member Call

    Returns:
        Response: HTTP Respose
    """
    try:
        globals.logger.info('Get member. method={}'.format(request.method))

        if request.method == 'GET':
            # all users get
            return api_service_member.get_users()
        else:
            # Error
            raise Exception('method not support! request_method={}, expect_method={}'.format(request.method, 'GET'))

    except Exception as e:
        return common.server_error(e)

@app.route('/user/current', methods=['GET'])
def call_user_current():
    """current_user Call

    Returns:
        Response: HTTP Respose
    """
    try:
        globals.logger.info('Get current user infomation. method={}'.format(request.method))

        if request.method == 'GET':
            # all users get
            return api_service_current.current_user_get()
        else:
            # Error
            raise Exception('method not support! request_method={}, expect_method={}'.format(request.method, 'GET'))

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
        globals.logger.info('Get or Set workspace member. method={}, workspace_id={}'.format(request.method, workspace_id))

        if request.method == 'GET':
            # all workspace members get
            return api_service_member.get_workspace_members(workspace_id)
        elif request.method == 'POST':
            # workspace members merge
            return api_service_member.merge_workspace_members(workspace_id)
        else:
            # Error
            raise Exception('method not support! request_method={}, expect_methods=[{}, {}]'.format(request.method, 'GET', 'POST'))

    except Exception as e:
        return common.server_error(e)

@app.route('/workspace/<int:workspace_id>/member/cdexec', methods=['GET'])
def call_workspace_member_cdexec(workspace_id):
    """workspace member cdexec Call

    Args:
        workspace_id (int): workspace ID

    Returns:
        Response: HTTP Respose
    """
    try:
        globals.logger.info('Get CD execution member. method={}, workspace_id={}'.format(request.method, workspace_id))

        if request.method == 'GET':
            # cdexec members get
            return api_service_member.get_workspace_members_cdexec(workspace_id)
        else:
            # Error
            raise Exception('method not support! request_method={}, expect_method={}'.format(request.method, 'GET'))

    except Exception as e:
        return common.server_error(e)

@app.route('/workspace/<int:workspace_id>/member/current', methods=['DELETE'])
def call_workspace_leave(workspace_id):
    """Exit from a member of the workspace - ワークスペースのメンバーから抜けます

    Args:
        workspace_id (int): workspace ID

    Returns:
        Response: HTTP Respose
    """
    try:
        globals.logger.info('Delete member from workspace. method={}, workspace_id={}'.format(request.method, workspace_id))


        return api_service_member.leave_workspace(workspace_id)

    except Exception as e:
        return common.server_error(e)


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('API_SERVICE_PORT', '8000')), threaded=True)
