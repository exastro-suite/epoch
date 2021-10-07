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
import base64
import io
import logging

from django.shortcuts import render
from django.http import HttpResponse
from django.http.response import JsonResponse

from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from epochCiCdApi.views_access import get_access_info

ita_host = os.environ['EPOCH_ITA_HOST']
ita_port = os.environ['EPOCH_ITA_PORT']

# メニューID
ite_menu_operation = '2100000304'

ita_restapi_endpoint='http://' + ita_host + ':' + ita_port + '/default/menu/07_rest_api_ver1.php'

logger = logging.getLogger('apilog')

@require_http_methods(['GET'])
@csrf_exempt
def index(request):
#   sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    logger.debug("CALL " + __name__ + ":{}".format(request.method))

    if request.method == 'GET':
        return get(request)
    else:
        return ""

@csrf_exempt
def get(request):

    # ワークスペース複数化するまでは1固定
    workspace_id = 1

    # ワークスペースアクセス情報取得
    access_info = get_access_info(workspace_id)

    ita_user = access_info['ITA_USER']
    ita_pass = access_info['ITA_PASSWORD']

    # HTTPヘッダの生成
    filter_headers = {
        'host': ita_host + ':' + ita_port,
        'Content-Type': 'application/json',
        'Authorization': base64.b64encode((ita_user + ':' + ita_pass).encode()),
        'X-Command': 'FILTER',
    }

    #
    # オペレーションの取得
    #
    opelist_resp = requests.post(ita_restapi_endpoint + '?no=' + ite_menu_operation, headers=filter_headers)
    opelist_json = json.loads(opelist_resp.text)
    logger.debug('---- Operation ----')
    logger.debug(opelist_resp.text)

    return JsonResponse(opelist_json, status=200)
