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
import api_access_info
import api_ita_manifests
import api_ita_cd

WAIT_SEC_ITA_POD_UP = 600 # ITA Pod 起動待ち時間(sec) ready check wait time
WAIT_SEC_ITA_IMPORT = 60 # ITA Import最大待ち時間(sec) import wait time
EPOCH_ITA_HOST = "it-automation"
EPOCH_ITA_PORT = "8084"

# 設定ファイル読み込み・globals初期化 flask setting file read and globals initialize
app = Flask(__name__)
app.config.from_envvar('CONFIG_API_ITA_PATH')
globals.init(app)

@app.route('/alive', methods=["GET"])
def alive():
    """死活監視(alive monitor)

    Returns:
        Response: HTTP Respose
    """
    return jsonify({"result": "200", "time": str(datetime.now(globals.TZ))}), 200


@app.route('/workspace/<int:workspace_id>/it-automation', methods=['POST'])
def call_ita(workspace_id):
    """workspace/workspace_id/it-automation call

    Args:
        workspace_id (int): workspace id

    Returns:
        Response: HTTP Respose
    """
    try:
        globals.logger.debug('#' * 50)
        globals.logger.debug('CALL {}:from[{}] workspace_id[{}]'.format(inspect.currentframe().f_code.co_name, request.method, workspace_id))
        globals.logger.debug('#' * 50)

        if request.method == 'POST':
            # it-automation pod create
            return create_ita(workspace_id)
        else:
            # Error
            raise Exception("method not support!")

    except Exception as e:
        return common.server_error(e)


@app.route('/workspace/<int:workspace_id>/it-automation/settings', methods=['POST'])
def call_ita_settings(workspace_id):
    """workspace/workspace_id/it-automation/settings call

    Args:
        workspace_id (int): workspace id

    Returns:
        Response: HTTP Respose
    """
    try:
        globals.logger.debug('#' * 50)
        globals.logger.debug('CALL {}:from[{}] workspace_id[{}]'.format(inspect.currentframe().f_code.co_name, request.method, workspace_id))
        globals.logger.debug('#' * 50)

        if request.method == 'POST':
            # it-automation setting
            return settings_ita(workspace_id)
        else:
            # Error
            raise Exception("method not support!")

    except Exception as e:
        return common.server_error(e)


@app.route('/workspace/<int:workspace_id>/it-automation/manifest/git', methods=['POST'])
def call_ita_manifest_git(workspace_id):
    """workspace/workspace_id/it-automation/manifest/git call

    Args:
        workspace_id (int): workspace id

    Returns:
        Response: HTTP Respose
    """
    try:
        globals.logger.info('Set git environment. method={}, workspace_id={}'.format(request.method, workspace_id))

        if request.method == 'POST':
            # it-automation git-environment settging
            return api_ita_manifests.settings_git_environment(workspace_id)
        else:
            # Error
            raise Exception("method not support!")

    except Exception as e:
        return common.server_error(e)


@app.route('/workspace/<int:workspace_id>/it-automation/manifest/parameter', methods=['POST'])
def call_ita_manifest_parameter(workspace_id):
    """workspace/workspace_id/it-automation/manifest/parameter call

    Args:
        workspace_id (int): workspace id

    Returns:
        Response: HTTP Respose
    """    
    try:
        globals.logger.info('Set it-automation manifest parameter. method={}, workspace_id={}'.format(request.method, workspace_id))

        if request.method == 'POST':
            # it-automation manifest-parameter settging
            return api_ita_manifests.settings_manifest_parameter(workspace_id)
        else:
            # Error
            raise Exception("method not support!")

    except Exception as e:
        return common.server_error(e)


@app.route('/workspace/<int:workspace_id>/it-automation/manifest/templates', methods=['POST'])
def call_ita_manifest_templates(workspace_id):
    """workspace/workspace_id/it-automation/manifest/templates call

    Args:
        workspace_id (int): workspace id

    Returns:
        Response: HTTP Respose
    """
    try:
        globals.logger.info('Set it-automation manifest template. method={}, workspace_id={}'.format(request.method, workspace_id))

        if request.method == 'POST':
            # it-automation manifest-templates settging
            return api_ita_manifests.settings_manifest_templates(workspace_id)
        else:
            # Error
            raise Exception("method not support!")

    except Exception as e:
        return common.server_error(e)


