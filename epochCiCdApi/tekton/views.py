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
import logging

from django.shortcuts import render
from django.http import HttpResponse
from django.http.response import JsonResponse

from django.views.decorators.csrf import csrf_exempt

from kubernetes import client, config
import yaml
from pprint import pprint

logger = logging.getLogger('apilog')

@csrf_exempt
def index(request):

    logger.debug ("CALL tekton : {}".format(request.method))

    if request.method == 'POST':
        return post(request)
    else:
        return ""

@csrf_exempt    
def post(request):
    try:

        resource_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/resource"

        stdout_pl = subprocess.check_output(["kubectl","apply","-f",(resource_dir + "/tekton_pipeline-release.yaml")],stderr=subprocess.STDOUT)
        stdout_tg = subprocess.check_output(["kubectl","apply","-f",(resource_dir + "/tekton_trigger-release.yaml")],stderr=subprocess.STDOUT)
        stdout_db = subprocess.check_output(["kubectl","apply","-f",(resource_dir + "/tekton_dashbord-release.yaml")],stderr=subprocess.STDOUT)

        response = {
            "result":"OK",
            "output" : [
                stdout_pl.decode('utf-8'),
                stdout_tg.decode('utf-8'),
                stdout_db.decode('utf-8'),
            ],
        }
        return JsonResponse(response)

    except subprocess.CalledProcessError as e:
        response = {
            "result":"ERROR",
            "returncode": e.returncode,
            "command": e.cmd,
            "output": e.output.decode('utf-8'),
            "traceback": traceback.format_exc(),
        }
        return JsonResponse(response)

