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
import hashlib

import globals
import common
import multi_lang
import api_access_info

# 設定ファイル読み込み・globals初期化 flask setting file read and globals initialize
app = Flask(__name__)
app.config.from_envvar('CONFIG_API_ITA_PATH')
globals.init(app)

EPOCH_ITA_HOST = "it-automation"
EPOCH_ITA_PORT = "8084"

# メニューID
ite_menu_operation = '2100000304'
ite_menu_conductor_exec = '2100180004'
ite_menu_conductor_result = '2100180005'
ite_menu_conductor_conductor_result = '2100180005'

def get_cd_operations(workspace_id):
    """get cd-operations list

    Returns:
        Response: HTTP Respose
    """

    app_name = "ワークスペース情報:"
    exec_stat = "Operation情報取得"
    error_detail = ""

    try:
        globals.logger.debug('#' * 50)
        globals.logger.debug('CALL {}'.format(inspect.currentframe().f_code.co_name))
        globals.logger.debug('#' * 50)

        # ワークスペースアクセス情報取得
        access_info = api_access_info.get_access_info(workspace_id)

        # namespaceの取得
        namespace = common.get_namespace_name(workspace_id)

        ita_restapi_endpoint = "http://{}.{}.svc:{}/default/menu/07_rest_api_ver1.php".format(EPOCH_ITA_HOST, namespace, EPOCH_ITA_PORT)
        ita_user = access_info['ITA_USER']
        ita_pass = access_info['ITA_PASSWORD']

        # HTTPヘッダの生成
        filter_headers = {
            'host': EPOCH_ITA_HOST + ':' + EPOCH_ITA_PORT,
            'Content-Type': 'application/json',
            'Authorization': base64.b64encode((ita_user + ':' + ita_pass).encode()),
            'X-Command': 'FILTER',
        }

        #
        # オペレーションの取得
        #
        opelist_resp = requests.post(ita_restapi_endpoint + '?no=' + ite_menu_operation, headers=filter_headers)
        globals.logger.debug('---- Operation ----')
        globals.logger.debug(opelist_resp.text)
        if common.is_json_format(opelist_resp.text):
            opelist_json = json.loads(opelist_resp.text)
        else:
            error_detail = "Operation情報取得失敗"
            raise common.UserException(error_detail)

        rows = opelist_json

        # 正常終了
        ret_status = 200

        # 戻り値をそのまま返却        
        return jsonify({"result": ret_status, "rows": rows}), ret_status

    except common.UserException as e:
        return common.server_error_to_message(e, app_name + exec_stat, error_detail)
    except Exception as e:
        return common.server_error_to_message(e, app_name + exec_stat, error_detail)


