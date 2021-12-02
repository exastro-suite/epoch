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

def post_manifest_parameter(workspace_id):
    """manifest パラメータ登録 manifest parameter registration

    Args:
        workspace_id (int): workspace ID

    Returns:
        Response: HTTP Respose
    """

    app_name = "ワークスペース情報:"
    exec_stat = "manifestパラメータ登録"
    error_detail = ""

    try:
        globals.logger.debug('#' * 50)
        globals.logger.debug('CALL {}'.format(inspect.currentframe().f_code.co_name))
        globals.logger.debug('#' * 50)

        # ヘッダ情報 post header info.
        post_headers = {
            'Content-Type': 'application/json',
        }

        # 引数をJSON形式で受け取りそのまま引数に設定 Receive the argument in JSON format and set it as it is
        post_data = request.json.copy()

        # send put (workspace data update)
        apiInfo = "{}://{}:{}".format(os.environ['EPOCH_RS_WORKSPACE_PROTOCOL'], os.environ['EPOCH_RS_WORKSPACE_HOST'], os.environ['EPOCH_RS_WORKSPACE_PORT'])
        globals.logger.debug("workspace put call: worksapce_id:{}".format(workspace_id))
        request_response = requests.put( "{}/workspace/{}/manifestParameter".format(apiInfo, workspace_id), headers=post_headers, data=post_data)
        # エラーの際は処理しない
        if request_response.status_code != 200:
            globals.logger.error("call rs workspace error:{}".format(request_response.status_code))
            error_detail = "ワークスペース情報更新失敗"
            raise common.Userexception(error_detail)

        # ヘッダ情報
        post_headers = {
            'Content-Type': 'application/json',
        }

        # 引数をJSON形式で受け取りそのまま引数に設定 Receive the argument in JSON format and set it as it is
        post_data = request.json.copy()

        # 呼び出すapiInfoは、環境変数より取得
        apiInfo = "{}://{}:{}".format(os.environ["EPOCH_CICD_PROTOCOL"], os.environ["EPOCH_CICD_HOST"], os.environ["EPOCH_CICD_PORT"])
        globals.logger.debug("apiInfo:" + apiInfo)

        # Manifestパラメータ設定(ITA)
        globals.logger.debug("ita/manifestParameter post call: worksapce_id:{}".format(workspace_id))
        request_response = requests.post( "{}/ita/manifestParameter".format(apiInfo), headers=post_headers, data=post_data)
        # globals.logger.debug("ita/manifestParameter:response:" + request_response.text.encode().decode('unicode-escape'))
        ret = json.loads(request_response.text)
        #ret = request_response.text
        # globals.logger.debug(ret["result"])
        if request_response.status_code != 200:
            globals.logger.error("call ita/manifestParameter error:{}".format(request_response.status_code))
            error_detail = "IT-Automation パラメータ登録失敗"
            raise common.Userexception(error_detail)

        # 正常終了 normal return code
        ret_status = 200

        return jsonify({"result": ret_status}), ret_status

    except common.UserException as e:
        return common.server_error_to_message(e, app_name + exec_stat, error_detail)
    except Exception as e:
        return common.server_error_to_message(e, app_name + exec_stat, error_detail)


def put_manifest_parameter(workspace_id):
    """manifest パラメータ更新 manifest parameter update

    Args:
        workspace_id (int): workspace ID

    Returns:
        Response: HTTP Respose
    """

    app_name = "ワークスペース情報:"
    exec_stat = "manifestパラメータ更新"
    error_detail = ""

    try:
        globals.logger.debug('#' * 50)
        globals.logger.debug('CALL {}'.format(inspect.currentframe().f_code.co_name))
        globals.logger.debug('#' * 50)
    
        # 正常終了 normal return code
        ret_status = 200

        return jsonify({"result": ret_status}), ret_status

    except common.UserException as e:
        return common.server_error_to_message(e, app_name + exec_stat, error_detail)
    except Exception as e:
        return common.server_error_to_message(e, app_name + exec_stat, error_detail)


def post_manifest_template(workspace_id):
    """manifest テンプレート登録 manifest template registration

    Args:
        workspace_id (int): workspace ID

    Returns:
        Response: HTTP Respose
    """

    app_name = "ワークスペース情報:"
    exec_stat = "manifestテンプレート登録"
    error_detail = ""

    try:
        globals.logger.debug('#' * 50)
        globals.logger.debug('CALL {}'.format(inspect.currentframe().f_code.co_name))
        globals.logger.debug('#' * 50)
    
        # 正常終了 normal return code
        ret_status = 200

        return jsonify({"result": ret_status}), ret_status

    except common.UserException as e:
        return common.server_error_to_message(e, app_name + exec_stat, error_detail)
    except Exception as e:
        return common.server_error_to_message(e, app_name + exec_stat, error_detail)


def get_manifest_template_list(workspace_id):
    """manifest テンプレート登録 manifest template registration

    Args:
        workspace_id (int): workspace ID

    Returns:
        Response: HTTP Respose
    """

    app_name = "ワークスペース情報:"
    exec_stat = "manifestテンプレート登録"
    error_detail = ""

    try:
        globals.logger.debug('#' * 50)
        globals.logger.debug('CALL {}'.format(inspect.currentframe().f_code.co_name))
        globals.logger.debug('#' * 50)
    
        rows = [
            {
                "file_id": 1,
                "file_name": "file1",
            }
        ]

        # 正常終了 normal return code
        ret_status = 200

        return jsonify({"result": ret_status, "rows": rows}), ret_status

    except common.UserException as e:
        return common.server_error_to_message(e, app_name + exec_stat, error_detail)
    except Exception as e:
        return common.server_error_to_message(e, app_name + exec_stat, error_detail)


def delete_manifest_template(workspace_id, file_id):
    """manifest テンプレート削除 manifest template delete

    Args:
        workspace_id (int): workspace ID
        file_id (int): file ID

    Returns:
        Response: HTTP Respose
    """

    app_name = "ワークスペース情報:"
    exec_stat = "manifestテンプレート削除"
    error_detail = ""

    try:
        globals.logger.debug('#' * 50)
        globals.logger.debug('CALL {}'.format(inspect.currentframe().f_code.co_name))
        globals.logger.debug('#' * 50)
    
        # 正常終了 normal return code
        ret_status = 200

        return jsonify({"result": ret_status}), ret_status

    except common.UserException as e:
        return common.server_error_to_message(e, app_name + exec_stat, error_detail)
    except Exception as e:
        return common.server_error_to_message(e, app_name + exec_stat, error_detail)
