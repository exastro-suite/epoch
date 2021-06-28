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

import requests
import json
import traceback
import os
import datetime, pytz
import base64
import logging

from django.shortcuts import render
from django.http import HttpResponse
from django.http.response import JsonResponse

from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

ita_host = os.environ['EPOCH_ITA_HOST']
ita_port = os.environ['EPOCH_ITA_PORT']
ita_user = os.environ['EPOCH_ITA_USER']
ita_pass = os.environ['EPOCH_ITA_PASSWORD']

# メニューID
ite_menu_operation = '2100000304'
ita_menu_manifest_template = '2100040704'

ita_restapi_endpoint='http://' + ita_host + ':' + ita_port + '/default/menu/07_rest_api_ver1.php'

logger = logging.getLogger('apilog')

@require_http_methods(['POST'])
@csrf_exempt
def post(request):

    logger.debug("CALL " + __name__)
    # HTTPヘッダの生成
    filter_headers = {
        'host': ita_host + ':' + ita_port,
        'Content-Type': 'application/json',
        'Authorization': base64.b64encode((ita_user + ':' + ita_pass).encode()),
        'X-Command': 'FILTER',
    }

    edit_headers = {
        'host': ita_host + ':' + ita_port,
        'Content-Type': 'application/json',
        'Authorization': base64.b64encode((ita_user + ':' + ita_pass).encode()),
        'X-Command': 'EDIT',
    }

    logger.debug(json.loads(request.body))

    #
    # マニフェストテンプレートの取得
    #
    content = {
        "1": {
            "NORMAL": "0"
        },
        "3": {
            "NORMAL": "TPF_epoch_template_yaml"
        },
    }
    manitpl_resp = requests.post(ita_restapi_endpoint + '?no=' + ita_menu_manifest_template, headers=filter_headers, data=json.dumps(content))
    manitpl_json = json.loads(manitpl_resp.text)
    logger.debug('---- Current Manifest Templates ----')
    # logger.debug(manitpl_resp.text)
    logger.debug(manitpl_json)

    req_data = json.loads(request.body)['manifests']
    mani_req_len = len(req_data)
    mani_ita_len = manitpl_json['resultdata']['CONTENTS']['RECORD_LENGTH']
    max_loop_cnt = max(mani_req_len, mani_ita_len)
    logger.debug("max_loop_cnt: " + str(max_loop_cnt))

    ita_data = manitpl_json['resultdata']['CONTENTS']["BODY"]
    ita_data.pop(0)
    logger.debug(ita_data)

    edit_data = {
        "UPLOAD_FILE": []
    }
    tpl_cnt = 0
    for i in range(max_loop_cnt):

        # ITAを廃止
        if i > mani_req_len - 1:
            tmp_data = []
            for j, item in enumerate(ita_data[i]):
                if j == 0:
                    tmp_data.append('廃止')
                else:
                    tmp_data.append(item)

            edit_data[str(i)] = tmp_data

        # ITAに新規登録する
        elif i > mani_ita_len - 1:
            tpl_cnt += 1
            tmp_data = {}
            tmp_data['0'] = "登録"
            tmp_data['3'] = "TPF_epoch_template_yaml" + str(tpl_cnt)
            tmp_data['4'] = req_data[i]["file_name"]
            tmp_data['5'] = "VAR_replicas:\n"\
                            "VAR_image:\n"\
                            "VAR_image_tag:"

            edit_data[str(i)] = tmp_data
            edit_data["UPLOAD_FILE"].append({"4": base64.b64encode(req_data[i]["file_text"].encode()).decode()})

        # ITAを更新する
        else:
            tpl_cnt += 1
            tmp_data = ita_data[i]
            tmp_data[0] = "更新"
            tmp_data[3] = "TPF_epoch_template_yaml" + str(tpl_cnt)
            tmp_data[4] = req_data[i]["file_name"]
            tmp_data[5] = "VAR_replicas:\n"\
                          "VAR_image:\n"\
                          "VAR_image_tag:"

            edit_data[str(i)] = tmp_data
            edit_data["UPLOAD_FILE"].append({"4": base64.b64encode(req_data[i]["file_text"].encode()).decode()})

    logger.debug(edit_data)

    # ITAへREST実行
    manutemplate_edit_resp = requests.post(ita_restapi_endpoint + '?no=' + ita_menu_manifest_template, headers=edit_headers, data=json.dumps(edit_data))
    manitemplate_json = json.loads(manutemplate_edit_resp.text)

    logger.debug(manitemplate_json)

    response = {
        "result": "200",
        "output": "登録に成功しました。",
        "datetime": datetime.datetime.now(pytz.timezone('Asia/Tokyo')).strftime('%Y/%m/%d %H:%M:%S'),
    }

    return JsonResponse(response, status=200)