@app.route('/workspace/<int:workspace_id>/it-automation/cd/operations', methods=['GET'])
def call_ita_cd_operations(workspace_id):
    """workspace/workspace_id/it-automation/cd/operations call

    Args:
        workspace_id (int): workspace id

    Returns:
        Response: HTTP Respose
    """
    try:
        globals.logger.info('Get it-automation CD operation. method={}, workspace_id={}'.format(request.method, workspace_id))

        if request.method == 'GET':
            # it-automation get cd-operations 
            return api_ita_cd.get_cd_operations(workspace_id)
        else:
            # Error
            raise Exception("method not support!")

    except Exception as e:
        return common.server_error(e)


@app.route('/workspace/<int:workspace_id>/it-automation/cd/execute', methods=['POST'])
def call_ita_cd_execute(workspace_id):
    """workspace/workspace_id/it-automation/cd/execute call

    Args:
        workspace_id (int): workspace id

    Returns:
        Response: HTTP Respose
    """
    try:
        globals.logger.info('Execute it-automation CD. method={}, workspace_id={}'.format(request.method, workspace_id))

        if request.method == 'POST':
            # it-automation cd execute
            return api_ita_cd.cd_execute(workspace_id)
        else:
            # Error
            raise Exception("method not support!")

    except Exception as e:
        return common.server_error(e)


@app.route('/workspace/<int:workspace_id>/it-automation/cd/execute/<string:conductor_id>', methods=['DELETE'])
def call_ita_cd_execute_by_conductor_id(workspace_id, conductor_id):
    """workspace/workspace_id/it-automation/cd/execute call

    Args:
        workspace_id (int): workspace id
        conductor_id (str): conductor id

    Returns:
        Response: HTTP Respose
    """
    try:
        globals.logger.info('Cancel it-automation cd execute. method={}, workspace_id={}, conductor_id={}'.format(request.method, workspace_id, conductor_id))

        if request.method == 'DELETE':
            # it-automation cd execute cancel
            return api_ita_cd.cd_execute_cancel(workspace_id, conductor_id)
        else:
            # Error
            raise Exception("method not support!")

    except Exception as e:
        return common.server_error(e)


@app.route('/workspace/<int:workspace_id>/it-automation/cd/result/<string:conductor_id>', methods=['GET'])
def call_ita_cd_result(workspace_id, conductor_id):
    """workspace/workspace_id/it-automation/cd/result call

    Args:
        workspace_id (int): workspace id
        conductor_id (str): conductor id

    Returns:
        Response: HTTP Respose
    """
    try:
        globals.logger.debug('#' * 50)
        globals.logger.debug('CALL {}:from[{}] workspace_id[{}] conductor_id[{}]'.format(inspect.currentframe().f_code.co_name, request.method, workspace_id, conductor_id))
        globals.logger.debug('#' * 50)

        if request.method == 'GET':
            # it-automation cd result get
            return api_ita_cd.cd_result_get(workspace_id, conductor_id)
        else:
            # Error
            raise Exception("method not support!")

    except Exception as e:
        return common.server_error(e)


@app.route('/workspace/<int:workspace_id>/it-automation/cd/result/<string:conductor_id>/logs', methods=['GET'])
def call_ita_cd_result_logs(workspace_id, conductor_id):
    """workspace/workspace_id/it-automation/cd/result/logs call

    Args:
        workspace_id (int): workspace id
        conductor_id (str): conductor id

    Returns:
        Response: HTTP Respose
    """
    try:
        globals.logger.debug('#' * 50)
        globals.logger.debug('CALL {}:from[{}] workspace_id[{}] conductor_id[{}]'.format(inspect.currentframe().f_code.co_name, request.method, workspace_id, conductor_id))
        globals.logger.debug('#' * 50)

        if request.method == 'GET':
            # it-automation cd result logs get
            return api_ita_cd.cd_result_logs_get(workspace_id, conductor_id)
        else:
            # Error
            raise Exception("method not support!")

    except Exception as e:
        return common.server_error(e)


