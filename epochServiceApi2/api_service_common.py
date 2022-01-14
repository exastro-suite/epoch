#   Copyright 2022 NEC Corporation
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

def get_workspace_members_by_role(workspace_id, pickup_roles):
    """指定ロール保有ワークスペースメンバー取得 Acquisition of workspace members with designated roles

    Args:
        workspace_id (int): workspace id
        pickup_roles (array str): roles array

    Returns:
        Response: HTTP Respose
    """

    try:
        globals.logger.debug('=' * 50)
        globals.logger.debug('CALL {}'.format(inspect.currentframe().f_code.co_name))
        globals.logger.debug('=' * 50)

        # 子のROLEからでは、もちえているユーザーの取得ができないのですべての親ロールから該当する情報を抜き出していく
        # Since it is not possible to acquire the user who has it from the child ROLE, the relevant information is extracted from all the parent roles.
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

                # 取得したすべてのロールから絞り込む Narrow down from all acquired roles
                for get_role in ret_roles["rows"]:
                    # 該当するロールが一致したら値を設定 Set the value when the corresponding role matches
                    if get_role["name"] in pickup_roles:
                        ret_user = {
                            "user_id": user["user_id"],
                            "username": user["user_name"],
                        }
                        ret_users.append(ret_user)
                        stock_user_id.append(user["user_id"])

        globals.logger.debug(f"users:{ret_users}")

        return ret_users

    except common.UserException as e:
        globals.logger.error(e.args)
        raise
    except Exception as e:
        globals.logger.error(e.args)
        raise
