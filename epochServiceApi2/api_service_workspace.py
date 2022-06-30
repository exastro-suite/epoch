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
import api_service_current

# 設定ファイル読み込み・globals初期化
app = Flask(__name__)
app.config.from_envvar('CONFIG_API_SERVICE_PATH')
globals.init(app)

def create_workspace():
    """ワークスペース作成

    Returns:
        Response: HTTP Respose
    """

    app_name = "ワークスペース情報:"
    exec_stat = "作成"
    error_detail = ""

    try:
        globals.logger.debug('#' * 50)
        globals.logger.debug('CALL {}'.format(inspect.currentframe().f_code.co_name))
        globals.logger.debug('#' * 50)

        # ヘッダ情報
        post_headers = {
            'Content-Type': 'application/json',
        }

        # 引数をJSON形式で受け取りそのまま引数に設定
        post_data = request.json.copy()

        # user_idの取得
        user_id = common.get_current_user(request.headers)

        # workspace put送信
        api_url = "{}://{}:{}/workspace".format(os.environ['EPOCH_RS_WORKSPACE_PROTOCOL'],
                                                os.environ['EPOCH_RS_WORKSPACE_HOST'],
                                                os.environ['EPOCH_RS_WORKSPACE_PORT'])

        response = requests.post(api_url, headers=post_headers, data=json.dumps(post_data))

        if response.status_code == 200:
            # 正常時は戻り値がレコードの値なのでそのまま返却する
            ret = json.loads(response.text)
            rows = ret['rows']
        else:
            if common.is_json_format(response.text):
                ret = json.loads(response.text)
                # 詳細エラーがある場合は詳細を設定
                if ret["errorDetail"] is not None:
                    error_detail = ret["errorDetail"]

            raise common.UserException("{} Error post workspace db status:{}".format(inspect.currentframe().f_code.co_name, response.status_code))

        # Get the workspace ID - ワークスペースIDを取得する
        workspace_id=rows[0]["workspace_id"]

        # Set workspace roles - ワークスペースのロールを設定する
        create_workspace_setting_roles(workspace_id, user_id)

        # exastro-authentication-infra setting - 認証基盤の設定
        create_workspace_setting_auth_infra(workspace_id, user_id)

        # workspace 状態取得 workspace status get
        api_url = "{}://{}:{}/workspace/{}/status".format(os.environ['EPOCH_RS_WORKSPACE_PROTOCOL'],
                                                            os.environ['EPOCH_RS_WORKSPACE_HOST'],
                                                            os.environ['EPOCH_RS_WORKSPACE_PORT'],
                                                            workspace_id)

        response = requests.get(api_url)

        if response.status_code == 200:
            # 取得したワークスペース状態を退避 Save the acquired workspace status
            get_workspace_status = json.loads(response.text)
            # 更新で使用する項目のみを展開する Expand only the items used in the update
            workspace_status = {
                const.STATUS_INITIALIZE : const.STATUS_OK
            }
        else:
            # 存在しない場合は、初期設定する If it does not exist, initialize it
            workspace_status = const.WORKSPACE_STATUS
            workspace_status[const.STATUS_INITIALIZE] = const.STATUS_OK

        # 状態が無ければ初回登録する
        if response.status_code == 404:
            # workspace 状態登録 workspace status registration
            api_url = "{}://{}:{}/workspace/{}/status".format(os.environ['EPOCH_RS_WORKSPACE_PROTOCOL'],
                                                                os.environ['EPOCH_RS_WORKSPACE_HOST'],
                                                                os.environ['EPOCH_RS_WORKSPACE_PORT'],
                                                                workspace_id)

            response = requests.post(api_url, headers=post_headers, data=json.dumps(workspace_status))

            if response.status_code != 200:
                raise common.UserException("{} Error post workspace status db status:{}".format(inspect.currentframe().f_code.co_name, response.status_code))
        else:
            # workspace 状態更新 workspace status update
            api_url = "{}://{}:{}/workspace/{}/status".format(os.environ['EPOCH_RS_WORKSPACE_PROTOCOL'],
                                                                os.environ['EPOCH_RS_WORKSPACE_HOST'],
                                                                os.environ['EPOCH_RS_WORKSPACE_PORT'],
                                                                workspace_id)

            response = requests.put(api_url, headers=post_headers, data=json.dumps(workspace_status))

            if response.status_code != 200:
                raise common.UserException("{} Error put workspace status db status:{}".format(inspect.currentframe().f_code.co_name, response.status_code))

        ret_status = 200

        # 戻り値をそのまま返却
        return jsonify({"result": ret_status, "rows": rows}), ret_status

    except common.UserException as e:
        return common.server_error_to_message(e, app_name + exec_stat, error_detail)
    except Exception as e:
        return common.server_error_to_message(e, app_name + exec_stat, error_detail)


def create_workspace_setting_roles(workspace_id, user_id):
    """Set workspace roles - ワークスペースのロールを設定する

    Args:
        workspace_id (int): workspace id
        user_id (str): login user id
    """

    try:

        # ヘッダ情報 post header
        post_headers = {
            'Content-Type': 'application/json',
        }

        api_url = "{}://{}:{}/{}/client/epoch-system/role".format(os.environ['EPOCH_EPAI_API_PROTOCOL'],
                                                                os.environ['EPOCH_EPAI_API_HOST'],
                                                                os.environ['EPOCH_EPAI_API_PORT'],
                                                                os.environ["EPOCH_EPAI_REALM_NAME"]
                                                        )

        # rolesの取得 get a roles
        post_data = set_roles(workspace_id)

        response = requests.post(api_url, headers=post_headers, data=json.dumps(post_data))

        #
        # append workspace owner role - ワークスペースオーナーロールの付与
        #
        api_url = "{}://{}:{}/{}/user/{}/roles/epoch-system".format(os.environ['EPOCH_EPAI_API_PROTOCOL'],
                                                                os.environ['EPOCH_EPAI_API_HOST'],
                                                                os.environ['EPOCH_EPAI_API_PORT'],
                                                                os.environ["EPOCH_EPAI_REALM_NAME"],
                                                                user_id,
                                                        )
        post_data = {
            "roles" : [
                {
                    "name": const.ROLE_WS_OWNER[0].format(workspace_id),
                    "enabled": True,
                }
            ]
        }

        response = requests.post(api_url, headers=post_headers, data=json.dumps(post_data))

    except common.UserException as e:
        globals.logger.debug(e.args)
        raise
    except Exception as e:
        globals.logger.debug(e.args)
        raise

