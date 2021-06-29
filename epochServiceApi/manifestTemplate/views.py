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
import logging

from django.shortcuts import render
from django.http import HttpResponse
from django.http.response import JsonResponse

from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

logger = logging.getLogger('apilog')

@require_http_methods(['POST', 'GET'])
@csrf_exempt    
def file_id_not_assign(request, workspace_id):

    logger.debug("CALL file_id_not_assign [{}]: workspace_id:{}".format(request.method, workspace_id))

    if request.method == 'POST':
        return post(request, workspace_id)
    else:
        return index(request, workspace_id)

@csrf_exempt    
def post(request, workspace_id):
    try:

        logger.debug("CALL FilePost:{}".format(workspace_id))

        apiInfo = os.environ['EPOCH_RESOURCE_PROTOCOL'] + "://" + os.environ['EPOCH_RESOURCE_HOST'] + ":" + os.environ['EPOCH_RESOURCE_PORT'] 

        # ヘッダ情報
        post_headers = {
            'Content-Type': 'application/json',
        }

        # データ情報(追加用)
        post_data_add = {
            "manifests": [

            ]
        }

        # データ情報(更新用)
        post_data_upd = {
            "manifests": [

            ]
        }

        # Resource API呼び出し(全件取得)
        response = requests.get( apiInfo + "/workspace/" + str(workspace_id) + "/manifests", headers=post_headers)

        # 戻り値が正常値以外の場合は、処理を終了
        if response.status_code != 200:
            raise Exception("CALL responseAPI /manifests Error")

        ret_manifests = json.loads(response.text)
        logger.debug("get Filedata ------------------ S")
        logger.debug(ret_manifests["rows"])
        logger.debug("get Filedata ------------------ E")

        # 送信されたマニフェストファイル数分処理する
        for manifest_file in request.FILES.getlist('manifest_files'):

            with manifest_file.file as f:

                file_text = ''

                # ↓ 2重改行になっているので、変更するかも ↓
                for line in f.readlines():

                    file_text += line.decode('utf-8')

            # ファイル情報(manifest_data)
            manifest_data = {
                "file_name": manifest_file.name,
                "file_text": file_text
            }

            # 同一ファイルがあるかファイルIDを取得
            file_id = getFileID(ret_manifests["rows"], manifest_file.name)
            
            # 同一ファイル名が登録されている場合は、更新とする
            if not file_id:
                # データ登録情報(manifest_dataと結合)
                post_data_add['manifests'].append(manifest_data)
            else:
                manifest_data["file_id"] = file_id 
                # データ更新情報(manifest_dataと結合)
                post_data_upd['manifests'].append(manifest_data)

        logger.debug("post_data_add ------------------ S")
        logger.debug(post_data_add)
        logger.debug("post_data_add ------------------ E")

        logger.debug("post_data_upd ------------------ S")
        logger.debug(post_data_upd)
        logger.debug("post_data_upd ------------------ E")

        # Resource API呼び出し(削除)
        # response = requests.delete( apiInfo + "/workspace/" + str(workspace_id) + "/manifests", headers=post_headers)

        # 更新は１件ずつ実施
        for upd in post_data_upd['manifests']:
            # JSON形式に変換
            post_data = json.dumps(upd)

            # Resource API呼び出し(更新)
            response = requests.put( "{}/workspace/{}/manifests/{}".format(apiInfo, workspace_id, upd["file_id"]), headers=post_headers, data=post_data)

        # JSON形式に変換
        post_data = json.dumps(post_data_add)

        # Resource API呼び出し(登録)
        response = requests.post( apiInfo + "/workspace/" + str(workspace_id) + "/manifests", headers=post_headers, data=post_data)

        # ITA呼び出し
        logger.debug("CALL ita_registration Start")
        response = ita_registration(request, workspace_id)
        logger.debug("CALL ita_registration End response:")
        logger.debug(response)

        # 正常時はmanifest情報取得した内容を返却
        response = {
            "result": "200",
            "rows": response,
            "datetime": datetime.datetime.now(pytz.timezone('Asia/Tokyo')).strftime('%Y/%m/%d %H:%M:%S'),
        }
        return JsonResponse(response, status=200)

    except Exception as e:
        logger.debug(traceback.format_exc())
        response = {
            "result": {
                "code": "500",
                "detailcode": "",
                "output": traceback.format_exc(),
                "datetime": datetime.datetime.now(pytz.timezone('Asia/Tokyo')).strftime('%Y/%m/%d %H:%M:%S'),
            }
        }
        return JsonResponse(response, status=500)