def create_ita(workspace_id):
    """IT-Automation Pod Create

    Args:
        workspace_id (int): workspace id

    Returns:
        Response: HTTP Respose
    """

    app_name = "ワークスペース情報:"
    exec_stat = "IT-Automation環境構築"
    error_detail = ""

    try:
        globals.logger.debug('#' * 50)
        globals.logger.debug('CALL {}'.format(inspect.currentframe().f_code.co_name))
        globals.logger.debug('#' * 50)

        # namespace定義
        name = common.get_namespace_name(workspace_id)

        globals.logger.debug("ita-pod create start")
        # templateの展開
        with tempfile.TemporaryDirectory() as tempdir:
            file_name = 'ita_install.yaml'
            yaml_param={
                "HTTP_PROXY": os.environ.get("EPOCH_HTTP_PROXY"),
                "HTTPS_PROXY": os.environ.get("EPOCH_HTTPS_PROXY"),
                "NO_PROXY": os.environ.get("EPOCH_HOSTNAME"),
            }
            yaml_text = render_template(file_name, param=yaml_param)

            # yaml一時ファイル生成
            path_yamlfile = '{}/{}'.format(tempdir, file_name)
            with open(path_yamlfile, mode='w') as fp:
                fp.write(yaml_text)

            # kubectl実行
            try:
                result_kubectl = subprocess.check_output(['kubectl', 'apply', '-f', path_yamlfile,'-n',name], stderr=subprocess.STDOUT)
                globals.logger.debug('COMMAAND SUCCEED: kubectl apply -f {}\n{}'.format(path_yamlfile, result_kubectl.decode('utf-8')))

            except subprocess.CalledProcessError as e:
                globals.logger.error('COMMAND ERROR RETURN:{}\n{}'.format(e.returncode, e.output.decode('utf-8')))
                exec_detail = "IT-AutomationのPodが生成できません。環境を確認してください。"
                raise common.UserException(exec_detail)
            except Exception:
                raise

        # 対象となるdeploymentを定義
        # deployments = [ "deployment/ita-worker" ]

        # envs = [
        #     "HTTP_PROXY=" + os.environ['EPOCH_HTTP_PROXY'],
        #     "HTTPS_PROXY=" + os.environ['EPOCH_HTTPS_PROXY'],
        #     "http_proxy=" + os.environ['EPOCH_HTTP_PROXY'],
        #     "https_proxy=" + os.environ['EPOCH_HTTPS_PROXY']
        # ]

        # exec_detail = "環境変数[PROXY]を確認してください"
        # for deployment_name in deployments:
        #     for env_name in envs:
        #         # 環境変数の設定
        #         try:
        #             result_kubectl = subprocess.check_output(["kubectl","set","env",deployment_name,"-n",name,env_name],stderr=subprocess.STDOUT)
        #             globals.logger.debug('COMMAAND SUCCEED: kubectl set env {}\n{}'.format(deployment_name, result_kubectl.decode('utf-8')))
        #         except subprocess.CalledProcessError as e:
        #             globals.logger.error('COMMAND ERROR RETURN:{}\n{}'.format(e.returncode, e.output.decode('utf-8')))
        #             exec_detail = "{}の環境変数[PROXY]の設定ができません。環境を確認してください。".format(deployment_name)
        #             raise common.UserException(exec_detail)
        #         except Exception:
        #             raise

        exec_detail = ""

        # 正常終了
        ret_status = 200

        # 戻り値をそのまま返却        
        return jsonify({"result": ret_status}), ret_status

    except common.UserException as e:
        return common.server_error_to_message(e, app_name + exec_stat, error_detail)
    except Exception as e:
        return common.server_error_to_message(e, app_name + exec_stat, error_detail)


