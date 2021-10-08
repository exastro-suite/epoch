#   Copyright 2019 NEC Corporation
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

import cgi # CGIモジュールのインポート
import cgitb
import sys
import requests
import json
import subprocess
import traceback
import os
import datetime, pytz
import time
import base64
import logging
import yaml
import hashlib


from django.shortcuts import render
from django.http import HttpResponse
from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from epochCiCdApi.views_access import get_access_info

logger = logging.getLogger('apilog')

WAIT_ITA_POD_UP = 120 # ITA Pod起動待ち時間
WAIT_ITA_IMPORT = 60 # ITA Import最大待ち時間

@require_http_methods(['POST'])
@csrf_exempt
def post(request):

    logger.debug("CALL " + __name__)
    try:
        # パラメータ情報(JSON形式)
        payload = json.loads(request.body)

        # ワークスペース複数化するまでは1固定
        workspace_id = 1

        # ワークスペースアクセス情報取得
        access_info = get_access_info(workspace_id)

        namespace = "epoch-workspace"
        # *-*-*-* podが立ち上がるのを待つ *-*-*-*
        start_time = time.time()
        while True:
            logger.debug("waiting for ita pod up...")
            logger.debug(datetime.datetime.now(pytz.timezone('Asia/Tokyo')).strftime('%Y/%m/%d %H:%M:%S'))
            time.sleep(3)

            if is_ita_pod_running(namespace):
                break

            # timeout
            current_time = time.time()
            if (current_time - start_time) > WAIT_ITA_POD_UP:
                logger.debug("ITA pod start Time out")
                response = {
                    "result": "500",
                    "output": "ITA Pod起動確認 Time out",
                    "datetime": datetime.datetime.now(pytz.timezone('Asia/Tokyo')).strftime('%Y/%m/%d %H:%M:%S'),
                }
                return JsonResponse(response, status=500)

        # *-*-*-* パスワード更新済み判定とする *-*-*-*
        ita_db_name = "ita_db"
        ita_db_user = "ita_db_user"
        ita_db_password = "ita_db_password"
        # command = "mysql -u %s -p%s %s < /app/epoch/tmp/ita_table_update.sql" % (ita_db_user, ita_db_password, ita_db_name)
        command = "mysql -u %s -p%s %s -e'UPDATE A_ACCOUNT_LIST SET PW_LAST_UPDATE_TIME = \"2999-12-31 23:59:58\" WHERE USER_ID = 1;'" % (ita_db_user, ita_db_password, ita_db_name)
        stdout_ita = subprocess.check_output(["kubectl", "exec", "-i", "-n", namespace, "deployment/it-automation", "--", "bash", "-c", command], stderr=subprocess.STDOUT)

        # *-*-*-* 認証情報準備 *-*-*-*
        host = os.environ["EPOCH_ITA_HOST"] + ":" + os.environ["EPOCH_ITA_PORT"]
        user_id = access_info["ITA_USER"]
        user_init_pass = "password"
        user_pass = access_info["ITA_PASSWORD"]

        # パスワード暗号化
        init_auth = base64.b64encode((user_id + ':' + user_init_pass).encode())
        auth = base64.b64encode((user_id + ':' + user_pass).encode())

        # すでに1度でもインポート済みの場合は、処理しない
        ret_is_import = is_already_imported(host, auth, init_auth)
        if ret_is_import == 200:
            logger.debug("ITA initialize Imported.(success)")
            response = {
                "result": "200",
                "output": "",
                "datetime": datetime.datetime.now(pytz.timezone('Asia/Tokyo')).strftime('%Y/%m/%d %H:%M:%S'),
            }
            return JsonResponse(response, status=200)

        # 一度もインポートしていないときに処理する
        if ret_is_import == 0:
            # *-*-*-* インポート実行(初期パスワードで実行) *-*-*-*
            task_id = import_process(host, init_auth)

            # *-*-*-* インポート結果確認 *-*-*-*
            logger.debug('---- monitoring import dialog ----')

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
                logger.debug("monitoring...")
                logger.debug(datetime.datetime.now(pytz.timezone('Asia/Tokyo')).strftime('%Y/%m/%d %H:%M:%S'))
                time.sleep(3)

                # リクエスト送信
                dialog_response = requests.post('http://' + host + '/default/menu/07_rest_api_ver1.php?no=2100000213', headers=header, data=json_data)
                if dialog_response.status_code != 200:
                    raise Exception(dialog_response)

                # ファイルがあるメニューのため、response.textをデバッグ出力すると酷い目にあう
                # print(dialog_response.text)

                dialog_resp_data = json.loads(dialog_response.text)
                if dialog_resp_data["status"] != "SUCCEED" or dialog_resp_data["resultdata"]["CONTENTS"]["RECORD_LENGTH"] != 1:
                    raise Exception(dialog_response.text)

                record = dialog_resp_data["resultdata"]["CONTENTS"]["BODY"][1]
                logger.debug(json.dumps(record))
                if record[3] == u"完了(異常)":
                    raise Exception("ITAのメニューインポートに失敗しました")
                if record[3] == u"完了":
                    break

                # timeout
                current_time = time.time()
                if (current_time - start_time) > WAIT_ITA_IMPORT:
                    logger.debug("ITA menu import Time out")
                    response = {
                        "result": "500",
                        "output": "ITAメニューインポート状況確認 Time out",
                        "datetime": datetime.datetime.now(pytz.timezone('Asia/Tokyo')).strftime('%Y/%m/%d %H:%M:%S'),
                    }
                    return JsonResponse(response, status=500)

        # *-*-*-* パスワード変更 *-*-*-*
        command = "mysql -u {} -p{} {} -e'UPDATE A_ACCOUNT_LIST".format(ita_db_user, ita_db_password, ita_db_name) + \
                    " SET PASSWORD = \"{}\"".format(hashlib.md5((user_pass).encode()).hexdigest()) + \
                    " WHERE USER_ID = 1;'"
        stdout_ita = subprocess.check_output(["kubectl", "exec", "-i", "-n", namespace, "deployment/it-automation", "--", "bash", "-c", command], stderr=subprocess.STDOUT)

        # *-*-*-* EPOCHユーザー更新 *-*-*-*
        command = "mysql -u {} -p{} {} -e'UPDATE A_ACCOUNT_LIST".format(ita_db_user, ita_db_password, ita_db_name) + \
                    " SET USERNAME = \"{}\"".format(access_info["ITA_EPOCH_USER"]) + \
                    " , PASSWORD = \"{}\"".format(hashlib.md5((access_info["ITA_EPOCH_PASSWORD"]).encode()).hexdigest()) + \
                    " , PW_LAST_UPDATE_TIME = \"2999-12-31 23:59:58\"" + \
                    " WHERE USER_ID = 2;'"
        stdout_ita = subprocess.check_output(["kubectl", "exec", "-i", "-n", namespace, "deployment/it-automation", "--", "bash", "-c", command], stderr=subprocess.STDOUT)

        # *-*-*-* 結果 *-*-*-*
        logger.debug("ITA initialize finished.(success)")
        response = {
            "result": "200",
            "output": "",
            "datetime": datetime.datetime.now(pytz.timezone('Asia/Tokyo')).strftime('%Y/%m/%d %H:%M:%S'),
        }
        return JsonResponse(response, status=200)

    except Exception as e:
        logger.debug(e)
        logger.debug("traceback:" + traceback.format_exc())
        response = {
            "result": "500",
            "output": traceback.format_exc(),
            "datetime": datetime.datetime.now(pytz.timezone('Asia/Tokyo')).strftime('%Y/%m/%d %H:%M:%S'),
        }
        return JsonResponse(response, status=500)