def getFileID(dict, fileName):
    """辞書からfile_nameの値が一致するものがあるかチェックする

    Args:
        dict (json): 検索する対象Json
        fileName (String): 検索対象ファイル名（完全一致）

    Returns:
        String: ファイルID
    """

    try:
        # 戻り値の初期化
        file_id = ""

        for dictP in dict:
            # 該当する文字列が一致した場合は、処理を抜ける
            if dictP["file_name"] == fileName:
                file_id = dictP["id"]
                break

        return file_id

    except Exception:
        raise
    

def ita_registration(request, workspace_id):
    """ITA登録

    Args:
        workspace_id (Int): ワークスペースID

    Returns:
        Json: 設定したManifest情報
    """

    try:

        logger.debug("CALL ita_registration")

        # post先のURL初期化
        resourceProtocol = os.environ['EPOCH_RESOURCE_PROTOCOL']
        resourceHost = os.environ['EPOCH_RESOURCE_HOST']
        resourcePort = os.environ['EPOCH_RESOURCE_PORT']
        apiurl = "{}://{}:{}/workspace/{}/manifests".format(resourceProtocol, resourceHost, resourcePort, workspace_id)

        # ヘッダ情報
        post_headers = {
            'Content-Type': 'application/json',
        }

        logger.debug("CALL responseAPI : url:{}".format(apiurl))
        # Resource API呼び出し
        response = requests.get(apiurl, headers=post_headers)
#        print("CALL responseAPI : response:{}, text:{}".format(response, response.text))

        # 戻り値が正常値以外の場合は、処理を終了
        if response.status_code != 200:
            raise Exception("CALL responseAPI Error")

        # json形式変換
        ret_manifests = json.loads(response.text)
        # print("--------------------------")
        # print("manifest Json")
        # print(response.text)
        # print(ret_manifests['rows'])
#        print(json.loads(manifest_data))
        # print("--------------------------")

        # パラメータ情報(JSON形式)
        cicdProtocol = os.environ['EPOCH_CICD_PROTOCOL']
        cicdHost = os.environ['EPOCH_CICD_HOST']
        cicdPort = os.environ['EPOCH_CICD_PORT']

        send_data = { "manifests": 
            ret_manifests['rows']
        }
        logger.debug("--------------------------")
        logger.debug("send_data:")
        logger.debug(send_data)
        logger.debug("--------------------------")

        send_data = json.dumps(send_data)

        apiurl = "{}://{}:{}/ita/manifestTemplates".format(cicdProtocol, cicdHost, cicdPort)

        # Resource API呼び出し
        response = requests.post( apiurl, headers=post_headers, data=send_data)
        logger.debug("CALL manifestTemplates : status:{}".format(response.status_code))

        # 正常時はmanifest情報取得した内容を返却
        if response.status_code == 200:
            return ret_manifests['rows']
        else:
            raise Exception("post manifestTemplates Error")

    except Exception:
        raise


def index(request, workspace_id):
    try:
        resourceProtocol = os.environ['EPOCH_RESOURCE_PROTOCOL']
        resourceHost = os.environ['EPOCH_RESOURCE_HOST']
        resourcePort = os.environ['EPOCH_RESOURCE_PORT']
        apiurl = "{}://{}:{}/workspace/{}/manifests".format(resourceProtocol, resourceHost, resourcePort, workspace_id)

        return  get_manifests(apiurl)

    except Exception as e:
        response = {
            "result": {
                "code": "500",
                "detailcode": "",
                "output": traceback.format_exc(),
                "datetime": datetime.datetime.now(pytz.timezone('Asia/Tokyo')).strftime('%Y/%m/%d %H:%M:%S'),
            }
        }
        return JsonResponse(response, status=500)


@require_http_methods(['GET', 'POST'])
@csrf_exempt    
def file_id_assign(request, workspace_id, file_id):

    logger.debug("CALL file_id_assign [{}]: workspace_id:{}: file_id:{}".format(request.method, workspace_id, file_id))

    if request.method == 'GET':
        return get(request, workspace_id, file_id)
    else:
        return delete(request, workspace_id, file_id)


def get(request, workspace_id, file_id):

    try:
        resourceProtocol = os.environ['EPOCH_RESOURCE_PROTOCOL']
        resourceHost = os.environ['EPOCH_RESOURCE_HOST']
        resourcePort = os.environ['EPOCH_RESOURCE_PORT']
        apiurl = "{}://{}:{}/workspace/{}/manifests/{}".format(resourceProtocol, resourceHost, resourcePort, workspace_id, file_id)

        return  get_manifests(apiurl)

    except Exception as e:
        response = {
            "result": {
                "code": "500",
                "detailcode": "",
                "output": traceback.format_exc(),
                "datetime": datetime.datetime.now(pytz.timezone('Asia/Tokyo')).strftime('%Y/%m/%d %H:%M:%S'),
            }
        }
        return JsonResponse(response, status=500)