def create_workspace_setting_auth_infra(workspace_id, user_id):
    """exastro-authentication-infra setting - 認証基盤の設定

    Args:
        workspace_id (int): workspace id
        user_id (str): login user id
    """

    try:

        # ヘッダ情報
        post_headers = {
            'Content-Type': 'application/json',
        }

        # authentication-infra-api の呼び先設定
        api_url_epai = "{}://{}:{}/".format(os.environ["EPOCH_EPAI_API_PROTOCOL"],
                                            os.environ["EPOCH_EPAI_API_HOST"],
                                            os.environ["EPOCH_EPAI_API_PORT"])

        # get namespace
        namespace = common.get_namespace_name(workspace_id)

        # get pipeline name
        pipeline_name = common.get_pipeline_name(workspace_id)


        #
        # Generate a client for use in the workspace - ワークスペースで使用するクライアントを生成
        #
        # postする情報 post information
        clients = [
            {
                "client_id" :   'epoch-ws-{}-ita'.format(workspace_id),
                "client_host" : os.environ["EPOCH_EPAI_HOST"],
                "client_protocol" : "https",
                "conf_template" : "epoch-ws-ita-template.conf",
                "backend_url" : "http://it-automation.{}.svc:8084/".format(namespace),
                "require_claim" : const.ROLE_WS_ROLE_CD_EXECUTE_RESULT[0].format(workspace_id),
                "mapping_client_id" : "epoch-system",
            },
            {
                "client_id" :   'epoch-ws-{}-sonarqube'.format(workspace_id),
                "client_host" : os.environ["EPOCH_EPAI_HOST"],
                "client_protocol" : "https",
                "conf_template" : "epoch-ws-sonarqube-template.conf",
                "backend_url" : "http://sonarqube.{}.svc:9000/".format(pipeline_name),
                "require_claim" : const.ROLE_WS_ROLE_CI_PIPELINE_RESULT[0].format(workspace_id),
                "mapping_client_id" : "epoch-system",
            },
        ]

        # post送信（アクセス情報生成）
        exec_stat = "認証基盤 client設定"
        for client in clients:
            response = requests.post("{}{}/{}/{}".format(api_url_epai, 'settings', os.environ["EPOCH_EPAI_REALM_NAME"], 'clients'), headers=post_headers, data=json.dumps(client))

            # 正常時以外はExceptionを発行して終了する
            if response.status_code != 200:
                globals.logger.debug(response.text)
                error_detail = "認証基盤 client設定に失敗しました。 {}".format(response.status_code)
                raise common.UserException(error_detail)

        #
        # Set usage authority of url used in workspace - ワークスペースで使用するurlの使用権限の設定する
        #
        exec_stat = "認証基盤 route設定"
        post_data = {
            "route_id" : namespace,
            "template_file" : "epoch-system-ws-template.conf",
            "render_params" : {
                "workspace_id" : workspace_id,
            }
        }
        response = requests.post(
            "{}settings/{}/clients/epoch-system/route".format(api_url_epai, os.environ["EPOCH_EPAI_REALM_NAME"]),
            headers=post_headers,
            data=json.dumps(post_data)
        )
        # 正常時以外はExceptionを発行して終了する
        if response.status_code != 200:
            globals.logger.debug(response.text)
            error_detail = "認証基盤 route設定に失敗しました。 {}".format(response.status_code)
            raise common.UserException(error_detail)

        #
        # Do "httpd graceful" - Apacheの設定読込を行う
        #
        exec_stat = "認証基盤 設定読み込み"
        response = requests.put("{}{}".format(api_url_epai, 'apply_settings'), headers=post_headers, data="{}")
        if response.status_code != 200:
            globals.logger.debug(response.text)
            error_detail = "認証基盤 設定読み込みに失敗しました。 {}".format(response.status_code)
            raise common.UserException(error_detail)

    except common.UserException as e:
        globals.logger.debug(e.args)
        raise
    except Exception as e:
        globals.logger.debug(e.args)
        raise

