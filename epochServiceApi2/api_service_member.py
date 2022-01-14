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
from datetime import timedelta, timezone
from dateutil import parser
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

import globals
import common
import const
import multi_lang

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

        api_url = "{}://{}:{}/{}/user".format(os.environ['EPOCH_EPAI_API_PROTOCOL'],
                                            os.environ['EPOCH_EPAI_API_HOST'],
                                            os.environ['EPOCH_EPAI_API_PORT'],
                                            os.environ["EPOCH_EPAI_REALM_NAME"],
                                            )
        #
        # get users - ユーザー取得
        #
        response = requests.get(api_url)
        if response.status_code != 200 and response.status_code != 404:
            error_detail = multi_lang.get_text("EP020-0008", "ユーザー情報の取得に失敗しました")
            raise common.UserException("{} Error user get status:{}".format(inspect.currentframe().f_code.co_name, response.status_code))

        users = json.loads(response.text)

        # globals.logger.debug(f"users:{users}")

        ret_users = []

        for user in users["rows"]:
            ret_user = {
                "user_id": user["id"],
                "username": user["username"],
            }

            ret_users.append(ret_user)

        rows = ret_users

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

        roles = const.ALL_ROLES

        stock_user_id = []  
        ret_users = []
        for role in roles:
            # workspace 参照権限のあるユーザーをすべて取得する Get all users with read permission
            # 子のロールでは取得できないので割り当てたロールで取得する
            # Since it cannot be acquired by the child role, it is acquired by the assigned role.
            api_url = "{}://{}:{}/{}/client/epoch-system/roles/{}/users".format(os.environ['EPOCH_EPAI_API_PROTOCOL'],
                                                    os.environ['EPOCH_EPAI_API_HOST'],
                                                    os.environ['EPOCH_EPAI_API_PORT'],
                                                    os.environ["EPOCH_EPAI_REALM_NAME"],
                                                    role.format(workspace_id)
                                                )
            #
            # get users - ユーザー取得
            #
            response = requests.get(api_url)
            if response.status_code != 200 and response.status_code != 404:
                error_detail = multi_lang.get_text("EP020-0008", "ユーザー情報の取得に失敗しました")
                raise common.UserException("{} Error user get status:{}".format(inspect.currentframe().f_code.co_name, response.status_code))

            users = json.loads(response.text)

            # globals.logger.debug(f"users:{users}")

            for user in users["rows"]:
                
                # すでに同じユーザーがいた場合は処理しない If the same user already exists, it will not be processed
                # if len(stock_user_id) > 0:
                if user["user_id"] in stock_user_id:
                    continue

                # 取得したユーザーのロールを取得 Get the role of the acquired user
                api_url = "{}://{}:{}/{}/user/{}/roles/epoch-system".format(os.environ['EPOCH_EPAI_API_PROTOCOL'],
                                                                        os.environ['EPOCH_EPAI_API_HOST'],
                                                                        os.environ['EPOCH_EPAI_API_PORT'],
                                                                        os.environ["EPOCH_EPAI_REALM_NAME"],
                                                                        user["user_id"]
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
                    "user_id": user["user_id"],
                    "username": user["user_name"],
                    "roles": set_role_kind
                }

                ret_users.append(ret_user)

                stock_user_id.append(user["user_id"])

        globals.logger.debug(f"users:{ret_users}")

        rows = ret_users

        return jsonify({"result": "200", "rows": rows}), 200

    except common.UserException as e:
        return common.server_error_to_message(e, app_name + exec_stat, error_detail)
    except Exception as e:
        return common.server_error_to_message(e, app_name + exec_stat, error_detail)