def delete(request, workspace_id, file_id):
    """マニフェスト削除API

    Args:
        request (request): HTTPリクエスト
        workspace_id (int): workspace_id
        file_id (int): file_id

    Returns:
        response: API Response
    """

    try:
        # ヘッダ情報
        headers = {
            'Content-Type': 'application/json',
        }

        # DELETE送信（作成）
        resourceProtocol = os.environ['EPOCH_RESOURCE_PROTOCOL']
        resourceHost = os.environ['EPOCH_RESOURCE_HOST']
        resourcePort = os.environ['EPOCH_RESOURCE_PORT']
        apiurl = "{}://{}:{}/workspace/{}/manifests/{}".format(resourceProtocol, resourceHost, resourcePort, workspace_id, file_id)

        response = requests.delete(apiurl, headers=headers)

        if response.status_code == 200 and isJsonFormat(response.text):
            # 取得したJSON結果が正常でない場合、例外を返す
            # ret = json.loads(response.text)
            # return JsonResponse(ret, status=200)
            pass

        elif response.status_code == 404:
            response = {
                "result": {
                    "detailcode": "",
                    "output": response.text,
                    "datetime": datetime.datetime.now(pytz.timezone('Asia/Tokyo')).strftime('%Y/%m/%d %H:%M:%S'),
                }
            }
            return JsonResponse(response, status=404)
        else:
            response = {
                "result": {
                    "detailcode": "",
                    "output": response.text,
                    "datetime": datetime.datetime.now(pytz.timezone('Asia/Tokyo')).strftime('%Y/%m/%d %H:%M:%S'),
                }
            }
            return JsonResponse(response, status=500)

        # ITA呼び出し
        logger.debug("CALL ita_registration Start")
        response = ita_registration(request, workspace_id)
        logger.debug("CALL ita_registration End response:")
        logger.debug(response)

        # 正常時はmanifest情報取得した内容を返却
        response = {
            "result": "200",
            "rows": response,
            "datetime": datetime.datetime.now(pytz.timezone('Asia/Tokyo')).strftime('%Y/%m/%d %H:%M:%S'),
        }
        return JsonResponse(response, status=200)

    except Exception as e:
        response = {
            "result": {
                "code": "500",
                "detailcode": "",
                "output": traceback.format_exc(),
                "datetime": datetime.datetime.now(pytz.timezone('Asia/Tokyo')).strftime('%Y/%m/%d %H:%M:%S'),
            }
        }
        return JsonResponse(response, status=500)


def get_manifests(url):
    """manifest 取得共通

    Args:
        url (str): HTTP Get URL

    Returns:
        response: API Response
    """
    # ヘッダ情報
    headers = {
        'Content-Type': 'application/json',
    }

    # GET送信（作成）
    response = requests.get(url, headers=headers)

    output = []
    if response.status_code == 200 and isJsonFormat(response.text):
        logger.debug("get_manifests return --------------------")
        # 取得したJSON結果が正常でない場合、例外を返す
        ret = json.loads(response.text)
        logger.debug(ret)
        logger.debug("--------------------")
        return JsonResponse(ret, status=200)

    elif response.status_code == 404:
        response = {
            "result": {
                "detailcode": "",
                "output": response.text,
                "datetime": datetime.datetime.now(pytz.timezone('Asia/Tokyo')).strftime('%Y/%m/%d %H:%M:%S'),
            }
        }
        return JsonResponse(response, status=404)
    else:
        response = {
            "result": {
                "detailcode": "",
                "output": response.text,
                "datetime": datetime.datetime.now(pytz.timezone('Asia/Tokyo')).strftime('%Y/%m/%d %H:%M:%S'),
            }
        }
        return JsonResponse(response, status=500)

def isJsonFormat(line):
    """Jsonフォーマットチェック

    Args:
        line (Json): Json値を確かめる値

    Returns:
        bool: True:Json, False:Json形式以外
    """
    try:
        json.loads(line)
    except json.JSONDecodeError as e:
        logger.debug(sys.exc_info())
        logger.debug(e)
        return False
    # 以下の例外でも捕まえるので注意
    except ValueError as e:
        logger.debug(sys.exc_info())
        logger.debug(e)
        return False
    except Exception as e:
        logger.debug(sys.exc_info())
        logger.debug(e)
        return False
    return True