def set_roles(workspace_id):
    """role設定するjsonの内容を編集する（client毎にロールが必要だが内容は同じのため共通化）
        Edit the content of json to set role (role is required for each client, but the content is the same, so it is common)

    Args:
        workspace_id (int): workspace id

    Returns:
        json: "roles" = [ ]
    """

    try:
        json_roles = {
            "roles" : [
                # ロール権限をすべて定義 Define all role permissions
                {
                    "name": const.ROLE_WS_ROLE_WS_REFERENCE[0].format(workspace_id),
                    "composite_roles": [],
                    "attributes": {
                        "display": [ const.ROLE_WS_ROLE_WS_REFERENCE[1] ],
                        "display_default": [ const.ROLE_WS_ROLE_WS_REFERENCE[2] ],
                    }
                },
                {
                    "name": const.ROLE_WS_ROLE_WS_NAME_UPDATE[0].format(workspace_id),
                    "composite_roles": [],
                    "attributes": {
                        "display": [ const.ROLE_WS_ROLE_WS_NAME_UPDATE[1] ],
                        "display_default": [ const.ROLE_WS_ROLE_WS_NAME_UPDATE[2] ],
                    }
                },
                {
                    "name": const.ROLE_WS_ROLE_WS_CI_UPDATE[0].format(workspace_id),
                    "composite_roles": [],
                    "attributes": {
                        "display": [ const.ROLE_WS_ROLE_WS_CI_UPDATE[1] ],
                        "display_default": [ const.ROLE_WS_ROLE_WS_CI_UPDATE[2] ],
                    }
                },
                {
                    "name": const.ROLE_WS_ROLE_WS_CD_UPDATE[0].format(workspace_id),
                    "composite_roles": [],
                    "attributes": {
                        "display": [ const.ROLE_WS_ROLE_WS_CD_UPDATE[1] ],
                        "display_default": [ const.ROLE_WS_ROLE_WS_CD_UPDATE[2] ],
                    }
                },
                {
                    "name": const.ROLE_WS_ROLE_WS_DELETE[0].format(workspace_id),
                    "composite_roles": [],
                    "attributes": {
                        "display": [ const.ROLE_WS_ROLE_WS_DELETE[1] ],
                        "display_default": [ const.ROLE_WS_ROLE_WS_DELETE[2] ],
                    }
                },
                {
                    "name": const.ROLE_WS_ROLE_OWNER_ROLE_SETTING[0].format(workspace_id),
                    "composite_roles": [],
                    "attributes": {
                        "display": [ const.ROLE_WS_ROLE_OWNER_ROLE_SETTING[1] ],
                        "display_default": [ const.ROLE_WS_ROLE_OWNER_ROLE_SETTING[2] ],
                    }
                },
                {
                    "name": const.ROLE_WS_ROLE_MEMBER_ADD[0].format(workspace_id),
                    "composite_roles": [],
                    "attributes": {
                        "display": [ const.ROLE_WS_ROLE_MEMBER_ADD[1] ],
                        "display_default": [ const.ROLE_WS_ROLE_MEMBER_ADD[2] ],
                    }
                },
                {
                    "name": const.ROLE_WS_ROLE_MEMBER_ROLE_UPDATE[0].format(workspace_id),
                    "composite_roles": [],
                    "attributes": {
                        "display": [ const.ROLE_WS_ROLE_MEMBER_ROLE_UPDATE[1] ],
                        "display_default": [ const.ROLE_WS_ROLE_MEMBER_ROLE_UPDATE[2] ],
                    }
                },
                {
                    "name": const.ROLE_WS_ROLE_CI_PIPELINE_RESULT[0].format(workspace_id),
                    "composite_roles": [],
                    "attributes": {
                        "display": [ const.ROLE_WS_ROLE_CI_PIPELINE_RESULT[1] ],
                        "display_default": [ const.ROLE_WS_ROLE_CI_PIPELINE_RESULT[2] ],
                    }
                },
                {
                    "name": const.ROLE_WS_ROLE_MANIFEST_UPLOAD[0].format(workspace_id),
                    "composite_roles": [],
                    "attributes": {
                        "display": [ const.ROLE_WS_ROLE_MANIFEST_UPLOAD[1] ],
                        "display_default": [ const.ROLE_WS_ROLE_MANIFEST_UPLOAD[2] ],
                    }
                },
                {
                    "name": const.ROLE_WS_ROLE_MANIFEST_SETTING[0].format(workspace_id),
                    "composite_roles": [],
                    "attributes": {
                        "display": [ const.ROLE_WS_ROLE_MANIFEST_SETTING[1] ],
                        "display_default": [ const.ROLE_WS_ROLE_MANIFEST_SETTING[2] ],
                    }
                },
                {
                    "name": const.ROLE_WS_ROLE_CD_EXECUTE[0].format(workspace_id),
                    "composite_roles": [],
                    "attributes": {
                        "display": [ const.ROLE_WS_ROLE_CD_EXECUTE[1] ],
                        "display_default": [ const.ROLE_WS_ROLE_CD_EXECUTE[2] ],
                    }
                },
                {
                    "name": const.ROLE_WS_ROLE_CD_EXECUTE_RESULT[0].format(workspace_id),
                    "composite_roles": [],
                    "attributes": {
                        "display": [ const.ROLE_WS_ROLE_CD_EXECUTE_RESULT[1] ],
                        "display_default": [ const.ROLE_WS_ROLE_CD_EXECUTE_RESULT[2] ],
                    }
                },
                # ロールをすべて定義 Define all roles
                {
                    "name": const.ROLE_WS_OWNER[0].format(workspace_id),
                    "composite_roles": [ const.ROLE_WS_ROLE_WS_REFERENCE[0].format(workspace_id),
                                        const.ROLE_WS_ROLE_WS_NAME_UPDATE[0].format(workspace_id),
                                        const.ROLE_WS_ROLE_WS_CI_UPDATE[0].format(workspace_id),
                                        const.ROLE_WS_ROLE_WS_CD_UPDATE[0].format(workspace_id),
                                        const.ROLE_WS_ROLE_WS_DELETE[0].format(workspace_id),
                                        const.ROLE_WS_ROLE_OWNER_ROLE_SETTING[0].format(workspace_id),
                                        const.ROLE_WS_ROLE_MEMBER_ADD[0].format(workspace_id),
                                        const.ROLE_WS_ROLE_MEMBER_ROLE_UPDATE[0].format(workspace_id),
                                        const.ROLE_WS_ROLE_CI_PIPELINE_RESULT[0].format(workspace_id),
                                        const.ROLE_WS_ROLE_MANIFEST_UPLOAD[0].format(workspace_id),
                                        const.ROLE_WS_ROLE_MANIFEST_SETTING[0].format(workspace_id),
                                        const.ROLE_WS_ROLE_CD_EXECUTE[0].format(workspace_id),
                                        const.ROLE_WS_ROLE_CD_EXECUTE_RESULT[0].format(workspace_id),
                    ],
                    "attributes": {
                        "display": [ const.ROLE_WS_OWNER[1] ],
                        "display_default": [ const.ROLE_WS_OWNER[2] ],
                    }
                },
                {
                    "name": const.ROLE_WS_MANAGER[0].format(workspace_id),
                    "composite_roles": [ const.ROLE_WS_ROLE_WS_REFERENCE[0].format(workspace_id),
                                        const.ROLE_WS_ROLE_WS_NAME_UPDATE[0].format(workspace_id),
                                        const.ROLE_WS_ROLE_WS_CI_UPDATE[0].format(workspace_id),
                                        const.ROLE_WS_ROLE_WS_CD_UPDATE[0].format(workspace_id),
                                        const.ROLE_WS_ROLE_MEMBER_ADD[0].format(workspace_id),
                                        const.ROLE_WS_ROLE_MEMBER_ROLE_UPDATE[0].format(workspace_id),
                                        const.ROLE_WS_ROLE_CI_PIPELINE_RESULT[0].format(workspace_id),
                                        const.ROLE_WS_ROLE_MANIFEST_UPLOAD[0].format(workspace_id),
                                        const.ROLE_WS_ROLE_MANIFEST_SETTING[0].format(workspace_id),
                                        const.ROLE_WS_ROLE_CD_EXECUTE[0].format(workspace_id),
                                        const.ROLE_WS_ROLE_CD_EXECUTE_RESULT[0].format(workspace_id),
                    ],
                    "attributes": {
                        "display": [ const.ROLE_WS_MANAGER[1] ],
                        "display_default": [ const.ROLE_WS_MANAGER[2] ],
                    }
                },
                {
                    "name": const.ROLE_WS_MEMBER_MG[0].format(workspace_id),
                    "composite_roles": [ const.ROLE_WS_ROLE_WS_REFERENCE[0].format(workspace_id),
                                        const.ROLE_WS_ROLE_MEMBER_ADD[0].format(workspace_id),
                                        const.ROLE_WS_ROLE_MEMBER_ROLE_UPDATE[0].format(workspace_id),
                    ],
                    "attributes": {
                        "display": [ const.ROLE_WS_MEMBER_MG[1] ],
                        "display_default": [ const.ROLE_WS_MEMBER_MG[2] ],
                    }
                },
                {
                    "name": const.ROLE_WS_CI_SETTING[0].format(workspace_id),
                    "composite_roles": [ const.ROLE_WS_ROLE_WS_REFERENCE[0].format(workspace_id),
                                        const.ROLE_WS_ROLE_WS_CI_UPDATE[0].format(workspace_id),
                                        const.ROLE_WS_ROLE_CI_PIPELINE_RESULT[0].format(workspace_id),
                                        const.ROLE_WS_ROLE_MANIFEST_UPLOAD[0].format(workspace_id),
                    ],
                    "attributes": {
                        "display": [ const.ROLE_WS_CI_SETTING[1] ],
                        "display_default": [ const.ROLE_WS_CI_SETTING[2] ],
                    }
                },
                {
                    "name": const.ROLE_WS_CI_RESULT[0].format(workspace_id),
                    "composite_roles": [ const.ROLE_WS_ROLE_WS_REFERENCE[0].format(workspace_id),
                                        const.ROLE_WS_ROLE_CI_PIPELINE_RESULT[0].format(workspace_id),
                    ],
                    "attributes": {
                        "display": [ const.ROLE_WS_CI_RESULT[1] ],
                        "display_default": [ const.ROLE_WS_CI_RESULT[2] ],
                    }
                },
                {
                    "name": const.ROLE_WS_CD_SETTING[0].format(workspace_id),
                    "composite_roles": [ const.ROLE_WS_ROLE_WS_REFERENCE[0].format(workspace_id),
                                        const.ROLE_WS_ROLE_WS_CD_UPDATE[0].format(workspace_id),
                                        const.ROLE_WS_ROLE_MANIFEST_SETTING[0].format(workspace_id),
                                        const.ROLE_WS_ROLE_CD_EXECUTE_RESULT[0].format(workspace_id),
                    ],
                    "attributes": {
                        "display": [ const.ROLE_WS_CD_SETTING[1] ],
                        "display_default": [ const.ROLE_WS_CD_SETTING[2] ],
                    }
                },
                {
                    "name": const.ROLE_WS_CD_EXECUTE[0].format(workspace_id),
                    "composite_roles": [ const.ROLE_WS_ROLE_WS_REFERENCE[0].format(workspace_id),
                                        const.ROLE_WS_ROLE_CD_EXECUTE[0].format(workspace_id),
                                        const.ROLE_WS_ROLE_CD_EXECUTE_RESULT[0].format(workspace_id),
                    ],
                    "attributes": {
                        "display": [ const.ROLE_WS_CD_EXECUTE[1] ],
                        "display_default": [ const.ROLE_WS_CD_EXECUTE[2] ],
                    }
                },
                {
                    "name": const.ROLE_WS_CD_RESULT[0].format(workspace_id),
                    "composite_roles": [ const.ROLE_WS_ROLE_WS_REFERENCE[0].format(workspace_id),
                                        const.ROLE_WS_ROLE_CD_EXECUTE_RESULT[0].format(workspace_id),
                    ],
                    "attributes": {
                        "display": [ const.ROLE_WS_CD_RESULT[1] ],
                        "display_default": [ const.ROLE_WS_CD_RESULT[2] ],
                    }
                },
            ]
        }

        return json_roles

    except common.UserException as e:
        globals.logger.debug(e.args)
        raise
    except Exception as e:
        globals.logger.debug(e.args)
        raise


