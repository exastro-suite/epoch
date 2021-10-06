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

import cgi # CGIモジュールのインポート
import cgitb
import sys
import requests
import json
import subprocess
import traceback
import os
import logging
import re
import random
import string

from django.shortcuts import render
from django.http import HttpResponse
from django.http.response import JsonResponse

from django.views.decorators.csrf import csrf_exempt

from . import views_access

logger = logging.getLogger("apilog")

@csrf_exempt
def index(request, workspace_id):

    logger.debug ("CALL workspace.init_data : method:{}, workspace_id:{}".format(request.method, workspace_id))

    if request.method == "POST":
        return post(request, workspace_id)
    else:
        return ""

@csrf_exempt    
def post(request, workspace_id):
    try:
        # ワークスペースの初期設定

        # アクセス情報設定を呼び出し 戻り値をそのまま返却する
        ret = views_access.index(request, workspace_id)
        return ret
        
    except Exception as e:
        logger.debug("Exception workspace.initialize")
        logger.debug("- traceback.format_exc")
        logger.debug(traceback.format_exc())

        response = {
            "result": "500",
            "output": traceback.format_exc(),
        }
        return JsonResponse(response, status=500)
