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
    """workspace呼び出し

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
        return common.serverError(e)


@app.route('/workspace/<int:workspace_id>', methods=['GET','PUT'])
def call_workspace_by_id(workspace_id):
    """workspace/workspace_id 呼び出し

    Args:
        workspace_id (int): ワークスペースID

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
        return common.serverError(e)

def create_workspace():
    """ワークスペース作成

    Returns:
        Response: HTTP Respose
    """
    try:
        globals.logger.debug('#' * 50)
        globals.logger.debug('CALL create_workspace')
        globals.logger.debug('#' * 50)

        return jsonify({"result": "200"}), 200

    except Exception as e:
        return common.serverError(e)


def get_workspace_list():
    """ワークスペース情報一覧取得

    Returns:
        Response: HTTP Respose
    """
    try:
        globals.logger.debug('#' * 50)
        globals.logger.debug('CALL {}'.format(inspect.currentframe().f_code.co_name))
        globals.logger.debug('#' * 50)

        ret = {
            "result": "200",
            "rows": [
                {
                    "id": 1,
                    "name": "EPOCHワークスペース１",
                    "remarks": "EPOCHワークスペース１の備考",
                    "update_at": datetime.now(globals.TZ),
                },
                {
                    "id": 2,
                    "name": "EPOCHワークスペース２",
                    "remarks": "EPOCHワークスペース２の備考",
                    "update_at": datetime.now(globals.TZ),
                },
                {
                    "id": 3,
                    "name": "EPOCHワークスペース３",
                    "remarks": "EPOCHワークスペース３の備考",
                    "update_at": datetime.now(globals.TZ),
                },
            ]
        }

        return jsonify(ret), 200

    except Exception as e:
        return common.serverError(e)


def get_workspace(workspace_id):
    """ワークスペース情報取得

    Args:
        workspace_id (int): ワークスペースID

    Returns:
        Response: HTTP Respose
    """
    try:
        globals.logger.debug('#' * 50)
        globals.logger.debug('CALL {}'.format(inspect.currentframe().f_code.co_name))
        globals.logger.debug('#' * 50)

        return jsonify({"result": "200"}), 200

    except Exception as e:
        return common.serverError(e)


def put_workspace(workspace_id):
    """ワークスペース情報更新

    Args:
        workspace_id (int): ワークスペースID

    Returns:
        Response: HTTP Respose
    """
    try:
        globals.logger.debug('#' * 50)
        globals.logger.debug('CALL {}'.format(inspect.currentframe().f_code.co_name))
        globals.logger.debug('#' * 50)

        return jsonify({"result": "200"}), 200

    except Exception as e:
        return common.serverError(e)


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('API_SERVICE_PORT', '8000')), threaded=True)