def settings_ita(workspace_id):
    """IT-Automation 設定

    Args:
        workspace_id (int): workspace id

    Returns:
        Response: HTTP Respose
    """

    app_name = "ワークスペース情報:"
    exec_stat = "IT-Automation初期設定"
    error_detail = ""

    try:
        globals.logger.debug('#' * 50)
        globals.logger.debug('CALL {}'.format(inspect.currentframe().f_code.co_name))
        globals.logger.debug('#' * 50)

        ita_db_name = "ita_db"
        ita_db_user = "ita_db_user"
        ita_db_password = "ita_db_password"

        # パラメータ情報(JSON形式)
        payload = request.json.copy()

        # ワークスペースアクセス情報取得
        access_info = api_access_info.get_access_info(workspace_id)

        # namespaceの取得
        namespace = common.get_namespace_name(workspace_id)

        # *-*-*-* podが立ち上がるのを待つ *-*-*-*
        start_time = time.time()
        while True:
            globals.logger.debug("waiting for ita pod up...")

            # PodがRunningになったら終了
            if is_ita_pod_running(namespace):
                break

            # timeout
            current_time = time.time()
            if (current_time - start_time) > WAIT_SEC_ITA_POD_UP:
                globals.logger.debug("ITA pod start Time out S:{} sec:{}".format(start_time, (current_time - start_time)))
                error_detail = "IT-Automation 初期設定でタイムアウトしました。再度、実行してください。"
                raise common.UserException(error_detail)

            time.sleep(1)

        # *-*-*-* podが立ち上がるのを待つ *-*-*-*
        start_time = time.time()
        while True:
            globals.logger.debug("waiting for ita mariaDB up...")

            # PodがRunningになったら終了
            if is_ita_mysql_running(namespace, ita_db_user, ita_db_password):
                break

            # timeout
            current_time = time.time()
            if (current_time - start_time) > WAIT_SEC_ITA_POD_UP:
                globals.logger.debug("ITA mariaDB start Time out S:{} sec:{}".format(start_time, (current_time - start_time)))
                error_detail = "IT-Automation 初期設定でタイムアウトしました。再度、実行してください。"
                raise common.UserException(error_detail)

            time.sleep(1)

        # *-*-*-* パスワード更新済み判定とする *-*-*-*
        # command = "mysql -u %s -p%s %s < /app/epoch/tmp/ita_table_update.sql" % (ita_db_user, ita_db_password, ita_db_name)
        command = "mysql -u %s -p%s %s -e'UPDATE A_ACCOUNT_LIST SET PW_LAST_UPDATE_TIME = \"2999-12-31 23:59:58\" WHERE USER_ID = 1;'" % (ita_db_user, ita_db_password, ita_db_name)
        stdout_ita = subprocess.check_output(["kubectl", "exec", "-i", "-n", namespace, "deployment/it-automation", "--", "bash", "-c", command], stderr=subprocess.STDOUT)

        # *-*-*-* 認証情報準備 *-*-*-*
        host = "{}.{}.svc:{}".format(EPOCH_ITA_HOST, namespace, EPOCH_ITA_PORT)
        user_id = access_info["ITA_USER"]
        user_init_pass = "password"
        user_pass = access_info["ITA_PASSWORD"]

        # パスワード暗号化
        init_auth = base64.b64encode((user_id + ':' + user_init_pass).encode())
        auth = base64.b64encode((user_id + ':' + user_pass).encode())

        # すでに1度でもインポート済みの場合は、処理しない
        ret_is_import = is_already_imported(host, auth, init_auth)
        if ret_is_import == 200:
            globals.logger.debug("ITA initialize Imported.(success)")
            # 正常終了
            ret_status = 200
            # 戻り値をそのまま返却        
            return jsonify({"result": ret_status}), ret_status

        # 一度もインポートしていないときに処理する
        if ret_is_import == 0:
            # *-*-*-* インポート実行(初期パスワードで実行) *-*-*-*
            task_id = import_process(host, init_auth)

            # *-*-*-* インポート結果確認 *-*-*-*
            globals.logger.debug('---- monitoring import dialog ----')

            # POST送信する
            # ヘッダ情報
            header = {
                'host': host,
                'Content-Type': 'application/json',
                'Authorization': init_auth,
                'X-Command': 'FILTER',
            }

            # 実行パラメータ設定
            data = {
                "2": {
                    "LIST": [task_id]
                }
            }

            # json文字列に変換（"utf-8"形式に自動エンコードされる）
            json_data = json.dumps(data)

            start_time = time.time()

            while True:
                globals.logger.debug("monitoring...")
                time.sleep(3)

                # timeout
                current_time = time.time()
                if (current_time - start_time) > WAIT_SEC_ITA_IMPORT:
                    globals.logger.debug("ITA menu import Time out")
                    error_detail = "IT-Automation 初期設定でタイムアウトしました。再度、実行してください。"
                    raise common.UserException(error_detail)

                # リクエスト送信
                dialog_response = requests.post('http://' + host + '/default/menu/07_rest_api_ver1.php?no=2100000213', headers=header, data=json_data)
                if dialog_response.status_code != 200:
                    globals.logger.error("no=2100000213 error:{}".format(dialog_response.status_code))
                    globals.logger.error(dialog_response.text)
                    error_detail = "IT-Automation 初期設定が失敗しました。再度、実行してください。"
                    # タイミングによって500応答が返されるため継続
                    # raise common.UserException(error_detail)
                    continue

                # ファイルがあるメニューのため、response.textをデバッグ出力すると酷い目にあう
                # print(dialog_response.text)

                dialog_resp_data = json.loads(dialog_response.text)
                if dialog_resp_data["status"] != "SUCCEED" or dialog_resp_data["resultdata"]["CONTENTS"]["RECORD_LENGTH"] != 1:
                    globals.logger.error("no=2100000213 status:{}".format(dialog_resp_data["status"]))
                    globals.logger.error(dialog_response.text)
                    error_detail = "IT-Automation 初期設定が失敗しました。再度、実行してください。"
                    raise common.UserException(error_detail)

                record = dialog_resp_data["resultdata"]["CONTENTS"]["BODY"][1]
                globals.logger.debug(json.dumps(record))
                if record[3] == u"完了(異常)":
                    error_detail = "IT-Automation ITAのメニューインポートに失敗しました。"
                    raise common.UserException(error_detail)
                if record[3] == u"完了":
                    break

        error_detail = "IT-Automation 初期設定のパスワード初期化に失敗しました。"
        # *-*-*-* パスワード変更 *-*-*-*
        command = "mysql -u {} -p{} {} -e'UPDATE A_ACCOUNT_LIST".format(ita_db_user, ita_db_password, ita_db_name) + \
                    " SET PASSWORD = \"{}\"".format(hashlib.md5((user_pass).encode()).hexdigest()) + \
                    " WHERE USER_ID = 1;'"
        stdout_ita = subprocess.check_output(["kubectl", "exec", "-i", "-n", namespace, "deployment/it-automation", "--", "bash", "-c", command], stderr=subprocess.STDOUT)

        error_detail = "IT-Automation 初期設定のユーザー情報生成に失敗しました。"
        # *-*-*-* EPOCHユーザー更新 *-*-*-*
        command = "mysql -u {} -p{} {} -e'UPDATE A_ACCOUNT_LIST".format(ita_db_user, ita_db_password, ita_db_name) + \
                    " SET USERNAME = \"{}\"".format(access_info["ITA_EPOCH_USER"]) + \
                    " , PASSWORD = \"{}\"".format(hashlib.md5((access_info["ITA_EPOCH_PASSWORD"]).encode()).hexdigest()) + \
                    " , PW_LAST_UPDATE_TIME = \"2999-12-31 23:59:58\"" + \
                    " WHERE USER_ID = 2;'"
        stdout_ita = subprocess.check_output(["kubectl", "exec", "-i", "-n", namespace, "deployment/it-automation", "--", "bash", "-c", command], stderr=subprocess.STDOUT)

        # 正常終了
        ret_status = 200

        # 戻り値をそのまま返却        
        return jsonify({"result": ret_status}), ret_status

    except common.UserException as e:
        return common.server_error_to_message(e, app_name + exec_stat, error_detail)
    except Exception as e:
        return common.server_error_to_message(e, app_name + exec_stat, error_detail)


