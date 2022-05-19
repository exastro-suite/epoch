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
import api_kubernetes_call
import api_workspace_manifests

# 設定ファイル読み込み・globals初期化
app = Flask(__name__)
app.config.from_envvar('CONFIG_API_WORKSPACE_PATH')
globals.init(app)

@app.route('/alive', methods=["GET"])
def alive():
    """死活監視

    Returns:
        Response: HTTP Respose
    """
    return jsonify({"result": "200", "time": str(datetime.now(globals.TZ))}), 200

@app.route('/workspace/<int:workspace_id>', methods=['POST'])
def call_workspace(workspace_id):
    """workspace/workspace_id 呼び出し

    Args:
        workspace_id (int): ワークスペースID

    Returns:
        Response: HTTP Respose
    """
    try:
        globals.logger.info('Create workspace. method={}, workspace_id={}'.format(request.method, workspace_id))

        if request.method == 'POST':
            # workspace 生成
            return create_workspace(workspace_id)
        else:
            # エラー
            raise Exception("method not support! request_method={}, expect_method={}".format(request.method, 'POST'))

    except Exception as e:
        return common.server_error(e)


@app.route('/workspace/<int:workspace_id>/manifest/templates', methods=['POST'])
def call_manifest_templates(workspace_id):
    """manifest/templates 呼び出し

    Args:
        workspace_id (int): ワークスペースID

    Returns:
        Response: HTTP Respose
    """
    try:
        globals.logger.info('Set manifest template. method={}, workspace_id={}'.format(request.method, workspace_id))

        if request.method == 'POST':
            # manifest テンプレートの設定
            return api_workspace_manifests.settings_manifest_templates(workspace_id)
        else:
            # エラー
            raise Exception("method not support! request_method={}, expect_method={}".format(request.method, 'POST'))

    except Exception as e:
        return common.server_error(e)

def create_workspace(workspace_id):
    """workspace 作成

    Args:
        workspace_id (int): ワークスペースID

    Returns:
        Response: HTTP Respose
    """

    app_name = "ワークスペース情報:"
    exec_stat = "workspace作成"
    error_detail = ""

    try:
        globals.logger.info('Create workspace. workspace_id={}'.format(workspace_id))

        error_detail = "workspace初期化失敗"

        # ユーザー・パスワードの初期値設定
        info = {
            "ARGOCD_USER" : "admin",
            "ARGOCD_PASSWORD" : common.random_str(20),
            "ARGOCD_EPOCH_USER" : "epoch-user",
            "ARGOCD_EPOCH_PASSWORD" : common.random_str(20),
            "ITA_USER" : "administrator",
            "ITA_PASSWORD" : common.random_str(20),
            "ITA_EPOCH_USER" : "epoch-user",
            "ITA_EPOCH_PASSWORD" : common.random_str(20),
            "SONARQUBE_USER" : "admin",
            "SONARQUBE_PASSWORD" : common.random_str(20),
            "SONARQUBE_EPOCH_USER" : "epoch-user",
            "SONARQUBE_EPOCH_PASSWORD" : common.random_str(20),
        }

        # ヘッダ情報
        post_headers = {
            'Content-Type': 'application/json',
        }

        apiInfo = "{}://{}:{}".format(os.environ['EPOCH_RS_WORKSPACE_PROTOCOL'], os.environ['EPOCH_RS_WORKSPACE_HOST'], os.environ['EPOCH_RS_WORKSPACE_PORT'])
        globals.logger.debug("workspace_access {}/workspace/{}/access".format(apiInfo, workspace_id))

        # 引数をJSON形式で受け取りそのまま引数に設定
        post_data = json.dumps(info)

        # アクセス情報取得
        # Select送信（workspace_access取得）
        globals.logger.debug("workspace_access get call: worksapce_id:{}".format(workspace_id))
        globals.logger.info('Send a request. workspace_id={} URL={}/workspace/{}/access'.format(workspace_id, apiInfo ,workspace_id))
        request_response = requests.get("{}/workspace/{}/access".format(apiInfo, workspace_id))
        # globals.logger.debug(request_response)

        globals.logger.info("status_code={}".format(request_response.status_code))
        # 情報が存在する場合は、作成しない、存在しない場合は、登録
        if request_response.status_code == 200:
            globals.logger.debug("data found")
            # 存在する場合は、作成しない
            # # PUT送信（workspace_access更新）
            # globals.logger.debug("workspace_access put call: worksapce_id:{}".format(workspace_id))
            # request_response = requests.put("{}/workspace/{}/access".format(apiInfo, workspace_id), headers=post_headers, data=post_data)
            # # エラーの際は処理しない
            # if request_response.status_code != 200:
            #     raise Exception(request_response.text)

        elif request_response.status_code == 404:
            # POST送信（workspace_access登録）
            globals.logger.debug("workspace_access post call: worksapce_id:{}".format(workspace_id))
            globals.logger.info('Send a request. workspace_id={} URL={}/workspace/{}/access'.format(workspace_id, apiInfo, workspace_id))
            request_response = requests.post("{}/workspace/{}/access".format(apiInfo, workspace_id), headers=post_headers, data=post_data)
            globals.logger.info("status_code={}".format(request_response.status_code))
            # エラーの際は処理しない
            if request_response.status_code != 200:
                raise common.UserException(request_response.text)

        else:
            raise Exception("workspace_access post error status:{}, responce:{}".format(request_response.status_code, request_response.text))

        error_detail = "namespace生成失敗"
        # namespace名の設定
        name = common.get_namespace_name(workspace_id)

        # namespaceの存在チェック
        ret = api_kubernetes_call.get_namespace(name)
        if ret is None:
            # 存在しない場合は、namespace生成
            api_kubernetes_call.create_namespace(name)

        ret_status = 200

        globals.logger.info('SUCCESS: Create workspace. ret_status={}'.format(ret_status))

        # 戻り値をそのまま返却        
        return jsonify({"result": ret_status}), ret_status

    except common.UserException as e:
        return common.server_error_to_message(e, app_name + exec_stat, error_detail)
    except Exception as e:
        return common.server_error_to_message(e, app_name + exec_stat, error_detail)


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('API_WORKSPACE_PORT', '8000')), threaded=True)
