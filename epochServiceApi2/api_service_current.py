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


def current_user_get():
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

        user_id = get_current_user(request.headers)

        api_url = "{}://{}:{}/{}/user/{}".format(os.environ['EPOCH_EPAI_API_PROTOCOL'],
                                                os.environ['EPOCH_EPAI_API_HOST'],
                                                os.environ['EPOCH_EPAI_API_PORT'],
                                                os.environ["EPOCH_EPAI_REALM_NAME"],
                                                user_id
                                            )
        #
        # get users - ユーザー取得
        #
        response = requests.get(api_url)
        if response.status_code != 200 and response.status_code != 404:
            error_detail = multi_lang.get_text("EP020-0008", "ユーザー情報の取得に失敗しました")
            raise common.UserException("{} Error user get status:{}".format(inspect.currentframe().f_code.co_name, response.status_code))

        users = json.loads(response.text)
        globals.logger.debug(f"users:{users}")

        # 取得したユーザーのロールを取得 Get the role of the acquired user
        api_url = "{}://{}:{}/{}/user/{}/roles/epoch-system".format(os.environ['EPOCH_EPAI_API_PROTOCOL'],
                                                                os.environ['EPOCH_EPAI_API_HOST'],
                                                                os.environ['EPOCH_EPAI_API_PORT'],
                                                                os.environ["EPOCH_EPAI_REALM_NAME"],
                                                                user_id
                                                        )

        #
        # get user role - ユーザーロール情報取得
        #
        response = requests.get(api_url)
        if response.status_code != 200:
            error_detail = multi_lang.get_text("EP020-0009", "ユーザーロール情報の取得に失敗しました")
            raise common.UserException("{} Error user role get status:{}".format(inspect.currentframe().f_code.co_name, response.status_code))

        ret_roles = json.loads(response.text)
        globals.logger.debug(f"roles:{ret_roles}")

        set_role_kind = []
        # 取得したすべてのロールから絞り込む Narrow down from all acquired roles
        for get_role in ret_roles["rows"]:
            kind = common.get_role_kind(get_role["name"])
            # 該当のロールのみチェック Check only the corresponding role
            if kind is not None:
                ex_role = re.match("ws-({}|\d+)-(.+)", get_role["name"])
                globals.logger.debug("role_workspace_id:{} kind:{}".format(ex_role[1], ex_role[2]))
                # 該当のワークスペースのみの絞り込み Narrow down only the applicable workspace
                if ex_role[1] == str(workspace_id):
                    set_role_kind.append(
                        {
                            "kind" : kind
                        }
                    )
        
        ret_user = {
            "user_id": user_id,
            "username": users["info"]["username"],
            "enabled": users["info"]["enabled"],
            "firstName": users["info"]["firstName"],
            "lastName": users["info"]["lastName"],
            "email": users["info"]["email"],
            "role": set_role_kind
        }

        return jsonify({"result": "200", "info": ret_user}), 200

    except common.UserException as e:
        return common.server_error_to_message(e, app_name + exec_stat, error_detail)
    except Exception as e:
        return common.server_error_to_message(e, app_name + exec_stat, error_detail)


def get_current_user(header):
    """ログインユーザID取得

    Args:
        header (dict): request header情報

    Returns:
        str: ユーザID
    """
    try:
        # 該当の要素が無い場合は、confの設定に誤り
        HEAD_REMOTE_USER = "X-REMOTE-USER"
        if not HEAD_REMOTE_USER in request.headers:
            raise Exception("get_current_user error not found header:{}".format(HEAD_REMOTE_USER))

        remote_user = request.headers[HEAD_REMOTE_USER]
        # globals.logger.debug('{}:{}'.format(HEAD_REMOTE_USER, remote_user))

        # 最初の@があるところまでをuser_idとする
        idx = remote_user.rfind('@')
        user_id = remote_user[:idx]
        # globals.logger.debug('user_id:{}'.format(user_id))

        return user_id

    except Exception as e:
        globals.logger.debug(e.args)
        globals.logger.debug(traceback.format_exc())
        raise