def is_already_imported(host, auth, init_auth):
    """新しいパスワードでのimport確認

    Args:
        host (str): ITAのホスト
        auth (str): ITAの認証情報
        init_auth (str): ITAの初期認証情報

    Raises:
        Exception: [description]
        common.UserException: [description]

    Returns:
        int: 200:インポート済み、0:インポート前
    """

    # *-*-*-* 新しいパスワードでのimport確認 *-*-*-*

    # POST送信する
    # ヘッダ情報
    header = {
        'host': host,
        'Content-Type': 'application/json',
        'Authorization': auth,
        'X-Command': 'FILTER',
    }

    # フィルタ条件はなし
    data = {}

    # json文字列に変換（"utf-8"形式に自動エンコードされる）
    json_data = json.dumps(data)

    # インポート結果取得
    dialog_response = requests.post('http://' + host + '/default/menu/07_rest_api_ver1.php?no=2100000213', headers=header, data=json_data)
    if dialog_response.status_code != 200 and dialog_response.status_code != 401:
        globals.logger.error("no=2100000213 status_code:{}".format(dialog_response.status_code))
        globals.logger.error(dialog_response.text)
        raise common.UserException(dialog_response.text)

    if dialog_response.status_code == 200:
        dialog_resp_data = json.loads(dialog_response.text)
        if dialog_resp_data["resultdata"]["CONTENTS"]["RECORD_LENGTH"] > 0:
            return 200
        else:
            # パスワード変更済み、かつインポートデータが無い状態は異常である
            raise common.UserException('IT-Automation Import error import-file abnormal')

    # *-*-*-* 初期パスワードでのimport確認 *-*-*-*

    # POST送信する
    # ヘッダ情報
    header = {
        'host': host,
        'Content-Type': 'application/json',
        'Authorization': init_auth,
        'X-Command': 'FILTER',
    }

    # フィルタ条件はなし
    data = {}

    # json文字列に変換（"utf-8"形式に自動エンコードされる）
    json_data = json.dumps(data)

    # インポート結果取得
    dialog_response = requests.post('http://' + host + '/default/menu/07_rest_api_ver1.php?no=2100000213', headers=header, data=json_data)
    if dialog_response.status_code != 200 and dialog_response.status_code != 401:
        globals.logger.error("no=2100000213 status_code:{}".format(dialog_response.status_code))
        globals.logger.error(dialog_response.text)
        raise common.UserException(dialog_response.text)

    if dialog_response.status_code == 200:
        # 初期パスワードで認証通る場合は、インポート前状態として判定する
        return 0

    # *-*-*-* システムが認識している以外のパスワードになっている *-*-*-*
    raise common.UserException('IT-Automation Import error password not abnormal')


