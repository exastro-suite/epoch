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

from flask import Flask, request, abort, jsonify, render_template
from datetime import datetime
import os
import json
import tempfile
import subprocess
import time
import re
from urllib.parse import urlparse
import base64
import requests
from requests.auth import HTTPBasicAuth
import traceback
from datetime import timedelta, timezone

import globals
import common

# GitLab api url
API_PROTOCOL = "http"
API_BASE_URL = "gitlab-webservice-default.gitlab.svc"
API_PORT = "8181"

# 設定ファイル読み込み・globals初期化
app = Flask(__name__)
app.config.from_envvar('CONFIG_API_INSIDE_GITLAB_PATH')
globals.init(app)

@app.route('/alive', methods=["GET"])
def alive():
    """死活監視

    Returns:
        Response: HTTP Respose
    """
    return jsonify({"result": "200", "time": str(datetime.now(globals.TZ))}), 200


@app.route('/workspace/<int:workspace_id>/gitlab/pod', methods=['POST'])
def post_gitlab_pod(workspace_id):
    """GitLab pod生成

    Args:
        workspace_id (int): ワークスペースID

    Returns:
        Response: HTTP Respose
    """
    globals.logger.debug('CALL post_gitlab_pod:{}'.format(workspace_id))

    try:
        return jsonify({"result": "200"}), 200

    except Exception as e:
        return common.serverError(e)

@app.route('/workspace/<int:workspace_id>/gitlab/initialize', methods=['POST'])
def post_gitlab_initialize(workspace_id):
    """GitLab 初期設定

    Args:
        workspace_id (int): ワークスペースID

    Returns:
        Response: HTTP Respose
    """
    globals.logger.debug('CALL post_gitlab_initialize:{}'.format(workspace_id))

    try:
        return jsonify({"result": "200"}), 200

    except Exception as e:
        return common.serverError(e)

@app.route('/workspace/<int:workspace_id>/gitlab/webhooks', methods=['POST'])
def post_gitlab_webhooks(workspace_id):
    """GitLab webhooks設定

    Args:
        workspace_id (int): ワークスペースID

    Returns:
        Response: HTTP Respose
    """
    globals.logger.debug('CALL post_gitlab_webhooks:{}'.format(workspace_id))

    try:
        return jsonify({"result": "200"}), 200

    except Exception as e:
        return common.serverError(e)

@app.route('/workspace/<int:workspace_id>/gitlab/repos', methods=['POST'])
def post_gitlab_repos(workspace_id):
    """GitLab リポジトリ作成

    Args:
        workspace_id (int): ワークスペースID

    Returns:
        Response: HTTP Respose
    """
    globals.logger.debug('CALL post_gitlab_repos:{}'.format(workspace_id))

    try:
        #
        # パラメータ項目設定
        #
        user = request.json['git_repositry']['user']
        token = request.json['git_repositry']['token']
        url = request.json['git_repositry']['url']

        # リポジトリの存在チェック
        ret_exists = exists_repositry(user, token, url)
        # すでにリポジトリが存在したので200で終了
        if ret_exists:
            return jsonify({"result": "200"}), 200

        # グループID取得
        url_group_id = get_group_id(user, token, url)
        # すでにリポジトリが存在したので200で終了
        if url_group_id is None:
            Exception("group not found")

        # ヘッダ情報
        post_headers = {
            'PRIVATE-TOKEN': token,
            'Content-Type': 'application/json',
        }

        # 引数をJSON形式で構築
        post_data = json.dumps({
            "name": url_name,
            "public": "true",
            "namespace_id": url_group_id,
        })


        api_url = "{}://{}:{}/api/v4/projects".format(API_PROTOCOL, API_BASE_URL, API_PORT)
        # create projectのPOST送信
        response = requests.post(api_url, headers=post_headers, data=post_data)

        globals.logger.debug('code: {}, message: {}'.format(str(response.status_code), response.text))
        # if response.status_code == 204:
        #     globals.logger.debug('SonarQube password change SUCCEED')
        # if response.status_code == 401:
        #     globals.logger.debug('SonarQube password has already changed')

        return jsonify({"result": "201"}), 201

    except Exception as e:
        return common.serverError(e)

def exists_repositry(user, token, url):
    """リポジトリの存在チェック

    Args:
        user (str): ユーザーID
        token (str): token
        url (str): リポジトリURL

    Returns:
        bool: True:あり、False:なし
    """
    # ヘッダ情報
    post_headers = {
        'PRIVATE-TOKEN': token,
        'Content-Type': 'application/json',
    }

    # URLの分割
    json_url = get_url_split(url)

    api_url = "{}://{}:{}/api/v4/projects/{}%2F{}".format(API_PROTOCOL, API_BASE_URL, API_PORT,json_url['group_name'],json_url['repos_name'])

    # 単一のプロジェクトを取得する
    response = requests.get(api_url, headers=post_headers)

    # リポジトリが存在する場合はTrueを返す
    if response.status_code == 200:
        ret = True

    # リポジトリが存在しなかったらFalseを返す
    elif response.status_code == 404:
        ret = False

    # それ以外はrepository errorを返す
    else:
        Exception("repository error")

    return ret

def get_group_id(user, token, url):
    """グループID 取得

    Args:
        user (str): ユーザーID
        token (str): token
        url (str): リポジトリURL

    Returns:
        int: group_id(namespace_id)
    """
    return None

def get_url_split(url):
    """urlの解析分割

    Args:
        url (str): url

    Returns:
        json: URLをbase_url, group_name, repos_nameに分割した値
    """
    # 正規表現を使って、urlからグループ名、レポジトリ名を取得する
    group_name = re.sub('\\.git$','',re.sub('^https?://[^/][^/]*/','',url))
    repos_name = re.sub('\\.git$','',re.sub('^https?://[^/][^/]*/','',url))



    json_url = {
        "base_url": "xxx",
        "group_name": "xxx",
        "repos_name": "xxx",
    }

    return json_url


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('API_INSIDE_GITLAB_PORT', '8000')), threaded=True)