def is_already_imported(host, auth, init_auth):

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
        raise Exception(dialog_response)

    if dialog_response.status_code == 200:
        dialog_resp_data = json.loads(dialog_response.text)
        if dialog_resp_data["resultdata"]["CONTENTS"]["RECORD_LENGTH"] > 0:
            return 200
        else:
            # パスワード変更済み、かつインポートデータが無い状態は異常である
            raise Exception('')

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
        raise Exception(dialog_response)

    if dialog_response.status_code == 200:
        # 初期パスワードで認証通る場合は、インポート前状態として判定する
        return 0

    # *-*-*-* システムが認識している以外のパスワードになっている *-*-*-*
    raise Exception('')


def import_process(host, auth):

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

    logger.debug('---- upload kym file ----')

    kym_file_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/resource/ita_kym/epoch_initialize.kym"
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

    logger.debug('---- ita file upload ---- HOST:' + host)
    # リクエスト送信
    upload_response = requests.post('http://' + host + '/default/menu/07_rest_api_ver1.php?no=2100000212', headers=header, data=json_data)
    if upload_response.status_code != 200:
        logger.debug(upload_response.text)
        raise Exception(upload_response)

    # print(upload_response.text)

    up_resp_data = json.loads(upload_response.text)
    if up_resp_data["status"] != "SUCCEED":
        raise Exception(upload_response.text)

    upload_id = up_resp_data["resultdata"]["upload_id"]
    logger.debug('upload_id: ' + upload_id)

    menu_items = up_resp_data["resultdata"]["IMPORT_LIST"].items()

    return upload_id, upload_filename, menu_items


def import_execute(host, auth, upload_id, menu_list, upload_filename):
    logger.debug('---- execute menu import ----')

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
        raise Exception(exec_response)

    logger.debug(exec_response.text)

    exec_resp_data = json.loads(exec_response.text)
    if exec_resp_data["status"] != "SUCCEED" or exec_resp_data["resultdata"]["RESULTCODE"] != "000":
        raise Exception(exec_response.text)

    task_id = exec_resp_data["resultdata"]["TASK_ID"]
    logger.debug('task_id: ' + task_id)

    return task_id


def is_ita_pod_running(namespace):

    stdout_pod_describe = subprocess.check_output(["kubectl", "get", "pods", "-n", namespace, "-l", "app=it-automation", "-o", "json"], stderr=subprocess.STDOUT)

    # pod_describe = yaml.load(stdout_pod_describe)
    pod_describe = json.loads(stdout_pod_describe)
    # logger.debug('--- stdout_pod_describe ---')
    # logger.debug(stdout_pod_describe)

    return (pod_describe['items'][0]['status']['phase'] == "Running")