def import_process(host, auth):
    """ファイルアップロード

    Args:
        host (str): ITAのホスト
        auth (str): ITAの認証情報

    Returns:
        str: task id
    """

    # *-*-*-* ファイルアップロード *-*-*-*
    upload_id, upload_filename, menu_items = kym_file_upload(host, auth)

    # menu_list再構築
    menu_list = {}
    for menu_group_id, menu_group_detail in menu_items:
        if menu_group_id in menu_list:
            menu_id_list = menu_list[menu_group_id]
        else:
            menu_id_list = []

        for menu_detail in menu_group_detail["menu"]:
            menu_id_list.append(int(menu_detail["menu_id"]))

        menu_list[menu_group_id] = menu_id_list

    # print(menu_list)

    # *-*-*-* インポート実行 *-*-*-*
    task_id = import_execute(host, auth, upload_id, menu_list, upload_filename)

    return task_id


def kym_file_upload(host, auth):
    """エクスポートファイルのアップロード

    Args:
        host (str): ITAのホスト
        auth (str): ITAの認証情報

    Raises:
        Exception: [description]

    Returns:
        [str]: upload id, filename, menu items 
    """

    globals.logger.debug('---- upload kym file ----')

    # インポートファイルのパス設定
    upload_filename = 'epoch_initialize.kym'
    kym_file_path = os.path.dirname(__file__) + "/resource/{}".format(upload_filename)

    # インポートファイルの内容をすべて取得
    with open(kym_file_path, 'rb') as f:
        kym_binary = f.read()
    encoded_data = base64.b64encode(kym_binary).decode(encoding='utf-8')
    upload_filename = os.path.basename(kym_file_path)

    # POST送信する
    # ヘッダ情報
    header = {
        'host': host,
        'Content-Type': 'application/json',
        'Authorization': auth,
        'X-Command': 'UPLOAD',
    }

    # 実行パラメータ設定
    data = {
        "zipfile": {
            "name": upload_filename,
            "base64": encoded_data,
        }
    }

    # json文字列に変換（"utf-8"形式に自動エンコードされる）
    json_data = json.dumps(data)

    globals.logger.debug('---- ita file upload ---- HOST:' + host)
    # リクエスト送信
    upload_response = requests.post('http://' + host + '/default/menu/07_rest_api_ver1.php?no=2100000212', headers=header, data=json_data)
    if upload_response.status_code != 200:
        globals.logger.error("no=2100000212 status_code:{}".format(upload_response.status_code))
        globals.logger.error(upload_response.text)
        raise common.UserException(upload_response.text)

    # print(upload_response.text)

    up_resp_data = json.loads(upload_response.text)
    if up_resp_data["status"] != "SUCCEED":
        globals.logger.error("no=2100000212 status:{}".format(up_resp_data["status"]))
        globals.logger.error(upload_response.text)
        raise common.UserException(upload_response.text)

    upload_id = up_resp_data["resultdata"]["upload_id"]
    globals.logger.debug('upload_id: ' + upload_id)

    menu_items = up_resp_data["resultdata"]["IMPORT_LIST"].items()

    return upload_id, upload_filename, menu_items