def get_workspace_members_cdexec(workspace_id):
    """ワークスペース CD実行メンバー情報取得 workspace cdexec members get

    Returns:
        Response: HTTP Respose
    """

    app_name = multi_lang.get_text("EP020-0003", "ワークスペース情報:")
    exec_stat = multi_lang.get_text("EP020-0018", "CD実行メンバー一覧取得")
    error_detail = ""

    try:
        globals.logger.debug('#' * 50)
        globals.logger.debug('CALL {}'.format(inspect.currentframe().f_code.co_name))
        globals.logger.debug('#' * 50)

        # 子のROLEからでは、もちえているユーザーの取得ができないのですべての親ロールから該当する情報を抜き出していく
        # Since it is not possible to acquire the user who has it from the child ROLE, the relevant information is extracted from all the parent roles.
        roles = const.ALL_ROLES

        # 抜き出す権限は以下を設定 Set the following for the extraction authority
        pickup_role = const.ROLE_WS_ROLE_CD_EXECUTE[0].format(workspace_id)

        stock_user_id = []  
        ret_users = []
        for role in roles:
            # workspace 参照権限のあるユーザーをすべて取得する Get all users with read permission
            # 子のロールでは取得できないので割り当てたロールで取得する
            # Since it cannot be acquired by the child role, it is acquired by the assigned role.
            api_url = "{}://{}:{}/{}/client/epoch-system/roles/{}/users".format(os.environ['EPOCH_EPAI_API_PROTOCOL'],
                                                    os.environ['EPOCH_EPAI_API_HOST'],
                                                    os.environ['EPOCH_EPAI_API_PORT'],
                                                    os.environ["EPOCH_EPAI_REALM_NAME"],
                                                    role.format(workspace_id)
                                                )
            #
            # get users - ユーザー取得
            #
            response = requests.get(api_url)
            if response.status_code != 200 and response.status_code != 404:
                error_detail = multi_lang.get_text("EP020-0008", "ユーザー情報の取得に失敗しました")
                raise common.UserException("{} Error user get status:{}".format(inspect.currentframe().f_code.co_name, response.status_code))

            users = json.loads(response.text)

            # globals.logger.debug(f"users:{users}")

            for user in users["rows"]:
                
                # すでに同じユーザーがいた場合は処理しない If the same user already exists, it will not be processed
                # if len(stock_user_id) > 0:
                if user["user_id"] in stock_user_id:
                    continue

                # 取得したユーザーのロールを取得 Get the role of the acquired user
                api_url = "{}://{}:{}/{}/user/{}/roles/epoch-system".format(os.environ['EPOCH_EPAI_API_PROTOCOL'],
                                                                        os.environ['EPOCH_EPAI_API_HOST'],
                                                                        os.environ['EPOCH_EPAI_API_PORT'],
                                                                        os.environ["EPOCH_EPAI_REALM_NAME"],
                                                                        user["user_id"]
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

                # 取得したすべてのロールから絞り込む Narrow down from all acquired roles
                for get_role in ret_roles["rows"]:
                    # 該当するロールが一致したら値を設定 Set the value when the corresponding role matches
                    if get_role["name"] == pickup_role:
                        ret_user = {
                            "user_id": user["user_id"],
                            "username": user["user_name"],
                        }
                        ret_users.append(ret_user)
                        stock_user_id.append(user["user_id"])

        globals.logger.debug(f"users:{ret_users}")

        rows = ret_users

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
    return_code = 500

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
            return_code = 400
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
            return_code = 400
            error_detail = multi_lang.get_text("EP000-0023", "対象の情報(workspace)が他で更新されたため、更新できません\n画面更新後、再度情報を入力・選択して実行してください", "workspace")
            raise common.UserException("{} update exclusive check error".format(inspect.currentframe().f_code.co_name))

        ret_status = response.status_code

        # ログインユーザーの情報取得 Get login user information
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

        for row in req_json["rows"]:

            # 登録前にすべてのroleを削除する Delete all roles before registration
            roles = const.ALL_ROLES
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
                globals.logger.debug(error_detail)
                raise common.UserException("{} Error user role add status:{}".format(inspect.currentframe().f_code.co_name, response.status_code))


            #
            # logs output - ログ出力
            #
            post_data = {
                "action" : "role update",
                "role_update_user_id" : row["user_id"],
                "role_update_user_roles" : add_roles,
            }

            api_url = "{}://{}:{}/workspace/{}/member/{}/logs/{}".format(os.environ['EPOCH_RS_LOGS_PROTOCOL'],
                                                        os.environ['EPOCH_RS_LOGS_HOST'],
                                                        os.environ['EPOCH_RS_LOGS_PORT'],
                                                        workspace_id,
                                                        users["info"]["username"],
                                                        const.LOG_KIND_UPDATE
                                                        )

            response = requests.post(api_url, headers=post_headers, data=json.dumps(post_data))
            if response.status_code != 200:
                error_detail = multi_lang.get_text("EP020-0023", "ログ出力に失敗しました")
                globals.logger.debug(error_detail)
                raise common.UserException("{} Error log output status:{}".format(inspect.currentframe().f_code.co_name, response.status_code))

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
                globals.logger.debug(error_detail)
                raise common.UserException("{} Error workspace-db update status:{}".format(inspect.currentframe().f_code.co_name, response.status_code))

            globals.logger.debug("role datetime update Succeed!")

        return jsonify({"result": "200"}), 200

    except common.UserException as e:
        return common.user_error_to_message(e, app_name + exec_stat, error_detail, return_code)
    except Exception as e:
        return common.server_error_to_message(e, app_name + exec_stat, error_detail)


def leave_workspace(workspace_id):
    """Exit from a member of the workspace - ワークスペースのメンバーから抜けます

    Args:
        workspace_id (int): workspace ID

    Returns:
        Response: HTTP Respose
    """
    app_name = multi_lang.get_text("EP020-0001", "ワークスペース情報:")
    exec_stat = multi_lang.get_text("EP020-0010", "退去")
    error_detail = ""

    try:
        globals.logger.debug('#' * 50)
        globals.logger.debug('CALL {} workspace_id [{}]'.format(inspect.currentframe().f_code.co_name, workspace_id))
        globals.logger.debug('#' * 50)

        # ヘッダ情報 header info
        post_header = {
            'Content-Type': 'application/json',
        }

        api_info_epai = "{}://{}:{}".format(os.environ["EPOCH_EPAI_API_PROTOCOL"], 
                                            os.environ["EPOCH_EPAI_API_HOST"], 
                                            os.environ["EPOCH_EPAI_API_PORT"])
        
        realm_name = "exastroplatform"
        
        # ユーザIDの取得 get user id
        user_id = common.get_current_user(request.headers)
        
        # 指定のワークスペースIDに対する、オーナーロールのユーザ一覧を取得 Get a list of owner role users for the specified workspace ID
        response = requests.get("{}/{}/client/epoch-system/roles/{}/users".format(api_info_epai, realm_name, const.ROLE_WS_OWNER[0].format(workspace_id)), headers=post_header)

        users = json.loads(response.text)
        globals.logger.debug(type(users["rows"]))
        globals.logger.debug(users["rows"])
        
        owner_check = False
        
        # 自身がオーナーかどうか確認 Check if you are the owner
        for user in users["rows"]:
            if user["user_id"] == user_id:
                owner_check = True
                break

        if owner_check:
            # 自身がオーナの場合、他のオーナーがいるかチェック If you are the owner, check if there are other owners
            if len(users["rows"]) == 1:
                # ログイン者が唯一のオーナーの時は退去できない Can't move out when the login person is the only owner
                return jsonify({"result": "400", "reason": multi_lang.get_text("EP020-0014", "あなた以外のオーナーがいないので退去できません")}), 400

        response = requests.get("{}/{}/user/{}/roles/epoch-system".format(api_info_epai, realm_name, user_id), headers=post_header)
        
        user_roles = json.loads(response.text)
        
        roles = []
        
        for role in user_roles["rows"]:            
            if "ws-{}".format(workspace_id) in role["name"]:
                roles.append(
                    {
                        "name" : role["name"]
                    }
                )
            
        post_data = {
            "roles" :  roles
        }
        
        globals.logger.debug("post_data : " + json.dumps(post_data))
        
        # 自分自身のワークスペースに関するロールを全て削除 - Delete all roles related to your own workspace
        response = requests.delete("{}/{}/user/{}/roles/epoch-system".format(api_info_epai, realm_name, user_id), headers=post_header, data=json.dumps(post_data))
        
        
        if response.status_code != 200:
            error_detail = multi_lang.get_text("EP020-0011", "ユーザクライアントロールの削除に失敗しました")
            return jsonify({"result": "400", "reason": multi_lang.get_text("EP020-0015", "ワークスペースからの退去に失敗しました")}), 400
    
        # ロールの更新日を現在時刻に変更 - Change the update date of the role to the current time
        api_info = "{}://{}:{}/workspace/{}".format(os.environ["EPOCH_RS_WORKSPACE_PROTOCOL"], 
                                                    os.environ["EPOCH_RS_WORKSPACE_HOST"], 
                                                    os.environ["EPOCH_RS_WORKSPACE_PORT"],
                                                    workspace_id)
        
        # 現在時刻を設定はrs_workspace側で処理 The current time is set on the rs_workspace side
        post_data = {
            'role_update_at' : ''
        }
        
        response = requests.patch(api_info, headers=post_header, data=json.dumps(post_data))
        
        if response.status_code != 200:
            error_detail = multi_lang.get_text("EP020-0012", "ロール更新日の変更に失敗しました")
            return jsonify({"result": "400", "reason": multi_lang.get_text("EP020-0015", "ワークスペースからの退去に失敗しました")}), 400

        return jsonify({"result": "200"}), 200

    except common.UserException as e:
        return common.server_error_to_message(e, app_name + exec_stat, error_detail)
    except Exception as e:
        return common.server_error_to_message(e, app_name + exec_stat, error_detail)
