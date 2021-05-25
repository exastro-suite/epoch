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

from django.shortcuts import render
from django.http import HttpResponse
from django.http.response import JsonResponse

from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

@require_http_methods(['POST', 'GET'])
@csrf_exempt    
def file_id_not_assign(request, workspace_id):
    
    response = {
            "result":"200",
            "workspace_id" :workspace_id,
    }

    return JsonResponse(response, status=200)


@require_http_methods(['GET', 'DELETE'])
@csrf_exempt    
def file_id_assign(request, workspace_id, file_id):

    response = {
            "result":"200",
            "workspace_id": workspace_id, 
            "file_id" :file_id,
    }

    return JsonResponse(response, status=200)