def get_workspace_list():
    """ワークスペース情報一覧取得

    Returns:
        Response: HTTP Respose
    """

    app_name = "ワークスペース情報:"
    exec_stat = "一覧取得"
    error_detail = ""

    try:
        globals.logger.debug('#' * 50)
        globals.logger.debug('CALL {}'.format(inspect.currentframe().f_code.co_name))
        globals.logger.debug('#' * 50)

        # ヘッダ情報 header info
        post_headers = {
            'Content-Type': 'application/json',
        }

        # ワークスペース情報取得 get workspace info
        api_url = "{}://{}:{}/workspace".format(os.environ['EPOCH_RS_WORKSPACE_PROTOCOL'],
                                                os.environ['EPOCH_RS_WORKSPACE_HOST'],
                                                os.environ['EPOCH_RS_WORKSPACE_PORT'])
        users_response = requests.get(api_url, headers=post_headers)

        # user_idの取得 get user id
        user_id = common.get_current_user(request.headers)

        # ユーザクライアントロール情報取得 get user client role info
        epai_api_url = "{}://{}:{}/{}/user/{}/roles/epoch-system".format(os.environ['EPOCH_EPAI_API_PROTOCOL'],
                                                                        os.environ['EPOCH_EPAI_API_HOST'],
                                                                        os.environ['EPOCH_EPAI_API_PORT'],
                                                                        os.environ["EPOCH_EPAI_REALM_NAME"],
                                                                        user_id)
        epai_resp_user_role = requests.get(epai_api_url, headers=post_headers)

        rows = []

        if users_response.status_code == 200 and common.is_json_format(users_response.text) \
        and epai_resp_user_role.status_code == 200 and common.is_json_format(epai_resp_user_role.text):
            user_roles = json.loads(epai_resp_user_role.text)
            # 取得した情報で必要な部分のみを編集して返却する Edit and return only the necessary part of the acquired information
            ret = json.loads(users_response.text)
            for data_row in ret["rows"]:
                # ログインユーザーのロールが該当するワークスペースの参照権限があるかチェックする
                # Check if the logged-in user's role has read permission for the applicable workspace
                find = False
                roles = []
                for role in user_roles["rows"]:
                    if role["name"] == const.ROLE_WS_ROLE_WS_REFERENCE[0].format(data_row["workspace_id"]):
                        find = True

                        # クライアントロール表示名取得 get client role display name
                        epai_api_url = "{}://{}:{}/{}/client/epoch-system/role/{}".format(os.environ['EPOCH_EPAI_API_PROTOCOL'],
                                                                                        os.environ['EPOCH_EPAI_API_HOST'],
                                                                                        os.environ['EPOCH_EPAI_API_PORT'],
                                                                                        os.environ["EPOCH_EPAI_REALM_NAME"],
                                                                                        role["name"])

                        epai_resp_role_disp_name = requests.get(epai_api_url, headers=post_headers)
                        role_info = json.loads(epai_resp_role_disp_name.text)["rows"]
                        # globals.logger.debug("role_info:{}".format(role_info))

                        disp_row = {
                            "id": role["name"],
                            "name": "",
                        }
                        # 表示する項目が存在した際は、多言語変換を実施して値を設定
                        # If there is an item to be displayed, perform multilingual conversion and set the value.
                        if "attributes" in role_info:
                            if "display" in role_info["attributes"]:
                                disp_row["name"] = multi_lang.get_text(role_info["attributes"]["display"], role_info["attributes"]["display_default"])

                        roles.append(disp_row)

                        break

                # Display in list with reference role - 参照ロールありで一覧に表示する
                if find:
                    all_roles = const.ALL_ROLES
                    stock_user_id = []
                    set_role_kind = []

                    #
                    # Processing for all roles - 全てのロールに対する処理
                    #
                    for role in all_roles:
                        # Get a list of users associated with the specified workspace - 指定したワークスペースに紐づくユーザ一覧を取得
                        epai_api_url = "{}://{}:{}/{}/client/epoch-system/roles/{}/users".format(os.environ['EPOCH_EPAI_API_PROTOCOL'],
                                                                                                os.environ['EPOCH_EPAI_API_HOST'],
                                                                                                os.environ['EPOCH_EPAI_API_PORT'],
                                                                                                os.environ["EPOCH_EPAI_REALM_NAME"],
                                                                                                role.format(data_row["workspace_id"]))
                        # get a list of users - ユーザー一覧取得
                        users_response = requests.get(epai_api_url)
                        if users_response.status_code != 200 and users_response.status_code != 404:
                            error_detail = multi_lang.get_text("EP020-0008", "ユーザー情報の取得に失敗しました")
                            raise common.UserException("{} Error user get status:{}".format(inspect.currentframe().f_code.co_name, users_response.status_code))

                        users = json.loads(users_response.text)

                        #
                        # Processing for the acquired user list - 取得したユーザ一覧に対する処理
                        #
                        for user in users["rows"]:
                            # Do not handle duplicate users - 重複したユーザーの場合は処理しない
                            if user["user_id"] in stock_user_id:
                                continue
                            # Unique user ID is stocked to get the number of members
                            # メンバー数取得のために、一意のユーザIDはストックする
                            stock_user_id.append(user["user_id"])

                    #
                    # ログインユーザに対する処理
                    #
                    # Get role info - ロール情報を取得
                    epai_api_url = "{}://{}:{}/{}/user/{}/roles/epoch-system".format(os.environ['EPOCH_EPAI_API_PROTOCOL'],
                                                                                    os.environ['EPOCH_EPAI_API_HOST'],
                                                                                    os.environ['EPOCH_EPAI_API_PORT'],
                                                                                    os.environ["EPOCH_EPAI_REALM_NAME"],
                                                                                    user_id)
                    user_role_response = requests.get(epai_api_url)
                    if user_role_response.status_code != 200:
                        error_detail = multi_lang.get_text("EP020-0009", "ユーザーロール情報の取得に失敗しました")
                        raise common.UserException("{} Error user role get status:{}".format(inspect.currentframe().f_code.co_name, users_response.status_code))

                    user_roles = json.loads(user_role_response.text)
                    # globals.logger.debug("user_roles: {}".format(user_roles["rows"]))

                    #
                    # Processing for all roles of the acquired login user - 取得したログインユーザの全ロールに対しての処理
                    #
                    for get_role in user_roles["rows"]:
                        kind = common.get_role_kind(get_role["name"])

                        # Check only the corresponding role - 該当のロールのみチェック
                        if kind is not None:
                            # ワークスペース作成権限は読み飛ばし Skip workspace creation authority
                            if get_role["name"] == const.ROLE_WS_CREATE[0]:
                                continue

                            ex_role = re.match("ws-({}|\d+)-(.+)", get_role["name"])
                            # globals.logger.debug("role_workspace_id:{} kind:{}".format(ex_role[1], kind))

                            # Narrow down only the applicable workspace - 該当のワークスペースのみの絞り込み
                            if ex_role[1] == str(data_row["workspace_id"]):
                                role_info = common.get_role_info(get_role["name"])
                                set_role_kind.append(
                                    {
                                        "kind" : kind,
                                        "sort" : role_info[3]
                                    }
                                )

                    # ロールの表示順を並び替え Sort the display order of roles
                    set_role_kind_sorted = sorted(set_role_kind, key=lambda x:x['sort'])

                    # Return value JSON formatting - 返り値 JSON整形
                    row = {
                        "workspace_id": data_row["workspace_id"],
                        "workspace_name": data_row["common"]["name"],
                        "roles": set_role_kind_sorted,
                        "members": len(stock_user_id),
                        "workspace_remarks": data_row["common"]["note"],
                        "update_at": data_row["update_at"],
                    }
                    rows.append(row)

        elif not users_response.status_code == 404:
            # 404以外の場合は、エラー、404はレコードなしで返却（エラーにはならない） If it is other than 404, it is an error, and 404 is returned without a record (it does not become an error)
            raise Exception('{} Error:{}'.format(inspect.currentframe().f_code.co_name, users_response.status_code))

        return jsonify({"result": "200", "rows": rows}), 200

    except common.UserException as e:
        return common.server_error_to_message(e, app_name + exec_stat, error_detail)
    except Exception as e:
        return common.server_error_to_message(e, app_name + exec_stat, error_detail)


