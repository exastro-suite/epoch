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
from django.core.files.storage import FileSystemStorage

@require_http_methods(['POST', 'GET'])
@csrf_exempt    
def file_id_not_assign(request, workspace_id):

    if request.method == 'POST':
        return post(request, workspace_id)
    else:
        return index(request, workspace_id)


def post(request, workspace_id):

    # ヘッダ情報
    post_headers = {
        'Content-Type': 'application/json',
    }

    print("******************************************")
    print("request.FILES :  ")
    print(request.FILES)
    print("******************************************")
    print("request.FILES['manifest_files'] : ")
    print(request.FILES['manifest_files'])
    print("******************************************")


    for manifest_file in request.FILES.getlist('manifest_files'):
        with manifest_file.file as f:
            # ↓ 2重改行になっているので、変更するかも ↓
            for line in f.readlines():
                print(line.decode())

    # for manifest_file in request.FILES['manifest_files']:

    #     print("manifest_file : ")
    #     print(manifest_file)
        # with manifest_file.file as f:
        #     for line in f.readlines():
        #         print(line.decode())
        # htmlfile = request.FILES['manifest_files'].file.readlines().decode()
        # print(htmlfile)

        # fileobject = FileSystemStorage()

        # # filedata = fileobject.save(htmlfile.name, htmlfile )

        # upload_url = fileobject.url(data)

        # return render(request, 'upload.html')

    # 
    # request_response = requests.post( apiInfo + "ita/cdExec", headers=post_headers, data=post_data)

    response = {
            "result":"200",
            "workspace_id" :workspace_id,
    }

    return JsonResponse(response, status=200)


def index(request, workspace_id):
    response = {
            "result":"200",
            "workspace_id" :workspace_id,
    }

    return JsonResponse(response, status=200)


@require_http_methods(['GET', 'DELETE'])
@csrf_exempt    
def file_id_assign(request, workspace_id, file_id):

    if request.method == 'GET':
        return get(request, workspace_id, file_id)
    else:
        return delete(request, workspace_id, file_id)


def get(request, workspace_id, file_id):

    response = {
            "result":"200",
            "workspace_id": workspace_id, 
            "file_id" :file_id,
    }

    return JsonResponse(response, status=200)


def delete(request, workspace_id, file_id):

    response = {
            "result":"200",
            "workspace_id": workspace_id, 
            "file_id" :file_id,
    }

    return JsonResponse(response, status=200)
