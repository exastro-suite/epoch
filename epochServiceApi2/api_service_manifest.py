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
import multi_lang

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
    globals.logger.info('Set manifest parameter. workspace_id={}'.format(workspace_id))

    app_name = "ワークスペース情報:"
    exec_stat = "manifestパラメータ登録"
    error_detail = ""

    try:
        # ヘッダ情報 post header info.
        post_headers = {
            'Content-Type': 'application/json',
        }

        # 引数をJSON形式で受け取りそのまま引数に設定 Receive the argument in JSON format and set it as it is
        post_data = request.json.copy()

        # send put (workspace data update)
        apiInfo = "{}://{}:{}".format(os.environ['EPOCH_RS_WORKSPACE_PROTOCOL'], os.environ['EPOCH_RS_WORKSPACE_HOST'], os.environ['EPOCH_RS_WORKSPACE_PORT'])
        globals.logger.info('Send a request. workspace_id={}, URL={}/workspace/{}/manifestParameter'.format(workspace_id, apiInfo, workspace_id))
        request_response = requests.put( "{}/workspace/{}/manifestParameter".format(apiInfo, workspace_id), headers=post_headers, data=json.dumps(post_data))
        # エラーの際は処理しない
        if request_response.status_code == 404:
            error_detail = multi_lang.get_text("EP000-0023", "対象の情報(workspace)が他で更新されたため、更新できません\n画面更新後、再度情報を入力・選択して実行してください", "workspace")
            raise common.UpdateException("{} Exclusive check error".format(inspect.currentframe().f_code.co_name))
        elif request_response.status_code != 200:
            globals.logger.error("Fail: Update manifestParameter. ret_status={}, workspace_id={}".format(request_response.status_code, workspace_id))
            error_detail = "ワークスペース情報更新失敗"
            raise common.UserException(error_detail)

        # ヘッダ情報
        post_headers = {
            'Content-Type': 'application/json',
        }

        # 引数をJSON形式で受け取りそのまま引数に設定 Receive the argument in JSON format and set it as it is
        post_data = request.json.copy()

        # 呼び出すapiInfoは、環境変数より取得
        apiInfo = "{}://{}:{}".format(os.environ["EPOCH_CONTROL_ITA_PROTOCOL"], os.environ["EPOCH_CONTROL_ITA_HOST"], os.environ["EPOCH_CONTROL_ITA_PORT"])

        # Manifestパラメータ設定(ITA)
        globals.logger.info('Send a request. workspace_id={} URL="{}/workspace/{}/it-automation/manifest/parameter'.format(workspace_id, apiInfo, workspace_id))
        request_response = requests.post( "{}/workspace/{}/it-automation/manifest/parameter".format(apiInfo, workspace_id), headers=post_headers, data=json.dumps(post_data))
        # globals.logger.debug("ita/manifestParameter:response:" + request_response.text.encode().decode('unicode-escape'))
        ret = json.loads(request_response.text)
        #ret = request_response.text
        # globals.logger.debug(ret["result"])
        if request_response.status_code != 200:
            globals.logger.error("Fail: Set it-automation manifest parameter. ret_status={}, workspace_id={}".format(request_response.status_code, workspace_id))
            error_detail = "IT-Automation パラメータ登録失敗"
            raise common.UserException(error_detail)

        # 変更後のworkspace取得 Get workspace after change
        api_url = "{}://{}:{}/workspace/{}".format(os.environ['EPOCH_RS_WORKSPACE_PROTOCOL'],
                                                    os.environ['EPOCH_RS_WORKSPACE_HOST'],
                                                    os.environ['EPOCH_RS_WORKSPACE_PORT'],
                                                    workspace_id)
        globals.logger.info('Send a request. workspace_id={}, URL={}'.format(workspace_id, api_url))
        response = requests.get(api_url)

        # 正常以外はエラーを返す Returns an error if not normal
        if response.status_code != 200:
            globals.logger.info('Fail: Get workspace detail. workspace_id={}'.format(workspace_id))
            if common.is_json_format(response.text):
                ret = json.loads(response.text)
                # 詳細エラーがある場合は詳細を設定
                if ret["errorDetail"] is not None:
                    error_detail = ret["errorDetail"]
            raise common.UserException("{} Error put workspace db status:{}".format(inspect.currentframe().f_code.co_name, response.status_code))

        rows = json.loads(response.text)
        row = rows["rows"][0]

        # 正常終了 normal return code
        ret_status = 200

        globals.logger.info('SUCCESS: Set manifest parameter. workspace_id={}, ret_status={}, update_at={}'.format(workspace_id, ret_status,row["update_at"]))

        return jsonify({"result": ret_status, "update_at": row["update_at"]}), ret_status

    except common.UpdateException as e:
        return common.user_error_to_message(e, app_name + exec_stat, error_detail, 400)
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
    globals.logger.info('Set manifest template. workspace_id={}'.format(workspace_id))

    app_name = "ワークスペース情報:"
    exec_stat = "manifestテンプレート登録"
    error_detail = ""

    try:
        # ファイルの存在チェック exists file check
        if 'manifest_files' not in request.files:
            error_detail = "アップロードファイルがありません"
            globals.logger.info('Not exist manifest file.')
            raise common.UserException(error_detail)

        apiInfo = "{}://{}:{}".format(os.environ['EPOCH_RS_WORKSPACE_PROTOCOL'],
                                      os.environ['EPOCH_RS_WORKSPACE_HOST'],
                                      os.environ['EPOCH_RS_WORKSPACE_PORT'])

        # ヘッダ情報
        post_headers = {
            'Content-Type': 'application/json',
        }

        # データ情報(追加用)
        post_data_add = {
            "manifests": [

            ]
        }

        # データ情報(更新用)
        post_data_upd = {
            "manifests": [

            ]
        }

        # RsWorkspace API呼び出し(全件取得)
        globals.logger.info('Send a request. workspace_id={} URL={}/workspace/{}/manifests'.format(workspace_id, apiInfo, workspace_id ))
        response = requests.get("{}/workspace/{}/manifests".format(apiInfo, workspace_id), headers=post_headers)

        # 戻り値が正常値以外の場合は、処理を終了
        if response.status_code != 200:
            error_detail = "manifestテンプレート情報取得失敗"
            globals.logger.info("Fail: Get manifest template information. workspace_id={}".format(workspace_id))
            raise common.UserException(error_detail)

        ret_manifests = json.loads(response.text)
        globals.logger.debug("get Filedata ------------------ S")
        globals.logger.debug(ret_manifests["rows"])
        globals.logger.debug("get Filedata ------------------ E")

        # 送信されたマニフェストファイル数分処理する
        for manifest_file in request.files.getlist('manifest_files'):

            file_text = ''

            # ↓ 2重改行になっているので、変更するかも ↓
            for line in manifest_file:

                file_text += line.decode('utf-8')

            # 画面でBlueGreenするが選択されたら
            # If Blue Green is selected on the screen
            # if  xx == "BlueGreen":
            # BlueGreen Deployment 用に自動変換
            post_data = {
                # todo: test用データ
                # "deploy_method": "BlueGreen",
                "deploy_params": {
                    "scaleDownDelaySeconds": "{{ bluegreen_sdd_sec }}",
                },
                "file_text": file_text,
            }

            api_control_workspace = "{}://{}:{}".format(os.environ['EPOCH_CONTROL_WORKSPACE_PROTOCOL'],
                                                        os.environ['EPOCH_CONTROL_WORKSPACE_HOST'],
                                                        os.environ['EPOCH_CONTROL_WORKSPACE_PORT'])

            # BlueGreen Deploymentの自動変換
            globals.logger.info('Send a request. workspace_id={}, URL={}/workspace/{}/manifest/templates'.format(workspace_id, api_control_workspace, workspace_id))
            response = requests.post("{}/workspace/{}/manifest/templates".format(api_control_workspace, workspace_id), headers=post_headers, data=json.dumps(post_data))

            # 戻り値が正常値以外の場合は、処理を終了
            if response.status_code != 200:
                error_detail = "manifestテンプレート変換失敗"
                globals.logger.info('Fail: Change manifest template. ret_status={}'.format(response.status_code))
                raise common.UserException(error_detail)

            ret_template = json.loads(response.text)

            # ファイル情報(manifest_data)
            manifest_data = {
                "file_name": manifest_file.filename,
                "file_text": ret_template["file_text"],
            }

            # 同一ファイルがあるかファイルIDを取得
            file_id = common.get_file_id(ret_manifests["rows"], manifest_file.filename)

            # 同一ファイル名が登録されている場合は、更新とする
            if not file_id:
                # データ登録情報(manifest_dataと結合)
                post_data_add['manifests'].append(manifest_data)
            else:
                manifest_data["file_id"] = file_id
                # データ更新情報(manifest_dataと結合)
                post_data_upd['manifests'].append(manifest_data)

        globals.logger.debug("post_data_add ------------------ S")
        globals.logger.debug(post_data_add)
        globals.logger.debug("post_data_add ------------------ E")

        globals.logger.debug("post_data_upd ------------------ S")
        globals.logger.debug(post_data_upd)
        globals.logger.debug("post_data_upd ------------------ E")

        # RsWorkspace API呼び出し(削除)
        # response = requests.delete( apiInfo + "/workspace/" + str(workspace_id) + "/manifests", headers=post_headers)

        # 更新は１件ずつ実施
        for upd in post_data_upd['manifests']:

            # JSON形式に変換
            post_data = json.dumps(upd)

            # RsWorkspace API呼び出し(更新)
            globals.logger.info('Send a request. workspace_id={}, URL={}/workspace/{}/manifests/{}'.format(workspace_id, apiInfo, workspace_id, upd["file_id"]))
            response = requests.put("{}/workspace/{}/manifests/{}".format(apiInfo, workspace_id, upd["file_id"]), headers=post_headers, data=post_data)

        # JSON形式に変換
        post_data = json.dumps(post_data_add)

        # RsWorkspace API呼び出し(登録)
        globals.logger.info('Send a request. workspace_id={}, URL={}/workspace/{}/manifests'.format(workspace_id, apiInfo, workspace_id))
        response = requests.post("{}/workspace/{}/manifests".format(apiInfo, workspace_id), headers=post_headers, data=post_data)

        # ITA呼び出し
        globals.logger.debug("CALL ita_registration Start")
        response = ita_registration(workspace_id)
        globals.logger.debug("CALL ita_registration End response:")
        globals.logger.debug(response)

        # 正常終了 normal return code
        ret_status = 200

        globals.logger.info('SUCCESS: Set manifest template. ret_status={}, workspace_id={}, manifest_template_count={}'.format(ret_status, workspace_id, len(response)))

        return jsonify({"result": ret_status, "rows": response}), ret_status

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
    globals.logger.info('Get manifest template. workspace_id={}'.format(workspace_id))

    app_name = "ワークスペース情報:"
    exec_stat = "manifestテンプレート取得"
    error_detail = ""

    try:
        resourceProtocol = os.environ['EPOCH_RS_WORKSPACE_PROTOCOL']
        resourceHost = os.environ['EPOCH_RS_WORKSPACE_HOST']
        resourcePort = os.environ['EPOCH_RS_WORKSPACE_PORT']
        apiurl = "{}://{}:{}/workspace/{}/manifests".format(resourceProtocol, resourceHost, resourcePort, workspace_id)

        # ヘッダ情報
        headers = {
            'Content-Type': 'application/json',
        }

        # GET送信（作成）
        globals.logger.info('Send a request. workspace_id={} URL={}'.format(workspace_id, apiurl))
        response = requests.get(apiurl, headers=headers)

        globals.logger.debug("get_manifests return --------------------")
        globals.logger.debug(json.loads(response.text))
        globals.logger.debug("--------------------")

        globals.logger.info('ret_status={}'.format(response.status_code))
        if response.status_code == 200 and common.is_json_format(response.text):
            # 200(正常)かつ、レスポンスデータがJSON形式の場合は、後続の処理を実行
            pass

        elif response.status_code == 404:
            error_detail = 'manifest template data not found'
            raise common.UserException(error_detail)

        elif response.status_code != 200:
            # 200(正常), 404(not found) 以外の応答の場合
            error_detail = 'CALL responseAPI Error'
            raise common.UserException(error_detail)

        ret_manifests = json.loads(response.text)

        rows = ret_manifests["rows"]

        # 正常終了 normal return code
        ret_status = 200

        globals.logger.info('SUCCESS: Get manifest template. ret_status={}, workspace_id={}, manifest_template_count={}'.format(ret_status, workspace_id, len(rows)))

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
    globals.logger.info('Delete manifest template. workspace_id={}, file_id={}'.format(workspace_id, file_id))

    app_name = "ワークスペース情報:"
    exec_stat = "manifestテンプレート削除"
    error_detail = ""

    try:
        # ヘッダ情報
        headers = {
            'Content-Type': 'application/json',
        }

        # DELETE送信（作成）
        resourceProtocol = os.environ['EPOCH_RS_WORKSPACE_PROTOCOL']
        resourceHost = os.environ['EPOCH_RS_WORKSPACE_HOST']
        resourcePort = os.environ['EPOCH_RS_WORKSPACE_PORT']
        apiurl = "{}://{}:{}/workspace/{}/manifests/{}".format(resourceProtocol, resourceHost, resourcePort, workspace_id, file_id)

        globals.logger.info('Send a request. workspace_id={} file_id={} URL={}'.format(workspace_id, file_id, apiurl))
        response = requests.delete(apiurl, headers=headers)

        globals.logger.info('ret_status={}'.format(response.status_code))
        if response.status_code == 200 and common.is_json_format(response.text):
            # 200(正常)かつ、レスポンスデータがJSON形式の場合は、後続の処理を実行
            pass

        elif response.status_code == 404:
            # manifestデータが見つからない(404)場合
            error_detail = 'manifest template data not found'
            raise common.UserException(error_detail)

        elif response.status_code != 200:
            # 200(正常), 404(not found) 以外の応答の場合
            error_detail = 'CALL responseAPI Error'
            raise common.UserException(error_detail)

        # ITA呼び出し
        globals.logger.debug("CALL ita_registration Start")
        response = ita_registration(workspace_id)
        globals.logger.debug("CALL ita_registration End response:")
        globals.logger.debug(response)

        # 正常終了 normal return code
        ret_status = 200

        globals.logger.info('SUCCESS: Delete manifest template. workspace_id={}, file_id={}, ret_status={}, manifest_template_count={}'.format(workspace_id, file_id, ret_status, len(response)))

        return jsonify({"result": ret_status, "rows": response}), ret_status

    except common.UserException as e:
        return common.server_error_to_message(e, app_name + exec_stat, error_detail)
    except Exception as e:
        return common.server_error_to_message(e, app_name + exec_stat, error_detail)