def get_workspace(workspace_id):
    """ワークスペース情報取得

    Args:
        workspace_id (int): workspace ID

    Returns:
        Response: HTTP Respose
    """

    app_name = "ワークスペース情報:"
    exec_stat = "取得"
    error_detail = ""

    try:
        globals.logger.debug('#' * 50)
        globals.logger.debug('CALL {}'.format(inspect.currentframe().f_code.co_name))
        globals.logger.debug('#' * 50)

        # ヘッダ情報
        post_headers = {
            'Content-Type': 'application/json',
        }

        # workspace GET送信
        api_url = "{}://{}:{}/workspace/{}".format(os.environ['EPOCH_RS_WORKSPACE_PROTOCOL'],
                                                    os.environ['EPOCH_RS_WORKSPACE_HOST'],
                                                    os.environ['EPOCH_RS_WORKSPACE_PORT'],
                                                    workspace_id)
        response = requests.get(api_url, headers=post_headers)

        if response.status_code == 200 and common.is_json_format(response.text):
            # 取得したJSON結果が正常でない場合、例外を返す
            ret = json.loads(response.text)
            rows = ret["rows"]
            ret_status = response.status_code

            # 現在のユーザーのロール値を取得 Get the role value of the current user
            user = api_service_current.user_get()
            roles = user["composite_roles"]

            # 権限によって、セキュア項目をマスクする Mask secure items by permission
            # ワークスペース更新 (CI)無しの場合 Without workspace update (CI)
            if const.ROLE_WS_ROLE_WS_CI_UPDATE[0].format(workspace_id) not in roles:
                rows[0]["ci_config"]["pipelines_common"]["git_repositry"]["password"] = common.str_mask(rows[0]["ci_config"]["pipelines_common"]["git_repositry"]["password"])
                rows[0]["ci_config"]["pipelines_common"]["git_repositry"]["token"] = common.str_mask(rows[0]["ci_config"]["pipelines_common"]["git_repositry"]["token"])
                rows[0]["ci_config"]["pipelines_common"]["container_registry"]["password"] = common.str_mask(rows[0]["ci_config"]["pipelines_common"]["container_registry"]["password"])

            # ワークスペース更新 (CD)無しの場合 Without workspace update (CD)
            if const.ROLE_WS_ROLE_WS_CD_UPDATE[0].format(workspace_id) not in roles:
                rows[0]["cd_config"]["environments_common"]["git_repositry"]["password"] = common.str_mask(rows[0]["ci_config"]["pipelines_common"]["git_repositry"]["password"])
                rows[0]["cd_config"]["environments_common"]["git_repositry"]["token"] = common.str_mask(rows[0]["ci_config"]["pipelines_common"]["git_repositry"]["token"])
                for env_idx, environment in enumerate(rows[0]["cd_config"]["environments"]):
                    rows[0]["cd_config"]["environments"][env_idx]["deploy_destination"]["authentication_token"] = common.str_mask(environment["deploy_destination"]["authentication_token"])
                    rows[0]["cd_config"]["environments"][env_idx]["deploy_destination"]["base64_encoded_certificate"] = common.str_mask(environment["deploy_destination"]["base64_encoded_certificate"])


        elif response.status_code == 404:
            # 情報が取得できない場合は、0件で返す
            rows = []
            ret_status = response.status_code
        else:
            if response.status_code == 500 and common.is_json_format(response.text):
                # 戻り値がJsonの場合は、値を取得
                ret = json.loads(response.text)
                # 詳細エラーがある場合は詳細を設定
                if ret["errorDetail"] is not None:
                    error_detail = ret["errorDetail"]

            raise common.UserException("{} Error get workspace db status:{}".format(inspect.currentframe().f_code.co_name, response.status_code))

        return jsonify({"result": ret_status, "rows": rows}), ret_status

    except common.UserException as e:
        return common.server_error_to_message(e, app_name + exec_stat, error_detail)
    except Exception as e:
        return common.server_error_to_message(e, app_name + exec_stat, error_detail)

