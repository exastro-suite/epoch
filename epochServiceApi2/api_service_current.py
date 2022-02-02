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


def current_user_get():
    """ユーザー情報取得 user info get

    Returns:
        Response: HTTP Respose
    """

    app_name = multi_lang.get_text("EP020-0001", "ユーザー情報:")
    exec_stat = multi_lang.get_text("EP020-0017", "取得")
    error_detail = ""

    try:
        globals.logger.debug('#' * 50)
        globals.logger.debug('CALL {}'.format(inspect.currentframe().f_code.co_name))
        globals.logger.debug('#' * 50)

        ret_user = user_get()

        return jsonify({"result": "200", "info": ret_user}), 200

    except common.UserException as e:
        return common.server_error_to_message(e, app_name + exec_stat, error_detail)
    except Exception as e:
        return common.server_error_to_message(e, app_name + exec_stat, error_detail)


def user_get():
    """ユーザー情報取得 user info get

    Returns:
        dict: user info.
    """

    try:
        globals.logger.debug('#' * 50)
        globals.logger.debug('CALL {}'.format(inspect.currentframe().f_code.co_name))
        globals.logger.debug('#' * 50)

        user_id = common.get_current_user(request.headers)

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
        # globals.logger.debug(f"roles:{ret_roles}")

        sorted_roles = sorted(ret_roles["rows"], key=lambda x:x['name'])
        globals.logger.debug(f"sorted_roles:{sorted_roles}")

        stock_workspace_id = []
        set_role_display = []
        ret_role = ""
        all_roles = []
        all_composite_roles = []
        workspace_name = None
        # 取得したすべてのロールから絞り込む Narrow down from all acquired roles
        for get_role in sorted_roles:
            role_info = common.get_role_info(get_role["name"])
            # 該当のロールのみチェック Check only the corresponding role
            if role_info is not None:
                # 同じロールは退避しない Do not save the same role
                if get_role["name"] not in all_roles:
                    all_roles.append(get_role["name"])

                ex_role = re.match("ws-({}|\d+)-(.+)", get_role["name"])
                globals.logger.debug("role_workspace_id:{} kind:{}".format(ex_role[1], ex_role[2]))

                # ワークスペースは重複があるので、1回のみ抽出 Workspaces are duplicated, so extract only once
                # ただし、1回目は設定しない However, do not set the first time
                if ex_role[1] not in stock_workspace_id and workspace_name is not None:
                    # 並んでいる要素をソート Sort the elements in a row
                    set_role_display.sort()
                    # ソート用の文字列カット String cut for sorting
                    role_display = [s[3:] for s in set_role_display]
                    # workspace_id が 変わった際にレコード化 Record when workspace_id changes
                    ret_role = ret_role + ',"{}":["{}"]'.format(workspace_name, '","'.join(role_display))
                    set_role_display = []

                # 取得したロール名を配列にする Make the acquired role name into an array
                set_role_display.append(f"{role_info[3]:02}:" + multi_lang.get_text(role_info[1], role_info[2]))

                workspace_id = ex_role[1]
                stock_workspace_id.append(workspace_id)
                # workspace get
                api_url = "{}://{}:{}/workspace/{}".format(os.environ['EPOCH_RS_WORKSPACE_PROTOCOL'],
                                                            os.environ['EPOCH_RS_WORKSPACE_HOST'],
                                                            os.environ['EPOCH_RS_WORKSPACE_PORT'],
                                                            workspace_id)

                response = requests.get(api_url)
                if response.status_code != 200:
                    error_detail = multi_lang.get_text("EP020-0013", "ワークスペース情報の取得に失敗しました")
                    raise common.UserException("{} Error workspace get status:{}".format(inspect.currentframe().f_code.co_name, response.status_code))

                ret_ws = json.loads(response.text)
                workspace_name = ret_ws["rows"][0]["common"]["name"]
                # workspace name empty to set fix name
                if len(workspace_name) == 0:
                    workspace_name = multi_lang.get_text("EP000-0025", "名称未設定")
            else:
                # 同じ子ロールは退避しない Do not save the same composite role
                if get_role["name"] not in all_composite_roles:
                    all_composite_roles.append(get_role["name"])

        # 並んでいる要素をソート Sort the elements in a row
        set_role_display.sort()
        # ソート用の文字列カット String cut for sorting
        role_display = [s[3:] for s in set_role_display]
        
        ret_role = ret_role + ',"{}":["{}"]'.format(workspace_name, '","'.join(role_display))
        ret_role = "{" + ret_role[1:] + "}" 

        ret_user = {
            "user_id": user_id,
            "username": users["info"]["username"],
            "enabled": users["info"]["enabled"],
            "firstName": users["info"]["firstName"],
            "lastName": users["info"]["lastName"],
            "email": users["info"]["email"],
            "role": ret_role,
            "roles": all_roles,
            "composite_roles": all_composite_roles,
        }
        globals.logger.debug(f"ret_user:{ret_user}")

        return ret_user

    except common.UserException as e:
        raise
    except Exception as e:
        raise