def cd_execute(workspace_id):
    """cd execute

    Returns:
        Response: HTTP Respose
    """

    app_name = "ワークスペース情報:"
    exec_stat = "CD実行"
    error_detail = ""

    try:
        globals.logger.debug('#' * 50)
        globals.logger.debug('CALL {}'.format(inspect.currentframe().f_code.co_name))
        globals.logger.debug('#' * 50)

        # パラメータ情報(JSON形式) prameter save
        payload = request.json.copy()

        # ワークスペースアクセス情報取得 get workspace access info.
        access_info = api_access_info.get_access_info(workspace_id)

        # namespaceの取得 get namespace 
        namespace = common.get_namespace_name(workspace_id)

        ita_restapi_endpoint = "http://{}.{}.svc:{}/default/menu/07_rest_api_ver1.php".format(EPOCH_ITA_HOST, namespace, EPOCH_ITA_PORT)
        ita_user = access_info['ITA_USER']
        ita_pass = access_info['ITA_PASSWORD']

        operation_id = payload["operation_id"]
        conductor_class_no = payload["conductor_class_no"]
        preserve_datetime = payload["preserve_datetime"]

        # POST送信する
        # HTTPヘッダの生成
        filter_headers = {
            'host': EPOCH_ITA_HOST + ':' + EPOCH_ITA_PORT,
            'Content-Type': 'application/json',
            'Authorization': base64.b64encode((ita_user + ':' + ita_pass).encode()),
            'X-Command': 'EXECUTE',
        }

        # 実行パラメータ設定
        data = {
            "CONDUCTOR_CLASS_NO": conductor_class_no,
            "OPERATION_ID": operation_id,
            "PRESERVE_DATETIME": preserve_datetime,
        }

        # json文字列に変換（"utf-8"形式に自動エンコードされる）
        json_data = json.dumps(data)

        # リクエスト送信
        exec_response = requests.post(ita_restapi_endpoint + '?no=' + ite_menu_conductor_exec, headers=filter_headers, data=json_data)

        if exec_response.status_code != 200:
            globals.logger.error(exec_response.text)
            error_detail = multi_lang.get_text("EP034-0001", "CD実行の呼び出しに失敗しました status:{0}".format(exec_response.status_code), exec_response.status_code)
            raise common.UserException(error_detail)

        globals.logger.debug("-------------------------")
        globals.logger.debug("response:")
        globals.logger.debug(exec_response.text)
        globals.logger.debug("-------------------------")

        resp_data = json.loads(exec_response.text)
        if resp_data["status"] != "SUCCEED":
            globals.logger.error("no={} status:{}".format(ite_menu_conductor_exec, resp_data["status"]))
            error_detail = multi_lang.get_text("EP034-0002", "CD実行の呼び出しに失敗しました ita-status:{0} resultdata:{1}".format(eresp_data["status"], eresp_data["resultdata"]), eresp_data["status"], eresp_data["resultdata"])
            raise common.UserException(error_detail)

        # 作業IDを退避
        cd_result_id = resp_data["resultdata"]["CONDUCTOR_INSTANCE_ID"]

        # 正常終了
        ret_status = 200

        # 戻り値をそのまま返却        
        return jsonify({"result": ret_status, "cd_result_id": cd_result_id}), ret_status

    except common.UserException as e:
        return common.server_error_to_message(e, app_name + exec_stat, error_detail)
    except Exception as e:
        return common.server_error_to_message(e, app_name + exec_stat, error_detail)


def cd_execute_cancel(workspace_id, conductor_id):
    """CD実行取り消し cd execute cancel

    Args:
        workspace_id (int): workspace id
        conductor_id (str): conductor id

    Returns:
        Response: HTTP Respose
    """

    try:
        globals.logger.debug('#' * 50)
        globals.logger.debug('CALL {}'.format(inspect.currentframe().f_code.co_name))
        globals.logger.debug('#' * 50)

        # ワークスペースアクセス情報取得 get workspace access info.
        access_info = api_access_info.get_access_info(workspace_id)

        # namespaceの取得 get namespace 
        namespace = common.get_namespace_name(workspace_id)

        ita_restapi_endpoint = "http://{}.{}.svc:{}/default/menu/07_rest_api_ver1.php".format(EPOCH_ITA_HOST, namespace, EPOCH_ITA_PORT)
        ita_user = access_info['ITA_USER']
        ita_pass = access_info['ITA_PASSWORD']

        # POST送信する
        # HTTPヘッダの生成
        filter_headers = {
            'host': EPOCH_ITA_HOST + ':' + EPOCH_ITA_PORT,
            'Content-Type': 'application/json',
            'Authorization': base64.b64encode((ita_user + ':' + ita_pass).encode()),
            'X-Command': 'EXECUTE',
        }

        # # 実行パラメータ設定
        # data = {
        #     "CONDUCTOR_CLASS_NO": conductor_class_no,
        #     "OPERATION_ID": operation_id,
        #     "PRESERVE_DATETIME": preserve_datetime,
        # }

        # # json文字列に変換（"utf-8"形式に自動エンコードされる）
        # json_data = json.dumps(data)

        # # リクエスト送信
        # exec_response = requests.post(ita_restapi_endpoint + '?no=' + ite_menu_conductor_exec, headers=filter_headers, data=json_data)

        # if exec_response.status_code != 200:
        #     globals.logger.error(exec_response.text)
        #     error_detail = multi_lang.get_text("EP034-0001", "CD実行の呼び出しに失敗しました status:{0}".format(exec_response.status_code), exec_response.status_code)
        #     raise common.UserException(error_detail)

        # globals.logger.debug("-------------------------")
        # globals.logger.debug("response:")
        # globals.logger.debug(exec_response.text)
        # globals.logger.debug("-------------------------")

        # resp_data = json.loads(exec_response.text)
        # if resp_data["status"] != "SUCCEED":
        #     globals.logger.error("no={} status:{}".format(ite_menu_conductor_exec, resp_data["status"]))
        #     error_detail = multi_lang.get_text("EP034-0002", "CD実行の呼び出しに失敗しました ita-status:{0} resultdata:{1}".format(eresp_data["status"], eresp_data["resultdata"]), eresp_data["status"], eresp_data["resultdata"])
        #     raise common.UserException(error_detail)

        # 正常終了
        ret_status = 200

        # 戻り値をそのまま返却        
        return jsonify({"result": ret_status}), ret_status

    except common.UserException as e:
        return common.server_error(e)
    except Exception as e:
        return common.server_error(e)


