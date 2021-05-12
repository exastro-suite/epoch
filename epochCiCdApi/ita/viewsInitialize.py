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
        with open(kym_file_path, 'r') as f:
            kym_binary = f.read()
        encoded_data = base64.b64encode(kym_binary)

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
                "name": os.path.basename(kym_file_path),
                "base64": encoded_data,
            }
        }

        # json文字列に変換（"utf-8"形式に自動エンコードされる）
        json_data = json.dumps(data)

        # リクエスト送信
        upload_response = requests.post('http://' + host + '/default/menu/07_rest_api_ver1.php?no=2100000212', headers=header, data=json_data)
        if upload_response.status_code != 200:
            riase Exception

        print(upload_response)

        up_resp_data = json.loads(exec_response.text)
        if up_resp_data["status"] != "SUCCEED":
            riase Exception

        upload_id = up_resp_data["resultdata"]["upload_id"]

        # menu_list再構築
        menu_list = {}
        for menu_group_id, menu_group_detail as up_resp_data["resultdata"]["IMPORT_LIST"].items():
            if menu_group_id in menu_list:
                menu_id_list = menu_list[menu_group_id]
            else:
                menu_id_list = []

        # *-*-*-* インポート実行 *-*-*-*

        # # POST送信する
        # # ヘッダ情報
        # header = {
        #     'host': host,
        #     'Content-Type': 'application/json',
        #     'Authorization': auth,
        #     'X-Command': 'EXECUTE',
        # }

        # # 実行パラメータ設定
        # data = {
        #     "CONDUCTOR_CLASS_NO": conductor_class_no,
        #     "OPERATION_ID": operation_id,
        #     "PRESERVE_DATETIME": preserve_datetime,
        # }

        # # json文字列に変換（"utf-8"形式に自動エンコードされる）
        # json_data = json.dumps(data)

        # # リクエスト送信
        # exec_response = requests.post('http://' + host + '/default/menu/07_rest_api_ver1.php?no=2100000212', headers=header, data=json_data)

        # *-*-*-* 結果 *-*-*-*

        response = {
            "result": "200",
            # "output": exec_response.text,
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
