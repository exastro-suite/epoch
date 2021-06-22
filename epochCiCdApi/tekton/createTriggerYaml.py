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
import shutil

from django.shortcuts import render
from django.http import HttpResponse
from django.http.response import JsonResponse

from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def index(request):
    if request.method == 'POST':
        return post(request)
    else:
        return ""

@csrf_exempt    
def post(request):
    try:

        # 引数で指定されたCD環境を取得
        print (request.body)
        request_json = json.loads(request.body)
        print (request_json)
        request_ci_config = request_json["ci_config"]

        templates_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/resource/templates/tekton-trigger"
        resource_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/resource/conv/tekton-trigger"

        # 対象となるYamlを定義
        yamls = [ "build-and-push-trigger-template.yaml",
                  "front-end-trigger-binding.yaml",
                  "github-push-trigger-binding.yaml",
                  "gitlab-push-listener.yaml",
                  "gitlab-push-trigger-binding.yaml" ]

        output_data = ""

        for yaml_name in yamls:
            conv(templates_dir + "/" + yaml_name,
                resource_dir + "/" + yaml_name,
                request_ci_config)

            try:
                stdout = subprocess.check_output(["kubectl","apply","-f",resource_dir +  "/" + yaml_name],stderr=subprocess.STDOUT)

                output_data += "{" + stdout.decode('utf-8') + "},"

            except subprocess.CalledProcessError as e:
                response = {
                    "result":"ERROR",
                    "returncode": e.returncode,
                    "command": e.cmd,
                    "output": e.output.decode('utf-8'),
                    "traceback": traceback.format_exc(),
                }
                return JsonResponse(response)

        response = {
            "result":"201",
            "output" : [ output_data ],
        }
        return JsonResponse(response)

    except Exception as e:
        response = {
            "result":"ERROR",
            "returncode": e.returncode,
            "command": e.cmd,
            "output": e.output.decode('utf-8'),
            "traceback": traceback.format_exc(),
        }
        return JsonResponse(response)

@csrf_exempt    
def conv(template_yaml, dest_yaml, json_ci_config):

    # 実行yamlの保存
    shutil.copy(template_yaml, dest_yaml)
        
    # 実行yamlを読み込む
    with open(dest_yaml, encoding="utf-8") as f:
        data_lines = f.read()

    # アプリケーションコードは１つのみ有効(複数対応待ち)
    json_pipelines = json_ci_config["pipelines"]["0"]

    # 文字列置換
    # data_lines = data_lines.replace("<__registry_imagetag__>", json_ci_config["registry"]["imageTag"]) # imageTagは不要に
    data_lines = data_lines.replace("<__registry_url__>", json_pipelines["contaier_registry"]["image"])
  
    # 同じファイル名で保存
    with open(dest_yaml, mode="w", encoding="utf-8") as f:
        f.write(data_lines)

