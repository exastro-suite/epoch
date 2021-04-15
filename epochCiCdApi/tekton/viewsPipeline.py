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

        output_data = []
        # Pipelineの設定
        output = postPipeline(request)
        if output["result"] == "201":
            output_data.append(output["output"])
        else:
            # エラーの場合は、そのまま返す
            return JsonResponse(output)

        # Triggerの設定
        output = postTrigger(request)
        if output["result"] == "201":
            output_data.append(output["output"])
        else:
            # エラーの場合は、そのまま返す
            return JsonResponse(output)

        response = {
            "result":"201",
            "output" : output_data,
        }
        return JsonResponse(response)

    except Exception as e:
        print (e)
        response = {
            "result":"500",
            "returncode": "0101",
            "args": e.args,
            "output": e.args,
            "traceback": traceback.format_exc(),
        }
        return JsonResponse(response)

@csrf_exempt    
def postPipeline(request):
    try:

        # 引数で指定されたCD環境を取得
        print (request.body)
        request_json = json.loads(request.body)
        print (request_json)
        request_build = request_json["build"]

        templates_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/resource/templates/tekton-pipeline"
        resource_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/resource/conv/tekton-pipeline"


        # 対象となるYamlを定義
        yamls = [ "pipeline-build-and-push.yaml",
                  "pipeline-task-git-clone.yaml",
                  "pipeline-task-kaniko.yaml" ]

        output_data = ""

        for yaml_name in yamls:
            # テンプレートの文字列置き換え
            conv(templates_dir + "/" + yaml_name,
                resource_dir + "/" + yaml_name,
                request_build)
        
            try:
                stdout = subprocess.check_output(["kubectl","apply","-f",resource_dir +  "/" + yaml_name],stderr=subprocess.STDOUT)

                output_data += "{" + stdout.decode('utf-8') + "},"

            except subprocess.CalledProcessError as e:
                response = {
                    "result": e.returncode,
                    "returncode": "0103",
                    "command": e.cmd,
                    "output": e.output.decode('utf-8'),
                    "traceback": traceback.format_exc(),
                }
                return (response)

        response = {
            "result":"201",
            "output" : [ output_data ],
        }
        return (response)

    except Exception as e:
        print (e)
        response = {
            "result":"500",
            "returncode": "0102",
            "args": e.args,
            "output": e.args,
            "traceback": traceback.format_exc(),
        }
        return (response)

@csrf_exempt    
def postTrigger(request):
    try:

        # 引数で指定されたCD環境を取得
        print (request.body)
        request_json = json.loads(request.body)
        print (request_json)
        request_build = request_json["build"]

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
            # テンプレートの文字列置き換え
            conv(templates_dir + "/" + yaml_name,
                resource_dir + "/" + yaml_name,
                request_build)

            try:
                stdout = subprocess.check_output(["kubectl","apply","-f",resource_dir +  "/" + yaml_name],stderr=subprocess.STDOUT)

                output_data += "{" + stdout.decode('utf-8') + "},"

            except subprocess.CalledProcessError as e:
                response = {
                    "result": e.returncode,
                    "returncode": "0105",
                    "command": e.cmd,
                    "output": e.output.decode('utf-8'),
                    "traceback": traceback.format_exc(),
                }
                return (response)

        response = {
            "result":"201",
            "output" : [ output_data ],
        }
        return (response)

    except Exception as e:
        print (e)
        response = {
            "result":"500",
            "returncode": "0104",
            "args": e.args,
            "output": e.args,
            "traceback": traceback.format_exc(),
        }
        return (response)

@csrf_exempt    
def conv(template_yaml, dest_yaml, json_build):

    # 実行yamlの保存
    shutil.copy(template_yaml, dest_yaml)
        
    # 実行yamlを読み込む
    with open(dest_yaml, encoding="utf-8") as f:
        data_lines = f.read()

    # 文字列置換
    data_lines = data_lines.replace("<__build_registry_imageTag__>", json_build["registry"]["imageTag"])
    data_lines = data_lines.replace("<__build_registry_url__>", json_build["registry"]["url"])
    data_lines = data_lines.replace("<__build_pathToContext__>", json_build["pathToContext"])
    data_lines = data_lines.replace("<__build_pathToDockerfile__>", json_build["pathToDockerfile"])
    data_lines = data_lines.replace("<__build_git_url__>", json_build["git"]["url"])
    data_lines = data_lines.replace("<__build_git_branch__>", json_build["git"]["branch"])

    data_lines = data_lines.replace("<__http_proxy__>", os.environ['EPOCH_HTTP_PROXY'])
    data_lines = data_lines.replace("<__https_proxy__>", os.environ['EPOCH_HTTPS_PROXY'])
    data_lines = data_lines.replace("<__no_proxy__>", os.environ['EPOCH_NO_PROXY'])

    # 同じファイル名で保存
    with open(dest_yaml, mode="w", encoding="utf-8") as f:
        f.write(data_lines)