def ita_registration(workspace_id):
    """ITA登録

    Args:
        workspace_id (Int): ワークスペースID

    Returns:
        Json: 設定したManifest情報
    """

    globals.logger.info('Register with it-automation. workspace_id={}'.format(workspace_id))

    try:
        # post先のURL初期化
        resourceProtocol = os.environ['EPOCH_RS_WORKSPACE_PROTOCOL']
        resourceHost = os.environ['EPOCH_RS_WORKSPACE_HOST']
        resourcePort = os.environ['EPOCH_RS_WORKSPACE_PORT']
        apiurl = "{}://{}:{}/workspace/{}/manifests".format(resourceProtocol, resourceHost, resourcePort, workspace_id)

        # ヘッダ情報
        post_headers = {
            'Content-Type': 'application/json',
        }

        # RsWorkspace API呼び出し RsWorkspace API call
        globals.logger.info('Send a request. workspace_id={} URL={}'.format(workspace_id, apiurl))
        response = requests.get(apiurl, headers=post_headers)
#        print("CALL responseAPI : response:{}, text:{}".format(response, response.text))

        # 戻り値が正常値以外の場合は、処理を終了
        # If the return value is other than the normal value, the process ends.
        if response.status_code != 200:
            raise Exception("CALL manifests get Error")

        # json形式変換 json format conversion
        ret_manifests = json.loads(response.text)
        # print("--------------------------")
        # print("manifest Json")
        # print(response.text)
        # print(ret_manifests['rows'])
