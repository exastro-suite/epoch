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
import zipfile
import glob

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
ite_menu_conductor_cancel = '2100180005'
ite_menu_conductor_download = '2100180006'

def get_cd_operations(workspace_id):
    """get cd-operations list

    Returns:
        Response: HTTP Respose
    """

    globals.logger.info('Get CD operations list. workspace_id={}'.format(workspace_id))

    app_name = "ワークスペース情報:"
    exec_stat = "Operation情報取得"
    error_detail = ""

    try:

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

        globals.logger.info('SUCCESS: Get CD operations list. ret_status={}, workspace_id={}, operation_count={}'.format(ret_status, workspace_id, len(rows)))

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

    globals.logger.info('Execute it-automation CD. workspace_id={}'.format(workspace_id))

    app_name = "ワークスペース情報:"
    exec_stat = "CD実行"
    error_detail = ""

    try:
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
            error_detail = multi_lang.get_text("EP034-0002", "CD実行の呼び出しに失敗しました ita-status:{0} resultdata:{1}".format(resp_data["status"], resp_data["resultdata"]), resp_data["status"], resp_data["resultdata"])
            raise common.UserException(error_detail)

        if resp_data["status"] != "SUCCEED":
            globals.logger.error("no={} status:{}".format(ite_menu_conductor_exec, resp_data["status"]))
            error_detail = multi_lang.get_text("EP034-0002", "CD実行の呼び出しに失敗しました ita-status:{0} resultdata:{1}".format(resp_data["status"], resp_data["resultdata"]), resp_data["status"], resp_data["resultdata"])
            raise common.UserException(error_detail)

        # 戻り値が"000"以外の場合は、エラーを返す
        # If the return value is other than "000", an error is returned.
        if resp_data["resultdata"]["RESULTCODE"] != "000":
            globals.logger.error("RESULTCODE error: resultdata:{}".format(resp_data["resultdata"]))
            error_detail = resp_data["resultdata"]["RESULTINFO"]
            raise common.UserException(error_detail)

        # 作業IDを退避
        cd_result_id = resp_data["resultdata"]["CONDUCTOR_INSTANCE_ID"]

        # 正常終了
        ret_status = 200

        globals.logger.info('SUCCESS: Execute it-automation CD. ret_status={}, workspace_id={}, cd_result_id={}'.format(ret_status, workspace_id, cd_result_id))

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

    globals.logger.info('Cancel it-automation cd execute. workspace_id={}, conductor_id={}'.format( workspace_id, conductor_id))

    try:
        # ワークスペースアクセス情報取得 get workspace access info.
        access_info = api_access_info.get_access_info(workspace_id)

        # namespaceの取得 get namespace 
        namespace = common.get_namespace_name(workspace_id)

        ita_restapi_endpoint = "http://{}.{}.svc:{}/default/menu/07_rest_api_ver1.php".format(EPOCH_ITA_HOST, namespace, EPOCH_ITA_PORT)
        ita_user = access_info['ITA_USER']
        ita_pass = access_info['ITA_PASSWORD']

        # HTTPヘッダの生成 HTTP header generation
        filter_headers = {
            'host': EPOCH_ITA_HOST + ':' + EPOCH_ITA_PORT,
            'Content-Type': 'application/json',
            'Authorization': base64.b64encode((ita_user + ':' + ita_pass).encode()),
            'X-Command': 'CANCEL',
        }

        # 実行パラメータ設定 Execution parameter setting
        data = {
            "CONDUCTOR_INSTANCE_ID": conductor_id
        }

        # json文字列に変換（"utf-8"形式に自動エンコードされる） Convert to json string (automatically encoded in "utf-8" format)
        json_data = json.dumps(data)

        # リクエスト送信
        response = requests.post(ita_restapi_endpoint + '?no=' + ite_menu_conductor_cancel, headers=filter_headers, data=json_data)

        globals.logger.debug(response.text)

        resp_data = json.loads(response.text)
        # Even if it fails, "status" is returned as "SUCCEED", so the error is judged by "RESULTCODE" (success: 0, failure: 2).
        # 失敗時も"status"は"SUCCEED"で返ってくるため、"RESULTCODE"(成功：0, 失敗：2)でエラーを判断
        if resp_data["resultdata"]["RESULTCODE"] == "002":
            globals.logger.error("no={} status:{}".format(ite_menu_conductor_cancel, resp_data["status"]))
            error_detail = multi_lang.get_text("EP034-0004", "CD予約取り消しの呼び出しに失敗しました ita-status:{0} resultdata:{1}".format(resp_data["status"], resp_data["resultdata"]), resp_data["status"], resp_data["resultdata"])
            raise common.UserException(error_detail)

        # 正常終了 Successful completion
        ret_status = 200

        globals.logger.info('SUCCESS: Cancel it-automation cd execute. ret_status={}, workspace_id={}, conductor_id={}'.format(ret_status, workspace_id, conductor_id))

        # 戻り値をそのまま返却 Return the return value as it is
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
        globals.logger.debug('CALL {} workspace_id[{}] conductor_id[{}]'.format(inspect.currentframe().f_code.co_name, workspace_id, conductor_id))
        globals.logger.debug('#' * 50)

        # ワークスペースアクセス情報取得 get workspace access info.
        access_info = api_access_info.get_access_info(workspace_id)

        # namespaceの取得 get namespace 
        namespace = common.get_namespace_name(workspace_id)

        ita_restapi_endpoint = "http://{}.{}.svc:{}/default/menu/07_rest_api_ver1.php".format(EPOCH_ITA_HOST, namespace, EPOCH_ITA_PORT)
        ita_user = access_info['ITA_USER']
        ita_pass = access_info['ITA_PASSWORD']

        # POST送信する post sender
        # HTTPヘッダの生成 HTTP header generation
        filter_headers = {
            'host': EPOCH_ITA_HOST + ':' + EPOCH_ITA_PORT,
            'Content-Type': 'application/json',
            'Authorization': base64.b64encode((ita_user + ':' + ita_pass).encode()),
            'X-Command': 'INFO',
        }

        # 実行パラメータ設定 parameter setting
        data = {
            "CONDUCTOR_INSTANCE_ID": conductor_id
        }

        # json文字列に変換 json convert
        json_data = json.dumps(data)

        # リクエスト送信 request post
        exec_response = requests.post(ita_restapi_endpoint + '?no=' + ite_menu_conductor_result, headers=filter_headers, data=json_data)

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

        # 正常終了 normal end
        ret_status = 200

        # 戻り値をそのまま返却 return to it-automation results        
        return jsonify({"result": ret_status, "rows": rows}), ret_status

    except common.UserException as e:
        return common.server_error(e)
    except Exception as e:
        return common.server_error(e)


