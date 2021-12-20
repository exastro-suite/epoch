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
import api_service_ci
import api_service_manifest
import api_service_cd

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
        create_workspace_setting_auth_infra(workspace_id)

        ret_status = response.status_code

        # 戻り値をそのまま返却        
        return jsonify({"result": ret_status, "rows": rows}), ret_status

    except common.UserException as e:
        return common.server_error_to_message(e, app_name + exec_stat, error_detail)
    except Exception as e:
        return common.server_error_to_message(e, app_name + exec_stat, error_detail)


def create_workspace_setting_roles(workspace_id,user_id):
    """Set workspace roles - ワークスペースのロールを設定する

    Args:
        workspace_id (int): workspace id
        user_id (str): login user id
    """

    # ヘッダ情報 post header
    post_headers = {
        'Content-Type': 'application/json',
    }

    api_url = "{}://{}:{}/{}/client/epoch-system/role".format(os.environ['EPOCH_EPAI_API_PROTOCOL'],
                                                            os.environ['EPOCH_EPAI_API_HOST'],
                                                            os.environ['EPOCH_EPAI_API_PORT'],
                                                            os.environ["EPOCH_EPAI_REALM_NAME"]
                                                    )

    post_data = {
        "roles" : [
            # ロール権限をすべて定義 Define all role permissions
            {
                "name": const.ROLE_WS_ROLE_WS_REFERENCE.format(workspace_id),
                "composite_roles": [],
            },
            {
                "name": const.ROLE_WS_ROLE_WS_NAME_UPDATE.format(workspace_id),
                "composite_roles": [],
            },
            {
                "name": const.ROLE_WS_ROLE_WS_CI_UPDATE.format(workspace_id),
                "composite_roles": [],
            },
            {
                "name": const.ROLE_WS_ROLE_WS_CD_UPDATE.format(workspace_id),
                "composite_roles": [],
            },
            {
                "name": const.ROLE_WS_ROLE_WS_DELETE.format(workspace_id),
                "composite_roles": [],
            },
            {
                "name": const.ROLE_WS_ROLE_OWNER_ROLE_SETTING.format(workspace_id),
                "composite_roles": [],
            },
            {
                "name": const.ROLE_WS_ROLE_MEMBER_ADD.format(workspace_id),
                "composite_roles": [],
            },
            {
                "name": const.ROLE_WS_ROLE_MEMBER_ROLE_UPDATE.format(workspace_id),
                "composite_roles": [],
            },
            {
                "name": const.ROLE_WS_ROLE_CI_PIPELINE_RESULT.format(workspace_id),
                "composite_roles": [],
            },
            {
                "name": const.ROLE_WS_ROLE_MANIFEST_SETTING.format(workspace_id),
                "composite_roles": [],
            },
            {
                "name": const.ROLE_WS_ROLE_CD_EXECUTE.format(workspace_id),
                "composite_roles": [],
            },
            {
                "name": const.ROLE_WS_ROLE_CD_EXECUTE_RESULT.format(workspace_id),
                "composite_roles": [],
            },
            # ロールをすべて定義 Define all roles
            {
                "name": const.ROLE_WS_OWNER.format(workspace_id),
                "composite_roles": [ const.ROLE_WS_ROLE_WS_REFERENCE.format(workspace_id),
                                    const.ROLE_WS_ROLE_WS_NAME_UPDATE.format(workspace_id),
                                    const.ROLE_WS_ROLE_WS_CI_UPDATE.format(workspace_id),
                                    const.ROLE_WS_ROLE_WS_CD_UPDATE.format(workspace_id),
                                    const.ROLE_WS_ROLE_WS_DELETE.format(workspace_id),
                                    const.ROLE_WS_ROLE_OWNER_ROLE_SETTING.format(workspace_id),
                                    const.ROLE_WS_ROLE_MEMBER_ADD.format(workspace_id),
                                    const.ROLE_WS_ROLE_MEMBER_ROLE_UPDATE.format(workspace_id),
                                    const.ROLE_WS_ROLE_CI_PIPELINE_RESULT.format(workspace_id),
                                    const.ROLE_WS_ROLE_MANIFEST_SETTING.format(workspace_id),
                                    const.ROLE_WS_ROLE_CD_EXECUTE.format(workspace_id),
                                    const.ROLE_WS_ROLE_CD_EXECUTE_RESULT.format(workspace_id),
                ]
            }
        ]
    }
    
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
                "name": const.ROLE_WS_OWNER.format(workspace_id),
                "enabled": True,
            }
        ]
    }

    response = requests.post(api_url, headers=post_headers, data=json.dumps(post_data))