def put_workspace(workspace_id):
    """ワークスペース情報更新

    Args:
        workspace_id (int): workspace ID

    Returns:
        Response: HTTP Respose
    """

    app_name = multi_lang.get_text("EP020-0003", "ワークスペース情報:")
    exec_stat = multi_lang.get_text("EP020-0016", "更新")
    error_detail = ""
    return_code = 500

    try:

        globals.logger.debug('#' * 50)
        globals.logger.debug('CALL {}'.format(inspect.currentframe().f_code.co_name))
        globals.logger.debug('#' * 50)

        # ヘッダ情報 header info.
        post_headers = {
            'Content-Type': 'application/json',
        }

        # 引数を一旦更新項目として仮保存する Temporarily save the argument as an update item
        req_data = request.json.copy()

        # 変更前のworkspace取得 Get workspace before change
        api_url = "{}://{}:{}/workspace/{}".format(os.environ['EPOCH_RS_WORKSPACE_PROTOCOL'],
                                                    os.environ['EPOCH_RS_WORKSPACE_HOST'],
                                                    os.environ['EPOCH_RS_WORKSPACE_PORT'],
                                                    workspace_id)
        response = requests.get(api_url)

        # 正常以外はエラーを返す Returns an error if not normal
        if response.status_code != 200:
            if common.is_json_format(response.text):
                ret = json.loads(response.text)
                # 詳細エラーがある場合は詳細を設定
                if ret["errorDetail"] is not None:
                    error_detail = ret["errorDetail"]
            raise common.UserException("{} Error put workspace db status:{}".format(inspect.currentframe().f_code.co_name, response.status_code))

        rows = json.loads(response.text)
        row = rows["rows"][0]

        # 現在のユーザーのロール値を取得 Get the role value of the current user
        user = api_service_current.user_get()
        globals.logger.debug(f'cuurent user:{user}')
        roles = user["composite_roles"]

        # 取得した情報をもとに、画面から送信された更新情報を権限毎に設定する
        # Based on the acquired information, set the update information sent from the screen for each authority.

        # 更新日は無条件に画面に表示された内容を設定
        # Set the update date unconditionally the content displayed on the screen
        row["update_at"] = req_data["update_at"]

        #
        # ワークスペース更新(名称)有の場合 If workspace update (name) is available
        #
        if const.ROLE_WS_ROLE_WS_NAME_UPDATE[0].format(workspace_id) in roles:
            row["common"] = req_data["common"]

        #
        # ワークスペース更新 (CI)有の場合 If workspace update (ci) is available
        #
        if const.ROLE_WS_ROLE_WS_CI_UPDATE[0].format(workspace_id) in roles:
            row["ci_config"]["pipelines_common"] = req_data["ci_config"]["pipelines_common"]
            row["ci_config"]["pipelines"] = req_data["ci_config"]["pipelines"]

        #
        # Manifestパラメータの更新 - Update Manifest parameters
        #
        if const.ROLE_WS_ROLE_MANIFEST_SETTING[0].format(workspace_id) in roles:
            # Manifestパラメータの更新権限がある場合はパラメータの内容を差し替える
            # If you have permission to update Manifest parameters, replace the contents of the parameters.
            row["ci_config"]["environments"] = req_data["ci_config"]["environments"]

        elif const.ROLE_WS_ROLE_WS_CD_UPDATE[0].format(workspace_id) in roles:
            # マニフェスト更新権限が無くてワークスペース更新 (CD)有の場合、環境の増減だけ行う
            # If you do not have the manifest update authority and have a workspace update (CD), only increase or decrease the environment.

            save_env = []
            # 元からあるものは一旦消去し、環境内容はIDが一致すれば元のまま、該当しない場合は新規とする
            # Delete the original one, leave the environment contents as they are if the IDs match, and make them new if they do not match.
            for src_env in row["ci_config"]["environments"]:
                # IDが存在するかチェック Check if the ID exists
                if common.search_array_dict(req_data["ci_config"]["environments"], "environment_id", src_env["environment_id"]) is not None:
                    save_env.append(src_env)

            for dest_env in req_data["ci_config"]["environments"]:
                # IDが存在するかチェック Check if the ID exists
                # 存在しない場合は情報を追加する Add information if it does not exist
                if common.search_array_dict(row["ci_config"]["environments"], "environment_id", dest_env["environment_id"]) is None:
                    save_env.append(dest_env)

            row["ci_config"]["environments"] = save_env

        #
        # CD設定の更新 - Update CD settings
        #

        # IaCリポジトリのユーザ,tokenを決定する - Determine user, token of IaC repository
        if req_data["cd_config"]["environments_common"]["git_repositry"]["account_select"] == "applicationCode":
            # アプリケーションコードと同じ - Same as application code
            iac_git_user = row["ci_config"]["pipelines_common"]["git_repositry"]["user"]
            iac_git_token = row["ci_config"]["pipelines_common"]["git_repositry"]["token"]
        else:
            # 別途入力の時は入力値を使う - Use the input value when inputting separately
            iac_git_user = req_data["cd_config"]["environments_common"]["git_repositry"]["user"]
            iac_git_token = req_data["cd_config"]["environments_common"]["git_repositry"]["token"]

        if const.ROLE_WS_ROLE_WS_CD_UPDATE[0].format(workspace_id) in roles and const.ROLE_WS_ROLE_MEMBER_ROLE_UPDATE[0].format(workspace_id) in roles:
            # ワークスペース更新(CD)の権限とメンバー更新の権限がある場合は全項目更新
            # Update all items if you have workspace update (CD) permission and member update permission
            row["cd_config"] = req_data["cd_config"]

            row["cd_config"]["environments_common"]["git_repositry"]["user"] = iac_git_user
            row["cd_config"]["environments_common"]["git_repositry"]["password"] = iac_git_token
            row["cd_config"]["environments_common"]["git_repositry"]["token"] = iac_git_token

        elif const.ROLE_WS_ROLE_WS_CD_UPDATE[0].format(workspace_id) in roles:
            # ワークスペース更新(CD)の権限がありメンバー更新の権限がない場合はDeploy権限の項目以外の項目を更新
            # If you have workspace update (CD) permission and you do not have member update permission, update items other than Deploy permission items.

            # 共通部分の更新 - Update of common parts
            row["cd_config"]["system_config"] = req_data["cd_config"]["system_config"]
            row["cd_config"]["environments_common"] = req_data["cd_config"]["environments_common"]

            row["cd_config"]["environments_common"]["git_repositry"]["user"] = iac_git_user
            row["cd_config"]["environments_common"]["git_repositry"]["password"] = iac_git_token
            row["cd_config"]["environments_common"]["git_repositry"]["token"] = iac_git_token

            # 環境毎の項目の更新 - Update items for each environment
            environments_new =[]

            for env_before in row["cd_config"]["environments"]:
                # 更新となる環境情報を取得する - Get updated environment information
                env_new = common.search_array_dict(req_data["cd_config"]["environments"], "environment_id", env_before["environment_id"])

                if env_new is not None:
                    # deploy_member以外の項目は更新する - Update items other than deploy_member
                    env_new = env_new.copy()
                    env_new["cd_exec_users"] = env_before["cd_exec_users"]
                    environments_new.append(env_new)
                else:
                    # 環境が削除された場合は設定しない（消える）
                    # Not set (disappears) when the environment is deleted
                    pass

            for env in req_data["cd_config"]["environments"]:
                if common.search_array_dict(row["cd_config"]["environments"], "environment_id", env["environment_id"]) is None:
                    # 新規の環境の場合、deploy_member以外の項目を設定し、deploy_memberはデフォルト値に設定
                    # For new environment, set items other than deploy_member and set deploy_member to default value
                    env_new = env.copy()
                    env_new["cd_exec_users"] = {"user_select":"all", "user_id": ""}
                    environments_new.append(env_new)

            row["cd_config"]["environments"] = environments_new

        elif const.ROLE_WS_ROLE_MEMBER_ROLE_UPDATE[0].format(workspace_id) in roles:
            # ワークスペース更新(CD)の権限がなくメンバー更新の権限がある場合はDeploy権限の項目だけを更新
            # If you do not have workspace update (CD) permission and you have member update permission, update only the item of Deploy permission.

            for env in row["cd_config"]["environments"]:
                env_new = common.search_array_dict(req_data["cd_config"]["environments"], "environment_id", env["environment_id"])
                env["cd_exec_users"] = env_new["cd_exec_users"]

        else:
            # ワークスペース更新(CD)の権限とメンバー更新の権限がない場合は更新しない
            # Do not update if you do not have workspace update (CD) and member update permissions
            pass

        post_data = row

        # workspace put送信
        api_url = "{}://{}:{}/workspace/{}".format(os.environ['EPOCH_RS_WORKSPACE_PROTOCOL'],
                                                    os.environ['EPOCH_RS_WORKSPACE_HOST'],
                                                    os.environ['EPOCH_RS_WORKSPACE_PORT'],
                                                    workspace_id)
        response = requests.put(api_url, headers=post_headers, data=json.dumps(post_data))

        if response.status_code == 200:
            # 正常時は戻り値がレコードの値なのでそのまま返却する
            ret = json.loads(response.text)
            rows = ret['rows']
        elif response.status_code == 404:
            return_code = 400
            error_detail = multi_lang.get_text("EP000-0023", "対象の情報(workspace)が他で更新されたため、更新できません\n画面更新後、再度情報を入力・選択して実行してください", "workspace")
            raise common.UserException("{} Exclusive check error".format(inspect.currentframe().f_code.co_name))
        else:
            if common.is_json_format(response.text):
                ret = json.loads(response.text)
                # 詳細エラーがある場合は詳細を設定
                if ret["errorDetail"] is not None:
                    error_detail = ret["errorDetail"]

            raise common.UserException("{} Error put workspace db status:{}".format(inspect.currentframe().f_code.co_name, response.status_code))

        # workspace 状態取得 workspace status get
        api_url = "{}://{}:{}/workspace/{}/status".format(os.environ['EPOCH_RS_WORKSPACE_PROTOCOL'],
                                                            os.environ['EPOCH_RS_WORKSPACE_HOST'],
                                                            os.environ['EPOCH_RS_WORKSPACE_PORT'],
                                                            workspace_id)

        response = requests.get(api_url)

        if response.status_code == 200:
            # 取得したワークスペース状態を退避 Save the acquired workspace status
            get_workspace_status = json.loads(response.text)
            # 更新で使用する項目のみを展開する Expand only the items used in the update
            workspace_status = {
                const.STATUS_INITIALIZE : const.STATUS_OK
            }
        else:
            # 存在しない場合は、初期設定する If it does not exist, initialize it
            workspace_status = const.WORKSPACE_STATUS
            workspace_status[const.STATUS_INITIALIZE] = const.STATUS_OK

        # 状態が無ければ初回登録する
        if response.status_code == 404:
            # workspace 状態登録 workspace status registration
            api_url = "{}://{}:{}/workspace/{}/status".format(os.environ['EPOCH_RS_WORKSPACE_PROTOCOL'],
                                                                os.environ['EPOCH_RS_WORKSPACE_HOST'],
                                                                os.environ['EPOCH_RS_WORKSPACE_PORT'],
                                                                workspace_id)

            response = requests.post(api_url, headers=post_headers, data=json.dumps(workspace_status))

            if response.status_code != 200:
                raise common.UserException("{} Error post workspace status db status:{}".format(inspect.currentframe().f_code.co_name, response.status_code))
        else:
            # workspace 状態更新 workspace status update
            api_url = "{}://{}:{}/workspace/{}/status".format(os.environ['EPOCH_RS_WORKSPACE_PROTOCOL'],
                                                                os.environ['EPOCH_RS_WORKSPACE_HOST'],
                                                                os.environ['EPOCH_RS_WORKSPACE_PORT'],
                                                                workspace_id)

            response = requests.put(api_url, headers=post_headers, data=json.dumps(workspace_status))

            if response.status_code != 200:
                raise common.UserException("{} Error put workspace status db status:{}".format(inspect.currentframe().f_code.co_name, response.status_code))

        ret_status = 200

        # 戻り値をそのまま返却
        return jsonify({"result": ret_status}), ret_status

    except common.UserException as e:
        return common.user_error_to_message(e, app_name + exec_stat, error_detail, return_code)
    except Exception as e:
        return common.server_error_to_message(e, app_name + exec_stat, error_detail)