#        print(json.loads(manifest_data))
        # print("--------------------------")

        # BlueGreen deploy方式を取得するためにワークスペース情報を取得
        # Get workspace information to get the BlueGreen deploy method
        apiurl = "{}://{}:{}/workspace/{}".format(resourceProtocol, resourceHost, resourcePort, workspace_id)
        globals.logger.info('Send a request. workspace_id={} URL={}'.format(workspace_id, apiurl))
        response = requests.get(apiurl, headers=post_headers)

        # 戻り値が正常値以外の場合は、処理を終了
        # If the return value is other than the normal value, the process ends.
        if response.status_code != 200:
            raise Exception("CALL workspace get Error")

        ret_ws = json.loads(response.text)

        # パラメータ情報(JSON形式) Parameter information (JSON format)
        ita_protocol = os.environ['EPOCH_CONTROL_ITA_PROTOCOL']
        ita_host = os.environ['EPOCH_CONTROL_ITA_HOST']
        ita_port = os.environ['EPOCH_CONTROL_ITA_PORT']

        send_data = {
            "manifests": ret_manifests['rows'],
        }
        globals.logger.debug("--------------------------")
        globals.logger.debug("send_data:")
        globals.logger.debug(send_data)
        globals.logger.debug("--------------------------")

        send_data = json.dumps(send_data)

        apiurl = "{}://{}:{}/workspace/{}/it-automation/manifest/templates".format(ita_protocol, ita_host, ita_port, workspace_id)

        # RsWorkspace API呼び出し RsWorkspace API call
        globals.logger.info('Send a request. workspace_id={} URL={}'.format(workspace_id, apiurl))
        response = requests.post(apiurl, headers=post_headers, data=send_data)

        # 正常時はmanifest情報取得した内容を返却
        # When normal, the acquired information is returned.
        if response.status_code == 200:

            globals.logger.info('SUCCESS: Register with it-automation. ret_status={}'.format(response.status_code))

            return ret_manifests['rows']
        else:
            globals.logger.info("Fail: Register with it-automation. ret_status={}, error_information={}".format(response.status_code, response.text))
            raise Exception("post it-automation/manifest/templates Error")

    except Exception:
        raise