def create_workspace_setting_auth_infra(workspace_id):
    """exastro-authentication-infra setting - 認証基盤の設定

    Args:
        workspace_id (int): workspace id
    """

    #
    # TODO:スタブ実装
    #

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

    # postする情報 post information
    clients = [
        {
            "client_id" :   'epoch-ws-{}-ita'.format(workspace_id),
            "client_host" : os.environ["EPOCH_EPAI_HOST"],
            "client_protocol" : "https",
            "conf_template" : "epoch-ws-ita-template.conf",
            "backend_url" : "http://it-automation.{}.svc:8084/".format(namespace),
        },
        {
            "client_id" :   'epoch-ws-{}-argocd'.format(workspace_id),
            "client_host" : os.environ["EPOCH_EPAI_HOST"],
            "client_protocol" : "https",
            "conf_template" : "epoch-ws-argocd-template.conf",
            "backend_url" : "https://argocd-server.{}.svc/".format(namespace),
        },
        {
            "client_id" :   'epoch-ws-{}-sonarqube'.format(workspace_id),
            "client_host" : os.environ["EPOCH_EPAI_HOST"],
            "client_protocol" : "https",
            "conf_template" : "epoch-ws-sonarqube-template.conf",
            "backend_url" : "http://sonarqube.{}.svc:9000/".format(pipeline_name),
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


    exec_stat = "認証基盤 設定読み込み"

    # workspace_id send data
    apply_data = {
        "workspace_id": workspace_id,
    }
    response = requests.put("{}{}".format(api_url_epai, 'apply_settings'), headers=post_headers, data=json.dumps(apply_data))


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

        # ヘッダ情報
        post_headers = {
            'Content-Type': 'application/json',
        }

        # ワークスペース情報取得
        api_url = "{}://{}:{}/workspace".format(os.environ['EPOCH_RS_WORKSPACE_PROTOCOL'],
                                                os.environ['EPOCH_RS_WORKSPACE_HOST'],
                                                os.environ['EPOCH_RS_WORKSPACE_PORT'])
        response = requests.get(api_url + '', headers=post_headers)

        rows = []
        if response.status_code == 200 and common.is_json_format(response.text):
            # 取得した情報で必要な部分のみを編集して返却する
            ret = json.loads(response.text)
            for data_row in ret["rows"]:
                row = {
                    "workspace_id": data_row["workspace_id"],
                    "workspace_name": data_row["common"]["name"],
                    "workspace_remarks": data_row["common"]["note"],
                    "update_at": data_row["update_at"],
                }
                rows.append(row)

        elif not response.status_code == 404:
            # 404以外の場合は、エラー、404はレコードなしで返却（エラーにはならない）
            raise Exception('{} Error:{}'.format(inspect.currentframe().f_code.co_name, response.status_code))

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

    app_name = "ワークスペース情報:"
    exec_stat = "更新"
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

        # ヘッダ情報
        post_headers = {
            'Content-Type': 'application/json',
        }

        # 引数をJSON形式で受け取りそのまま引数に設定
        post_data = request.json.copy()

        # workspace post送信
        api_url = "{}://{}:{}/workspace/{}".format(os.environ['EPOCH_CONTROL_WORKSPACE_PROTOCOL'],
                                                   os.environ['EPOCH_CONTROL_WORKSPACE_HOST'],
                                                   os.environ['EPOCH_CONTROL_WORKSPACE_PORT'],
                                                   workspace_id)
        response = requests.post(api_url, headers=post_headers, data=json.dumps(post_data))
        globals.logger.debug("post workspace response:{}".format(response.text))
        
        if response.status_code != 200:
            error_detail = 'workspace post処理に失敗しました'
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

        ret_status = 200

        # 戻り値をそのまま返却        
        return jsonify({"result": ret_status}), ret_status

    except common.UserException as e:
        return common.server_error_to_message(e, app_name + exec_stat, error_detail)
    except Exception as e:
        return common.server_error_to_message(e, app_name + exec_stat, error_detail)


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('API_SERVICE_PORT', '8000')), threaded=True)