def patch_workspace(workspace_id):
    """ワークスペース情報一部更新 workspace info. pacth

    Args:
        workspace_id (int): workspace ID

    Returns:
        Response: HTTP Respose
    """

    app_name = multi_lang.get_text("EP020-0003", "ワークスペース情報:")
    exec_stat = multi_lang.get_text("EP020-0016", "更新")
    error_detail = ""

    try:
        globals.logger.debug('#' * 50)
        globals.logger.debug('CALL {}'.format(inspect.currentframe().f_code.co_name))
        globals.logger.debug('#' * 50)

        # ヘッダ情報
        post_headers = {
            'Content-Type': 'application/json',
        }

        # 引数をJSON形式で受け取りそのまま引数に設定
        post_data = request.json.copy()

        # workspace patch send
        api_url = "{}://{}:{}/workspace/{}".format(os.environ['EPOCH_RS_WORKSPACE_PROTOCOL'],
                                                    os.environ['EPOCH_RS_WORKSPACE_HOST'],
                                                    os.environ['EPOCH_RS_WORKSPACE_PORT'],
                                                    workspace_id)
        response = requests.patch(api_url, headers=post_headers, data=json.dumps(post_data))

        if response.status_code == 200:
            # 正常時は戻り値がレコードの値なのでそのまま返却する
            ret = json.loads(response.text)
            rows = ret['rows']
        else:
            if common.is_json_format(response.text):
                ret = json.loads(response.text)
                # 詳細エラーがある場合は詳細を設定
                if ret["errorDetail"] is not None:
                    error_detail = ret["errorDetail"]

            raise common.UserException("{} Error put workspace db status:{}".format(inspect.currentframe().f_code.co_name, response.status_code))

        ret_status = response.status_code

        # 戻り値をそのまま返却
        return jsonify({"result": ret_status}), ret_status

    except common.UserException as e:
        return common.server_error_to_message(e, app_name + exec_stat, error_detail)
    except Exception as e:
        return common.server_error_to_message(e, app_name + exec_stat, error_detail)


