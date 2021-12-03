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


# 共通項目
column_indexes_common = {
    "method": 0,    # 実行処理種別
    "delete": 1,    # 廃止
    "record_no": 2, # No
}

# 項目名リスト
column_names_opelist = {
    'operation_id': 'オペレーションID',
    'operation_name': 'オペレーション名',
    'operation_date': '実施予定日時',
    'remarks': '備考',
}

COND_CLASS_NO_CD_EXEC = 2


def post_cd_pipeline(workspace_id):
    """CDパイプライン情報設定

    Args:
        workspace_id (int): workspace ID

    Returns:
        Response: HTTP Respose
    """

    app_name = "ワークスペース情報:"
    exec_stat = "CDパイプライン情報設定"
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

        # epoch-control-argocd-api の呼び先設定
        api_url = "{}://{}:{}/workspace/{}/argocd/settings".format(os.environ['EPOCH_CONTROL_ARGOCD_PROTOCOL'],
                                                                    os.environ['EPOCH_CONTROL_ARGOCD_HOST'],
                                                                    os.environ['EPOCH_CONTROL_ARGOCD_PORT'],
                                                                    workspace_id)
        # argocd/settings post送信
        response = requests.post(api_url, headers=post_headers, data=json.dumps(post_data))
        globals.logger.debug("post argocd/settings response:{}".format(response.text))

        if response.status_code != 200:
            error_detail = 'argocd/settings post処理に失敗しました'
            raise common.UserException(error_detail)

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
        exec_stat = "認証基盤 初期情報設定"
        for client in clients:
            response = requests.post("{}{}/{}/{}".format(api_url_epai, 'settings', os.environ["EPOCH_EPAI_REALM_NAME"], 'clients'), headers=post_headers, data=json.dumps(client))

            # 正常時以外はExceptionを発行して終了する
            if response.status_code != 200:
                globals.logger.debug(response.text)
                error_detail = "認証基盤 初期情報設定の生成に失敗しました。 {}".format(response.status_code)
                raise common.UserException(error_detail)

        exec_stat = "認証基盤 設定読み込み"
        response = requests.put("{}{}".format(api_url_epai, 'apply_settings'))

        # 正常時以外はExceptionを発行して終了する
        if response.status_code != 200:
            error_detail = "認証基盤 設定読み込みに失敗しました。 {}".format(response.status_code)
            raise common.UserException(error_detail)

        ret_status = 200

        # 戻り値をそのまま返却        
        return jsonify({"result": ret_status}), ret_status

    except common.UserException as e:
        return common.server_error_to_message(e, app_name + exec_stat, error_detail)
    except Exception as e:
        return common.server_error_to_message(e, app_name + exec_stat, error_detail)


def cd_execute(workspace_id):
    """CD実行 cd execute

    Args:
        workspace_id (int): workspace ID

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

        # 引数をJSON形式で受け取りそのまま引数に設定 parameter set json
        request_json = request.json.copy()

        # ヘッダ情報 header info.
        post_headers = {
            'Content-Type': 'application/json',
        }

        # 呼び出すapiInfoは環境変数より取得 api url set
        apiInfo = "{}://{}:{}/workspace/{}/it-automation".format(os.environ["EPOCH_CONTROL_ITA_PROTOCOL"],
                                                                os.environ["EPOCH_CONTROL_ITA_HOST"],
                                                                os.environ["EPOCH_CONTROL_ITA_PORT"],
                                                                workspace_id)
        # globals.logger.debug ("cicd url:" + apiInfo)

        # オペレーション一覧の取得(ITA) get a ita operations
        request_response = requests.get(apiInfo + "/cd/operations", headers=post_headers)
        # globals.logger.debug("cd/operations:" + request_response.text)
        # 戻り値がJson形式かチェックする return parameter is json?
        if common.is_json_format(request_response.text):
            ret = json.loads(request_response.text)
        else:
            globals.logger.debug("cd/operations:response:{}".format(request_response.text))
            error_detail = "CD実行に失敗しました"
            raise common.UserException(error_detail)

        ret_ita = ret['rows']
        # 項目位置の取得 get columns 
        column_indexes_opelist = column_indexes(column_names_opelist, ret_ita['resultdata']['CONTENTS']['BODY'][0])
        globals.logger.debug('---- Operation Index ----')
        globals.logger.debug(column_indexes_opelist)

        # 引数のgit urlをもとにオペレーションIDを取得 get operation id for git-url
        ope_id = search_opration_id(ret_ita['resultdata']['CONTENTS']['BODY'], column_indexes_opelist, request_json['operationSearchKey'])
        if ope_id is None:
            globals.logger.debug("Operation ID Not found!")
            error_detail = "Operation ID Not found!"
            raise common.UserException(error_detail)

        # CD実行の引数を設定 paramater of cd execute 
        post_data = {
            "operation_id" : ope_id,
            "conductor_class_no" : COND_CLASS_NO_CD_EXEC,
            "preserve_datetime" : request_json["preserveDatetime"]
        }
        post_data = json.dumps(post_data)

        # CD実行(ITA) cd execute ita
        request_response = requests.post(apiInfo + "/cd/execute", headers=post_headers, data=post_data)
        # 戻り値がJson形式かチェックする return parameter is json?
        if common.is_json_format(request_response.text):
            ret = json.loads(request_response.text)
            #ret = request_response.text
            globals.logger.debug("result:{}".format(ret["result"]))
            # 正常の判断 Normal judgment
            if ret["result"] != "200" and ret["result"] != "201":
                globals.logger.debug("status error: ita/execute:response:{}".format(request_response.text))
                error_detail = "CD実行に失敗しました"
                raise common.UserException(error_detail)
        else:
            globals.logger.debug("ita/execute:response:{}".format(request_response.text))
            error_detail = "CD実行に失敗しました"
            raise common.UserException(error_detail)

        # 正常終了 normal return code
        ret_status = 200

        return jsonify({"result": ret_status}), ret_status

    except common.UserException as e:
        return common.server_error_to_message(e, app_name + exec_stat, error_detail)
    except Exception as e:
        return common.server_error_to_message(e, app_name + exec_stat, error_detail)