def cd_result_get(workspace_id, conductor_id):
    """CD実行結果取得 cd result get

    Args:
        workspace_id (int): workspace id
        conductor_id (str): conductor id

    Returns:
        Response: HTTP Respose
    """

    try:
        globals.logger.debug('#' * 50)
        globals.logger.debug('CALL {}'.format(inspect.currentframe().f_code.co_name))
        globals.logger.debug('#' * 50)

        # ワークスペースアクセス情報取得 get workspace access info.
        access_info = api_access_info.get_access_info(workspace_id)

        # namespaceの取得 get namespace 
        namespace = common.get_namespace_name(workspace_id)

        ita_restapi_endpoint = "http://{}.{}.svc:{}/default/menu/07_rest_api_ver1.php".format(EPOCH_ITA_HOST, namespace, EPOCH_ITA_PORT)
        ita_user = access_info['ITA_USER']
        ita_pass = access_info['ITA_PASSWORD']

        # POST送信する
        # HTTPヘッダの生成
        filter_headers = {
            'host': EPOCH_ITA_HOST + ':' + EPOCH_ITA_PORT,
            'Content-Type': 'application/json',
            'Authorization': base64.b64encode((ita_user + ':' + ita_pass).encode()),
            'X-Command': 'INFO',
        }

        # 実行パラメータ設定
        data = {
            "CONDUCTOR_INSTANCE_ID": conductor_id
        }

        # json文字列に変換（"utf-8"形式に自動エンコードされる）
        json_data = json.dumps(data)

        # リクエスト送信
        exec_response = requests.post(ita_restapi_endpoint + '?no=' + ite_menu_conductor_conductor_result, headers=filter_headers, data=json_data)

        if exec_response.status_code != 200:
            globals.logger.error(exec_response.text)
            error_detail = multi_lang.get_text("EP034-0005", "実行結果取得の呼び出しに失敗しました status:{0}".format(exec_response.status_code), exec_response.status_code)
            raise common.UserException(error_detail)

        # globals.logger.debug("-------------------------")
        # globals.logger.debug("response:")
        # globals.logger.debug(exec_response.text)
        # globals.logger.debug("-------------------------")

        resp_data = json.loads(exec_response.text)

        if resp_data["status"] != "SUCCEED":
            globals.logger.error("no={} status:{}".format(ite_menu_conductor_exec, resp_data["status"]))
            error_detail = multi_lang.get_text("EP034-0006", "実行結果取得の呼び出しに失敗しました ita-status:{0} resultdata:{1}".format(eresp_data["status"], eresp_data["resultdata"]), eresp_data["status"], eresp_data["resultdata"])
            raise common.UserException(error_detail)

        rows = resp_data

        # 正常終了
        ret_status = 200

        # 戻り値をそのまま返却        
        return jsonify({"result": ret_status, "rows": rows}), ret_status

    except common.UserException as e:
        return common.server_error(e)
    except Exception as e:
        return common.server_error(e)
