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

def merge_workspace_members(workspace_id):
    """ワークスペース該当メンバー登録 workspace member registration

    Request: json
        {
            "rows": [
                {
                    "user_id": "",
                    "roles": [
                        {
                            "kind": "",
                        }
                    ]
                },
            ],
            "role_update_at": "",
        }

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

        # 引数はJSON形式 Arguments are in JSON format
        req_json = request.json.copy()

        # ヘッダ情報 header info.
        post_headers = {
            'Content-Type': 'application/json',
        }

        # workspace get
        api_url = "{}://{}:{}/workspace/{}".format(os.environ['EPOCH_RS_WORKSPACE_PROTOCOL'],
                                                    os.environ['EPOCH_RS_WORKSPACE_HOST'],
                                                    os.environ['EPOCH_RS_WORKSPACE_PORT'],
                                                    workspace_id)
        response = requests.get(api_url, headers=post_headers)

        if response.status_code == 200 and common.is_json_format(response.text):
            # 取得したワークスペース情報を退避 Save the acquired workspace information
            ret = json.loads(response.text)
            ws_row = ret["rows"][0]
        elif response.status_code == 404:
            error_detail = multi_lang.get_text("EP000-0022", "更新対象(workspace)がありません", "workspace")
            # 情報取得できない場合はエラー Error if information cannot be obtained
            raise common.UserException("{} not found workspace !".format(inspect.currentframe().f_code.co_name))
        else:
            if response.status_code == 500 and common.is_json_format(response.text):
                # 戻り値がJsonの場合は、値を取得 If the return value is Json, get the value
                ret = json.loads(response.text)
                # 詳細エラーがある場合は詳細を設定 Set details if there are detailed errors
                if ret["errorDetail"] is not None:
                    error_detail = ret["errorDetail"]

            raise common.UserException("{} Error get workspace db status:{}".format(inspect.currentframe().f_code.co_name, response.status_code))

        globals.logger.debug("Exclusive check")
        globals.logger.debug("db[{}] update[{}]".format(str(ws_row["role_update_at"]), req_json["role_update_at"]))
        # 排他チェック:ロール更新日時が一致しているかチェックする
        # Exclusive check: Check if the role update datetime match
        if str(ws_row["role_update_at"]) != req_json["role_update_at"]:
            error_detail = multi_lang.get_text("EP000-0023", "対象の情報(workspace)が他で更新されたため、更新できません\n画面更新後、再度情報を入力・選択して実行してください", "workspace")
            raise common.UserException("{} update exclusive check error".format(inspect.currentframe().f_code.co_name))

        ret_status = response.status_code

        for row in req_json["rows"]:

            # 登録前にすべてのroleを削除する Delete all roles before registration
            roles = [
                const.ROLE_WS_OWNER[0],
                const.ROLE_WS_MANAGER[0],
                const.ROLE_WS_MEMBER_MG[0],
                const.ROLE_WS_CI_SETTING[0],
                const.ROLE_WS_CI_RESULT[0],
                const.ROLE_WS_CD_SETTING[0],
                const.ROLE_WS_CD_EXECUTE[0],
                const.ROLE_WS_CD_RESULT[0],
            ]
            #
            # ロールの制御のurl role control url
            #
            api_url = "{}://{}:{}/{}/user/{}/roles/epoch-system".format(os.environ['EPOCH_EPAI_API_PROTOCOL'],
                                                                    os.environ['EPOCH_EPAI_API_HOST'],
                                                                    os.environ['EPOCH_EPAI_API_PORT'],
                                                                    os.environ["EPOCH_EPAI_REALM_NAME"],
                                                                    row["user_id"],
                                                            )

            del_roles = []
            for role in roles:
                del_role = {
                    "name": role.format(workspace_id),
                }
                del_roles.append(del_role)

            post_data = {
                "roles" : del_roles
            }

            #
            # delete workspace role - ワークスペース ロールの削除
            #
            response = requests.delete(api_url, headers=post_headers, data=json.dumps(post_data))
            if response.status_code != 200:
                error_detail = multi_lang.get_text("EP020-0006", "ロールの削除に失敗しました")
                raise common.UserException("{} Error user role delete status:{}".format(inspect.currentframe().f_code.co_name, response.status_code))

            # 登録するroleの情報を編集 Edit the information of the role to be registered
            add_roles = []
            for role in row["roles"]:
                add_role = {
                    "name": common.get_role_name(role["kind"]).format(workspace_id),
                    "enabled": True,
                }
                add_roles.append(add_role)
            
            post_data = {
                "roles" : add_roles
            }

            #
            # append workspace role - ワークスペース ロールの付与
            #
            response = requests.post(api_url, headers=post_headers, data=json.dumps(post_data))
            if response.status_code != 200:
                error_detail = multi_lang.get_text("EP020-0007", "ロールの登録に失敗しました")
                raise common.UserException("{} Error user role add status:{}".format(inspect.currentframe().f_code.co_name, response.status_code))

            #
            # workspace info. Roll update date update - ワークスペース情報 ロール更新日の更新
            #
            post_data = {
                "role_update_at" : "",
            }

            globals.logger.debug("role datetime update Start")
            api_url = "{}://{}:{}/workspace/{}".format(os.environ['EPOCH_RS_WORKSPACE_PROTOCOL'],
                                                        os.environ['EPOCH_RS_WORKSPACE_HOST'],
                                                        os.environ['EPOCH_RS_WORKSPACE_PORT'],
                                                        workspace_id)
            response = requests.patch(api_url, headers=post_headers, data=json.dumps(post_data))
            if response.status_code != 200:
                error_detail = multi_lang.get_text("EP000-0024", "対象の情報({})を更新できませんでした", "workspace")
                raise common.UserException("{} Error workspace-db update status:{}".format(inspect.currentframe().f_code.co_name, response.status_code))

            globals.logger.debug("role datetime update Succeed!")

        return jsonify({"result": "200"}), 200

    except common.UserException as e:
        return common.server_error_to_message(e, app_name + exec_stat, error_detail)
    except Exception as e:
        return common.server_error_to_message(e, app_name + exec_stat, error_detail)