def cd_result_logs_get(workspace_id, conductor_id):
    """CD実行結果ログ取得 cd result logs get

    Args:
        workspace_id (int): workspace id
        conductor_id (str): conductor id

    Returns:
        Response: HTTP Respose
    """

    try:
        globals.logger.debug('#' * 50)
        globals.logger.debug('CALL {} workspace_id[{}] conductor_id[{}]'.format(inspect.currentframe().f_code.co_name, workspace_id, conductor_id))
        globals.logger.debug('#' * 50)

        # ワークスペースアクセス情報取得 get workspace access info.
        access_info = api_access_info.get_access_info(workspace_id)

        # namespaceの取得 get namespace 
        namespace = common.get_namespace_name(workspace_id)

        ita_restapi_endpoint = "http://{}.{}.svc:{}/default/menu/07_rest_api_ver1.php".format(EPOCH_ITA_HOST, namespace, EPOCH_ITA_PORT)
        ita_user = access_info['ITA_USER']
        ita_pass = access_info['ITA_PASSWORD']

        # POST送信する post sender
        # HTTPヘッダの生成 HTTP header generation
        filter_headers = {
            'host': EPOCH_ITA_HOST + ':' + EPOCH_ITA_PORT,
            'Content-Type': 'application/json',
            'Authorization': base64.b64encode((ita_user + ':' + ita_pass).encode()),
            'X-Command': 'DOWNLOAD',
        }

        # 実行パラメータ設定 parameter setting
        data = {
            "CONDUCTOR_INSTANCE_NO": [ str(int(conductor_id)+1) ]

        }

        # json文字列に変換 json convert
        json_data = json.dumps(data)

        # リクエスト送信 request post
        exec_response = requests.post(ita_restapi_endpoint + '?no=' + ite_menu_conductor_download, headers=filter_headers, data=json_data)

        if exec_response.status_code != 200:
            globals.logger.error(exec_response.text)
            error_detail = multi_lang.get_text("EP034-0007", "実行結果ログ取得の呼び出しに失敗しました status:{0}".format(exec_response.status_code), exec_response.status_code)
            raise common.UserException(error_detail)

        # globals.logger.debug("-------------------------")
        # globals.logger.debug("response:")
        # globals.logger.debug(exec_response)
        # globals.logger.debug("response_text:")
        # globals.logger.debug(exec_response.text)
        # globals.logger.debug("-------------------------")

        # 戻り値用の器設定 Device setting for return value
        rows = {
            "manifest_embedding": {},
            "manifest_commit_push": {},
        }

        # 実行してすぐは読込ができない状況があるのでチェックする
        # Check because there are situations where it cannot be read immediately after execution.
        if not common.is_json_format(exec_response.text):
            # 実行途中の正常終了として返す Returns as normal termination during execution
            globals.logger.debug("not start!")
            ret_status = 404
            # 実行前なので404を返却 Return 404 because it is before execution  
            return jsonify({"result": ret_status, "rows": rows}), ret_status

        resp_data = json.loads(exec_response.text)
        # globals.logger.debug(f"resp_data:{resp_data}")

        if resp_data["status"] != "SUCCEED":
            globals.logger.error("no={} status:{}".format(ite_menu_conductor_exec, resp_data["status"]))
            error_detail = multi_lang.get_text("EP034-0008", "実行結果ログ取得の呼び出しに失敗しました ita-status:{0} resultdata:{1}".format(eresp_data["status"], eresp_data["resultdata"]), eresp_data["status"], eresp_data["resultdata"])
            raise common.UserException(error_detail)

        body_cnt = 0
        for body in resp_data["resultdata"]["CONTENTS"]["BODY"]:
            # download_input_key =  body["INPUT_DATA"]
            # base64_input_log_zip = resp_data["resultdata"]["CONTENTS"]["DOWNLOAD"][download_key]
            download_result_key =  body["RESULT_DATA"]
            base64_result_log_zip = resp_data["resultdata"]["CONTENTS"]["DOWNLOAD_FILE"][body_cnt][download_result_key]
            # globals.logger.debug(f"base64_result_log_zip:{base64_result_log_zip}")
            binary_result_log_zip = base64.b64decode(base64_result_log_zip.encode())

            with tempfile.TemporaryDirectory() as tempdir:

                # zipファイル生成 Zip file generation
                path_zip_file = '{}/{}'.format(tempdir, download_result_key)
                # globals.logger.debug(f"path_zip_file:{path_zip_file}")
                with open(path_zip_file, mode='bw') as fp:
                    fp.write(binary_result_log_zip)
                
                # zipファイルに含まれているファイル名の取得
                # Get the file name contained in the zip file
                with zipfile.ZipFile(path_zip_file) as log_zip:
                    # zipファイルに含まれているファイルのリストを返す
                    # Returns a list of files contained in the zip file
                    for f in log_zip.namelist():
                        # ファイル名の末尾が"/"じゃない内容を解凍
                        # Unzip the contents that do not end with "/" in the file name
                        if f[-1:] != "/":
                            # globals.logger.debug(f"f:{f}")

                            # zipファイルに含まれているファイルを取り出す
                            # Extract the files contained in the zip file
                            log_zip.extract(f, tempdir)

                # 解凍した各フォルダの内容を再度解凍
                # Unzip the contents of each unzipped folder again
                files = glob.glob(tempdir + "/**/*.zip")
                for file in files:
                    # globals.logger.debug(f"file:{file}")

                    with zipfile.ZipFile(file) as log_zip:
                        for f in log_zip.namelist():
                            if f == "exec.log":
                                # 実行ログ Execution log
                                # globals.logger.debug(f"f:{f}")
                                with log_zip.open(f) as f_log:
                                    exec_logs = f_log.read()
                                    # globals.logger.debug(f"logs:{exec_logs}")
                            elif f == "error.log":
                                # エラーログ error log
                                # globals.logger.debug(f"f:{f}")
                                with log_zip.open(f) as f_log:
                                    error_logs = f_log.read()
                                    # globals.logger.debug(f"logs:{error_logs}")

                    sub_dir_name = os.path.basename(os.path.dirname(file))
                    # globals.logger.debug(f"sub_dir_name:{sub_dir_name}")
                    if sub_dir_name == "0000000001":
                        # フォルダの1番目は、Manifest埋め込みのログ
                        # The first folder is the Manifest embedded log
                        rows["manifest_embedding"] = {
                                "execute_logs": exec_logs.decode('utf-8'),
                                "error_logs": error_logs.decode('utf-8'),
                            }
                    elif sub_dir_name == "0000000002":
                        # フォルダの2番目は、Manifest Commit&Pushのログ
                        # The second folder is the Manifest Commit & Push log
                        rows["manifest_commit_push"] = {
                                "execute_logs": exec_logs.decode('utf-8'),
                                "error_logs": error_logs.decode('utf-8'),
                            }

            body_cnt += 1

        # globals.logger.debug(f"rows:{rows}")

        # 正常終了 normal end
        ret_status = 200

        # 戻り値をそのまま返却        
        return jsonify({"result": ret_status, "rows": rows}), ret_status

    except common.UserException as e:
        return common.server_error(e)
    except Exception as e:
        return common.server_error(e)