def import_execute(host, auth, upload_id, menu_list, upload_filename):
    """インポート実行

    Args:
        host (str): ITAのホスト
        auth (str): ITAの認証情報
        upload_id (str): upload id
        menu_list (str): menu items
        upload_filename (str): filename

    Raises:
        Exception: [description]

    Returns:
        str: task id
    """
    globals.logger.debug('---- execute menu import ----')

    # POST送信する
    # ヘッダ情報
    header = {
        'host': host,
        'Content-Type': 'application/json',
        'Authorization': auth,
        'X-Command': 'EXECUTE',
    }

    # 実行パラメータ設定
    data = menu_list
    data["upload_id"] = "A_" + upload_id
    data["data_portability_upload_file_name"] = upload_filename

    # json文字列に変換（"utf-8"形式に自動エンコードされる）
    json_data = json.dumps(data)

    # リクエスト送信
    exec_response = requests.post('http://' + host + '/default/menu/07_rest_api_ver1.php?no=2100000212', headers=header, data=json_data)
    if exec_response.status_code != 200:
        globals.logger.error("no=2100000212 status_code:{}".format(exec_response.status_code))
        globals.logger.error(exec_response.text)
        raise common.UserException(exec_response.text)

    globals.logger.debug(exec_response.text)

    exec_resp_data = json.loads(exec_response.text)
    if exec_resp_data["status"] != "SUCCEED" or exec_resp_data["resultdata"]["RESULTCODE"] != "000":
        globals.logger.error("no=2100000212 status:{}".format(exec_resp_data["status"]))
        globals.logger.error(exec_response.text)
        raise common.UserException(exec_response.text)

    task_id = exec_resp_data["resultdata"]["TASK_ID"]
    globals.logger.debug('task_id: ' + task_id)

    return task_id


def is_ita_pod_running(namespace):
    """podの起動チェック

    Args:
        namespace (str): namespace名

    Returns:
        True: ready ok!
    """

    stdout_pod_describe = subprocess.check_output(["kubectl", "get", "pods", "-n", namespace, "-l", "app=it-automation", "-o", "json"], stderr=subprocess.STDOUT)

    # pod_describe = yaml.load(stdout_pod_describe)
    pod_describe = json.loads(stdout_pod_describe)
    # globals.logger.debug('--- stdout_pod_describe ---')
    # globals.logger.debug(stdout_pod_describe)

    # Keyが存在する場合のみチェック
    try:
        if 'containerStatuses' in pod_describe['items'][0]['status']:
            return (pod_describe['items'][0]['status']['containerStatuses'][0]['ready'] == True)
        else:
            return False
    except Exception as e:
        return False
    # return (pod_describe['items'][0]['status']['phase'] == "Running")


def is_ita_mysql_running(namespace, ita_db_user, ita_db_password):
    """mysqlの起動チェック

    Args:
        namespace (str): namespace名
        ita_db_user (str): DB user
        ita_db_password (str): DB user password

    Returns:
        True: ready ok!
    """

    ret = False
    command = "mysqladmin ping -u {} -p{}".format(ita_db_user, ita_db_password)
    try:
        stdout_exec = subprocess.check_output(["kubectl", "exec", "-i", "-n", namespace, "deployment/it-automation", "--", "bash", "-c", command], stderr=subprocess.STDOUT)
        # globals.logger.error(stdout_exec)
        # 起動が完了しているかチェック Check if booting is complete
        if stdout_exec == b'mysqld is alive\n':
            ret = True

    except Exception as e:
        globals.logger.error(e.args)
        pass

    return ret


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('API_ITA_PORT', '8000')), threaded=True)
