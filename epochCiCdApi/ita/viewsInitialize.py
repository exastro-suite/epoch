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

from django.shortcuts import render
from django.http import HttpResponse
from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

@require_http_methods(['POST'])
@csrf_exempt
def post(request):

    print("CALL " + __name__)
    try:
        # パラメータ情報(JSON形式)
        payload = json.loads(request.body)

        host = payload["itaInfo"]["host"]
        user_id = payload["itaInfo"]["userId"]
        user_pass = payload["itaInfo"]["userPass"]

        auth = base64.b64encode((user_id + ':' + user_pass).encode())

        # *-*-*-* ファイルアップロード *-*-*-*
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

        # リクエスト送信
        upload_response = requests.post('http://' + host + '/default/menu/07_rest_api_ver1.php?no=2100000212', headers=header, data=json_data)
        if upload_response.status_code != 200:
            raise Exception

        print(upload_response.text)

        up_resp_data = json.loads(upload_response.text)
        if up_resp_data["status"] != "SUCCEED":
            raise Exception

        upload_id = up_resp_data["resultdata"]["upload_id"]

        # menu_list再構築
        menu_list = {}
        for menu_group_id, menu_group_detail in up_resp_data["resultdata"]["IMPORT_LIST"].items():
            if menu_group_id in menu_list:
                menu_id_list = menu_list[menu_group_id]
            else:
                menu_id_list = []

            for menu_detail in menu_group_detail["menu"]:
                menu_id_list.append(int(menu_detail["menu_id"]))

            menu_list[menu_group_id] = menu_id_list

        print(menu_list)

        # *-*-*-* インポート実行 *-*-*-*

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
            raise Exception

        print(exec_response.text)

        exec_resp_data = json.loads(exec_response.text)
        if exec_resp_data["status"] != "SUCCEED" or exec_resp_data["resultdata"]["RESULTCODE"] != "000":
            raise Exception(exec_response.text)

        task_id = exec_resp_data["resultdata"]["TASK_ID"]

        # *-*-*-* インポート結果確認 *-*-*-*

        # # POST送信する
        # # ヘッダ情報
        # header = {
        #     'host': host,
        #     'Content-Type': 'application/json',
        #     'Authorization': auth,
        #     'X-Command': 'FILTER',
        # }

        # # 実行パラメータ設定
        # data = {
        #     "2": {
        #         "LIST": [task_id]
        #     }
        # }

        # # json文字列に変換（"utf-8"形式に自動エンコードされる）
        # json_data = json.dumps(data)

        # i = 1
        # while True:
        #     i += 1
        #     print("状態監視: " + datetime.datetime.now(pytz.timezone('Asia/Tokyo')))
        #     sleep(1)

        #     # リクエスト送信
        #     dialog_response = requests.post('http://' + host + '/default/menu/07_rest_api_ver1.php?no=2100000213', headers=header, data=json_data)
        #     if dialog_response.status_code != 200:
        #         raise Exception

        #     print(dialog_response.text)

        #     dialog_resp_data = json.loads(dialog_response.text)
        #     if dialog_resp_data["status"] != "SUCCEED" or dialog_resp_data["CONTENTS"]["RECORD_LENGTH"] != 1:
        #         raise Exception(dialog_response.text)

        #     if dialog_resp_data["CONTENTS"]

        #     # dev safety break
        #     if i > 100:
        #         break


        # *-*-*-* 結果 *-*-*-*

        response = {
            "result": "200",
            "output": task_id,
            "datetime": datetime.datetime.now(pytz.timezone('Asia/Tokyo')).strftime('%Y/%m/%d %H:%M:%S'),
        }
        return JsonResponse(response, status=200)

    except Exception as e:
        response = {
            "result": "500",
            "output": traceback.format_exc(),
            "datetime": datetime.datetime.now(pytz.timezone('Asia/Tokyo')).strftime('%Y/%m/%d %H:%M:%S'),
        }
        return JsonResponse(response, status=500)