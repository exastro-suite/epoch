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
import api_service_ci
import api_service_manifest
import api_service_cd

# 設定ファイル読み込み・globals初期化
app = Flask(__name__)
app.config.from_envvar('CONFIG_API_SERVICE_PATH')
globals.init(app)


def get_users():
    """ユーザー情報一覧取得 user info list get

    Returns:
        Response: HTTP Respose
    """

    app_name = multi_lang.get_text("EP020-0001", "ユーザー情報:")
    exec_stat = multi_lang.get_text("EP020-0002", "一覧取得")
    error_detail = ""

    try:
        globals.logger.debug('#' * 50)
        globals.logger.debug('CALL {}'.format(inspect.currentframe().f_code.co_name))
        globals.logger.debug('#' * 50)

        rows = [
            {
                "user_id": "xxxxxx1",
                "username": "taro",
                "roles": [
                    {
                        "kind": "owner"
                    }
                ]
            },
            {
                "user_id": "xxxxxx2",
                "username": "jiro",
                "roles": [
                    {
                        "kind": "manager"
                    },
                    {
                        "kind": "member-mg" 
                    }
                ]
            }
        ]

        return jsonify({"result": "200", "rows": rows}), 200

    except common.UserException as e:
        return common.server_error_to_message(e, app_name + exec_stat, error_detail)
    except Exception as e:
        return common.server_error_to_message(e, app_name + exec_stat, error_detail)


def get_workspace_members(workspace_id):
    """ワークスペース該当メンバー情報取得 workspace members get

    Returns:
        Response: HTTP Respose
    """

    app_name = multi_lang.get_text("EP020-0003", "ワークスペース情報:")
    exec_stat = multi_lang.get_text("EP020-0004", "メンバー一覧取得")
    error_detail = ""

    try:
        globals.logger.debug('#' * 50)
        globals.logger.debug('CALL {}'.format(inspect.currentframe().f_code.co_name))
        globals.logger.debug('#' * 50)

        rows = [
            {
                "user_id": "xxxxxx1",
                "username": "taro",
                "roles": [
                    {
                        "kind": "owner"
                    }
                ]
            },
            {
                "user_id": "xxxxxx2",
                "username": "jiro",
                "roles": [
                    {
                        "kind": "manager"
                    },
                    {
                        "kind": "member-mg" 
                    }
                ]
            }
        ]

        return jsonify({"result": "200", "rows": rows}), 200

    except common.UserException as e:
        return common.server_error_to_message(e, app_name + exec_stat, error_detail)
    except Exception as e:
        return common.server_error_to_message(e, app_name + exec_stat, error_detail)

def merge_workspace_users(workspace_id):
    """ワークスペース該当メンバー登録 workspace member registration

    Returns:
        Response: HTTP Respose
    """

    app_name = multi_lang.get_text("EP020-0003", "ワークスペース情報:")
    exec_stat = multi_lang.get_text("EP020-0005", "メンバー登録")
    error_detail = ""

    try:
        globals.logger.debug('#' * 50)
        globals.logger.debug('CALL {}'.format(inspect.currentframe().f_code.co_name))
        globals.logger.debug('#' * 50)

        return jsonify({"result": "200"}), 200

    except common.UserException as e:
        return common.server_error_to_message(e, app_name + exec_stat, error_detail)
    except Exception as e:
        return common.server_error_to_message(e, app_name + exec_stat, error_detail)