def post_pod(workspace_id):
    """ワークスペース作成

    Args:
        workspace_id (int): workspace ID

    Returns:
        Response: HTTP Respose
    """

    app_name = "ワークスペース情報:"
    exec_stat = "作成"
    error_detail = ""

    try:
        globals.logger.debug('#' * 50)
        globals.logger.debug('CALL {}'.format(inspect.currentframe().f_code.co_name))
        globals.logger.debug('#' * 50)

        # ヘッダ情報 header info
        post_headers = {
            'Content-Type': 'application/json',
        }

        # # 引数をJSON形式で受け取りそのまま引数に設定
        # post_data = request.json.copy()

        # workspace get
        api_url = "{}://{}:{}/workspace/{}".format(os.environ['EPOCH_RS_WORKSPACE_PROTOCOL'],
                                                    os.environ['EPOCH_RS_WORKSPACE_HOST'],
                                                    os.environ['EPOCH_RS_WORKSPACE_PORT'],
                                                    workspace_id)
        response = requests.get(api_url)

        if response.status_code != 200:
            error_detail = multi_lang.get_test("EP020-0013", "ワークスペース情報の取得に失敗しました")
            globals.logger.debug(error_detail)
            raise common.UserException(error_detail)

        # 取得したワークスペース情報を退避 Save the acquired workspace information
        ret = json.loads(response.text)
        # 取得したworkspace情報をパラメータとして受け渡す Pass the acquired workspace information as a parameter
        post_data = ret["rows"][0]

        # 実行前はNGで更新 Update with NG before execution
        workspace_status = {
            const.STATUS_POD : const.STATUS_NG
        }

        # workspace 状態更新 workspace status update
        api_url = "{}://{}:{}/workspace/{}/status".format(os.environ['EPOCH_RS_WORKSPACE_PROTOCOL'],
                                                            os.environ['EPOCH_RS_WORKSPACE_HOST'],
                                                            os.environ['EPOCH_RS_WORKSPACE_PORT'],
                                                            workspace_id)

        response = requests.put(api_url, headers=post_headers, data=json.dumps(workspace_status))

        if response.status_code != 200:
            error_detail = multi_lang.get_test("EP020-0027", "ワークスペース状態情報の更新に失敗しました")
            globals.logger.debug(error_detail)
            raise common.UserException(error_detail)

        # workspace post送信
        api_url = "{}://{}:{}/workspace/{}".format(os.environ['EPOCH_CONTROL_WORKSPACE_PROTOCOL'],
                                                    os.environ['EPOCH_CONTROL_WORKSPACE_HOST'],
                                                    os.environ['EPOCH_CONTROL_WORKSPACE_PORT'],
                                                    workspace_id)
        response = requests.post(api_url, headers=post_headers, data=json.dumps(post_data))
        globals.logger.debug("post workspace response:{}".format(response.text))

        if response.status_code != 200:
            error_detail = 'workspace post処理に失敗しました'
            globals.logger.debug(error_detail)
            raise common.UserException(error_detail)

        # argocd post送信
        api_url = "{}://{}:{}/workspace/{}/argocd".format(os.environ['EPOCH_CONTROL_ARGOCD_PROTOCOL'],
                                                            os.environ['EPOCH_CONTROL_ARGOCD_HOST'],
                                                            os.environ['EPOCH_CONTROL_ARGOCD_PORT'],
                                                            workspace_id)
        response = requests.post(api_url, headers=post_headers, data=json.dumps(post_data))
        globals.logger.debug("post argocd response:{}".format(response.text))

        if response.status_code != 200:
            error_detail = 'argocd post処理に失敗しました'
            globals.logger.debug(error_detail)
            raise common.UserException(error_detail)

        # ita post送信
        api_url = "{}://{}:{}/workspace/{}/it-automation".format(os.environ['EPOCH_CONTROL_ITA_PROTOCOL'],
                                                                    os.environ['EPOCH_CONTROL_ITA_HOST'],
                                                                    os.environ['EPOCH_CONTROL_ITA_PORT'],
                                                                    workspace_id)
        response = requests.post(api_url, headers=post_headers, data=json.dumps(post_data))
        globals.logger.debug("post it-automation response:{}".format(response.text))

        if response.status_code != 200:
            error_detail = 'it-automation post処理に失敗しました'
            raise common.UserException(error_detail)

        # epoch-control-ita-api の呼び先設定
        api_url = "{}://{}:{}/workspace/{}/it-automation/settings".format(os.environ['EPOCH_CONTROL_ITA_PROTOCOL'],
                                                                            os.environ['EPOCH_CONTROL_ITA_HOST'],
                                                                            os.environ['EPOCH_CONTROL_ITA_PORT'],
                                                                            workspace_id)

        # it-automation/settings post送信
        response = requests.post(api_url, headers=post_headers, data=json.dumps(post_data))
        globals.logger.debug("post it-automation/settings response:{}".format(response.text))

        if response.status_code != 200:
            error_detail = 'it-automation/settings post処理に失敗しました'
            raise common.UserException(error_detail)

        # 実行後はOKで更新 Update with OK after execution
        workspace_status[const.STATUS_POD] = const.STATUS_OK
        # workspace 状態更新 workspace status update
        api_url = "{}://{}:{}/workspace/{}/status".format(os.environ['EPOCH_RS_WORKSPACE_PROTOCOL'],
                                                            os.environ['EPOCH_RS_WORKSPACE_HOST'],
                                                            os.environ['EPOCH_RS_WORKSPACE_PORT'],
                                                            workspace_id)

        response = requests.put(api_url, headers=post_headers, data=json.dumps(workspace_status))

        if response.status_code != 200:
            error_detail = multi_lang.get_test("EP020-0027", "ワークスペース状態情報の更新に失敗しました")
            globals.logger.debug(error_detail)
            raise common.UserException(error_detail)

        ret_status = 200

        # 戻り値をそのまま返却
        return jsonify({"result": ret_status}), ret_status

    except common.UserException as e:
        return common.server_error_to_message(e, app_name + exec_stat, error_detail)
    except Exception as e:
        return common.server_error_to_message(e, app_name + exec_stat, error_detail)
