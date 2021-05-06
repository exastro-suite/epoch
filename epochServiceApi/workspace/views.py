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
import shutil

from django.shortcuts import render
from django.http import HttpResponse
from django.http.response import JsonResponse

from django.views.decorators.csrf import csrf_exempt

from kubernetes import client, config

@csrf_exempt
def index(request):
    if request.method == 'POST':
        return post(request)
    else:
        return ""

@csrf_exempt    
def post(request):
    try:
        # ヘッダ情報
        headers = {
            'Content-Type': 'application/json',
        }

        templates_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/resource/templates"
        resource_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/resource/conv"

        # データ情報
        data = '{}'
        
        temp_yaml_name = templates_dir + "/epochCiCdApi.yaml"
        conv_yaml_name = resource_dir + "/epochCiCdApi.yaml"
        deploy_config = "/etc/epoch/deploy-config/deployconfig.yaml"
        #deploy_config = "/etc/epoch/deploy-config/deployconfig"

        # パラメータ情報(JSON形式)
        payload = json.loads(request.body)

        # テンプレートの文字列置き換え
        conv(temp_yaml_name, conv_yaml_name)

        apiInfo = payload["clusterInfo"]["apiInfo"]
        output = []
        
        # CI/CD APIコンテナ作成
        stdout = subprocess.check_output(["kubectl","apply","-f",conv_yaml_name, "--kubeconfig=" + deploy_config],stderr=subprocess.STDOUT)

        # CI/CD API Pod状態確認
        config.load_kube_config(deploy_config) 
        v1 = client.CoreV1Api()

        namespace = 'epoch-system'
        # label = 'app=cicd-api'

        start = time.time()
        floop = True
        while floop:
            try:                                                
                time.sleep(1)
                pod_list = v1.list_namespaced_pod(namespace)      
                # pod_list = v1.list_namespaced_pod(namespace, label_selector=label)      
            except ApiException as e:                                                 
                print('Exception when calling CoreV1Api->list_namespaced_pod: %s\n' % e)

            time.sleep(1)
            count = 0
            for pod in pod_list.items:
                if pod.status.phase == 'Running':
                    print('status : ' + pod.status.phase)
                    floop=False
                    break
                elif (time.time() - start) > 60:
                    print('count : ' + count)
                    floop=False
                    break

        time.sleep(10)

        # post送信（tekton/pod作成）
        print('apiInfo : ' + apiInfo)
        response = requests.post(apiInfo + 'tekton/', headers=headers, data=data, params=payload)

        if isJsonFormat(response.text):
            # 取得したJSON結果が正常でない場合、例外を返す
            ret = json.loads(response.text)
            if ret["result"] == "OK":
                output.append(ret["output"])
            else:
                raise Exception
        else:
            response = {
                "result": {
                    "code": "500",
                    "detailcode": "",
                    "output": response.text,
                    "datetime": datetime.datetime.now(pytz.timezone('Asia/Tokyo')).strftime('%Y/%m/%d %H:%M:%S'),
                }
            }
            return JsonResponse(response)

        # post送信（argocd/pod作成）
        response = requests.post(apiInfo + 'argocd/pod', headers=headers, data=data, params=payload)

        if isJsonFormat(response.text):
            # 取得したJSON結果が正常でない場合、例外を返す
            ret = json.loads(response.text)
            if ret["result"] == "OK":
                output.append(ret["output"])
            else:
                raise Exception
        else:
            response = {
                "result": {
                    "code": "500",
                    "detailcode": "",
                    "output": response.text,
                    "datetime": datetime.datetime.now(pytz.timezone('Asia/Tokyo')).strftime('%Y/%m/%d %H:%M:%S'),
                }
            }
            return JsonResponse(response)


        # post送信（ita/pod作成）
        response = requests.post(apiInfo + 'ita/', headers=headers, data=data, params=payload)

        # 取得したJSON結果が正常でない場合、例外を返す
        ret = json.loads(response.text)
        if ret["result"] == "OK":
            output.append(ret["output"])
        else:
            raise Exception

        response = {
            "result": {
                "code": "200",
                "detailcode": "",
                "output": output,
                "datetime": datetime.datetime.now(pytz.timezone('Asia/Tokyo')).strftime('%Y/%m/%d %H:%M:%S'),
            }
        }
        return JsonResponse(response)

    except Exception as e:
        response = {
            "result": {
                "code": "500",
                "detailcode": "",
                "output": traceback.format_exc(),
                "datetime": datetime.datetime.now(pytz.timezone('Asia/Tokyo')).strftime('%Y/%m/%d %H:%M:%S'),
            }
        }
        return JsonResponse(response)

def isJsonFormat(line):
    try:
        json.loads(line)
    except json.JSONDecodeError as e:
        print(sys.exc_info())
        print(e)
        return False
    # 以下の例外でも捕まえるので注意
    except ValueError as e:
        print(sys.exc_info())
        print(e)
        return False
    except Exception as e:
        print(sys.exc_info())
        print(e)
        return False
    return True

@csrf_exempt    
def conv(template_yaml, dest_yaml):

    # 実行yamlの保存
    shutil.copy(template_yaml, dest_yaml)
        
    # 実行yamlを読み込む
    with open(dest_yaml, encoding="utf-8") as f:
        data_lines = f.read()

    epochImage = os.environ['EPOCH_CICD_IMAGE']
    epochPort = os.environ['EPOCH_CICD_PORT']

    # 文字列置換
    data_lines = data_lines.replace("<__epoch_cicd_api_image__>", epochImage)
    data_lines = data_lines.replace("<__epoch_cicd_api_port__>", epochPort)
  
    # 同じファイル名で保存
    with open(dest_yaml, mode="w", encoding="utf-8") as f:
        f.write(data_lines)