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
import inspect
import os
import json
import tempfile
import subprocess
import time
import re
import urllib.parse 
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


# @app.route('/workspace/<int:workspace_id>/gitlab/pod', methods=['POST'])
# def post_gitlab_pod(workspace_id):
#     """GitLab pod生成

#     Args:
#         workspace_id (int): ワークスペースID

#     Returns:
#         Response: HTTP Respose
#     """
#     globals.logger.debug('CALL post_gitlab_pod:{}'.format(workspace_id))

#     try:
#         return jsonify({"result": "200"}), 200

#     except Exception as e:
#         return common.serverError(e)

# @app.route('/workspace/<int:workspace_id>/gitlab/initialize', methods=['POST'])
# def post_gitlab_initialize(workspace_id):
#     """GitLab 初期設定

#     Args:
#         workspace_id (int): ワークスペースID

#     Returns:
#         Response: HTTP Respose
#     """
#     globals.logger.debug('CALL post_gitlab_initialize:{}'.format(workspace_id))

#     try:
#         return jsonify({"result": "200"}), 200

#     except Exception as e:
#         return common.serverError(e)

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
        #
        # パラメータ項目設定
        #
        user = request.json['git_repositry']['user']
        token = request.json['git_repositry']['token']
        url = request.json['git_repositry']['url']
        #webhooks_url = request.json['webhooks_url'] + ':' + os.environ['EPOCH_WEBHOOK_PORT']
        webhooks_url = request.json["webhooks_url"] + ':' + os.environ['EPOCH_WEBHOOK_PORT'] + '/api/listener/{}'.format(workspace_id)

        # webhookの存在チェック
        ret_exists = exists_webhook(user, token, url, webhooks_url)
        globals.logger.debug('CALL exists_webhook:ret:{}'.format(ret_exists))
        # すでにwebhookが存在したので200で終了
        if ret_exists:
            return jsonify({"result": "200", "output": "gitlab_webhook{ already exists webhook}"}), 200

        # ヘッダ情報
        post_headers = {
            'PRIVATE-TOKEN': token,
            'Content-Type': 'application/json',
        }

        # URLの分割
        json_url = get_url_split(url)

        # 引数をJSON形式で構築
        post_data = json.dumps({
            "id": "{}%2F{}".format(json_url['group_name'], json_url['repos_name']),
            "url": webhooks_url,
            "push_events": True,
            "tag_push_events": True,
            "enable_ssl_verification": False,
        })

        api_url = "{}://{}:{}/api/v4/projects/{}%2F{}/hooks".format(API_PROTOCOL, API_BASE_URL, API_PORT, json_url['group_name'], json_url['repos_name'])
        globals.logger.debug('api_url: {}'.format(api_url))
        # create webhookのPOST送信
        request_response = requests.post(api_url, headers=post_headers, data=post_data)

        globals.logger.debug('code: {}, message: {}'.format(str(request_response.status_code), request_response.text))
        # 正常に作成された場合は201が応答されるので正常終了
        if request_response.status_code == 201:
            globals.logger.debug('gitlab webhook create SUCCEED')
        else:
            raise Exception("webhook create error:{}".format(request_response.text))

        response = {
            "result": "201",
            "output": "gitlab_webhook{" + request_response.text + "}"
        }

        return jsonify(response), 201

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
        globals.logger.debug('CALL exists_repositry:ret:{}'.format(ret_exists))
        # すでにリポジトリが存在したので200で終了
        if ret_exists:
            return jsonify({"result": "200", "output": "gitlab_project{ already exists repositry}"}), 200

        # URLの分割
        json_url = get_url_split(url)

        # 分割したグループ名がユーザー名と一致しない場合は、グループIDを取得する
        if json_url['group_name'] != user:
            # グループID取得
            url_group_id = get_group_id(user, token, url)
            # グループが存在しない場合は、Exceptionで終了する
            if url_group_id is None:
                raise Exception("group not found")
        else:
            url_group_id = None

        # ヘッダ情報
        post_headers = {
            'PRIVATE-TOKEN': token,
            'Content-Type': 'application/json',
        }

        # 引数をJSON形式で構築
        post_data = {
            "name": json_url['repos_name'],
            "public": "true",
            "initialize_with_readme": "true",
        }

        # グループ指定有無を判定
        if url_group_id is not None:
            post_data["namespace_id"] = url_group_id

        post_data = json.dumps(post_data)

        api_url = "{}://{}:{}/api/v4/projects".format(API_PROTOCOL, API_BASE_URL, API_PORT)
        # create projectのPOST送信
        request_response = requests.post(api_url, headers=post_headers, data=post_data)

        globals.logger.debug('code: {}, message: {}'.format(str(request_response.status_code), request_response.text))
        # 正常に作成された場合は201が応答されるので正常終了
        if request_response.status_code == 201:
            globals.logger.debug('gitlab project create SUCCEED')
        else:
            raise Exception("project create error:{}".format(request_response.text))

        response = {
            "result": "201",
            "output": "gitlab_project{" + request_response.text + "}"
        }

        return jsonify(response), 201

    except Exception as e:
        return common.serverError(e)


@app.route('/commits', methods=['GET'])
def call_gitlab_commits_root():
    """/commits 呼び出し

    Returns:
        Response: HTTP Respose
    """
    try:
        globals.logger.debug('#' * 50)
        globals.logger.debug('CALL {}:from[{}]'.format(inspect.currentframe().f_code.co_name, request.method))
        globals.logger.debug('#' * 50)

        if request.method == 'GET':
            # git commits get
            return get_git_commits()
        else:
            # エラー
            raise Exception("method not support!")

    except Exception as e:
        return common.server_error(e)


@app.route('/branches', methods=['GET'])
def call_gitlab_branches_root():
    """/branches 呼び出し

    Returns:
        Response: HTTP Respose
    """
    try:
        globals.logger.debug('#' * 50)
        globals.logger.debug('CALL {}:from[{}]'.format(inspect.currentframe().f_code.co_name, request.method))
        globals.logger.debug('#' * 50)

        if request.method == 'GET':
            # git branches get
            return get_git_branches()
        else:
            # エラー
            raise Exception("method not support!")

    except Exception as e:
        return common.server_error(e)


@app.route('/commits/<string:revision>', methods=['GET'])
def call_gitlab_commits(revision):
    """/commits 呼び出し

    Args:
        revision (str): revision

    Returns:
        Response: HTTP Respose
    """
    try:
        globals.logger.debug('#' * 50)
        globals.logger.debug('CALL {}:from[{}] revision[{}]'.format(inspect.currentframe().f_code.co_name, request.method, revision))
        globals.logger.debug('#' * 50)

        if request.method == 'GET':
            # git commits get
            return get_git_commits(revision)
        else:
            # エラー
            raise Exception("method not support!")

    except Exception as e:
        return common.server_error(e)


@app.route('/commits/<string:revision>/branch', methods=['GET'])
def call_gitlab_commits_branch(revision):
    """/commits/branch 呼び出し

    Args:
        revision (str): revision

    Returns:
        Response: HTTP Respose
    """
    try:
        globals.logger.debug('#' * 50)
        globals.logger.debug('CALL {}:from[{}] revision[{}]'.format(inspect.currentframe().f_code.co_name, request.method, revision))
        globals.logger.debug('#' * 50)

        if request.method == 'GET':
            # git commits branch get
            return get_git_commits_branch(revision)
        else:
            # エラー
            raise Exception("method not support!")

    except Exception as e:
        return common.server_error(e)


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
        raise Exception("repository error:{}".format(response.text))

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
    # ヘッダ情報
    post_headers = {
        'PRIVATE-TOKEN': token,
        'Content-Type': 'application/json',
    }

    # URLの分割
    json_url = get_url_split(url)

    api_url = "{}://{}:{}/api/v4/groups/{}".format(API_PROTOCOL, API_BASE_URL, API_PORT,json_url['group_name'])

    # 単一のグループ詳細を取得する
    response = requests.get(api_url, headers=post_headers)

    # グループが存在する場合はグループIDを返す
    if response.status_code == 200:
        ret_data = json.loads(response.text)
        ret_id = int(ret_data['id'])

    # グループが存在しなかったらFalseを返す
    else:
        raise Exception("group error:{}".format(response.text))

    return ret_id

def get_url_split(url):
    """urlの解析分割

    Args:
        url (str): url

    Returns:
        json: URLをbase_url, group_name, repos_nameに分割した値
    """
    # 正規表現を使って、urlからベースurl
    base_url = re.search('^https?://[^/][^/]*/',url).group()
    # 正規表現を使って、urlからグループ名、レポジトリ名を取得する
    repos_url = re.sub('\\.git$','',re.sub('^https?://[^/][^/]*/','',url))
    # 1つめで、xxxx/xxxx形式になっているので、"/"で分割して前半部をグループ名、後半部をレポジトリ名（プロジェクト名）で設定する
    split_url = repos_url.split('/')
    if len(split_url) != 2:
        raise Exception("url error")

    group_name = split_url[0]
    repos_name = split_url[1]

    json_url = {
        "base_url": base_url,
        "group_name": group_name,
        "repos_name": repos_name ,
    }

    return json_url

def exists_webhook(user, token, url, webhooks_url):
    """webhookの存在チェック

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

    api_url = "{}://{}:{}/api/v4/projects/{}%2F{}/hooks".format(API_PROTOCOL, API_BASE_URL, API_PORT,json_url['group_name'],json_url['repos_name'])

    # webhookの一覧を取得する
    response = requests.get(api_url, headers=post_headers)

    # webhookが存在する場合はTrueを返す
    if response.status_code == 200:
        webhook_list = json.loads(response.text)
        globals.logger.debug('webhook_list: {}'.format(response.text))
        ret = False
        for item in webhook_list:
            if item['url'] == webhooks_url:
                ret = True
                break

    # それ以外はwebhook errorを返す
    else:
        raise Exception("webhook error:{}".format(response.text))

    return ret


def get_git_branches():
    """git branches 情報の取得 Get git branches information

    Returns:
        Response: HTTP Respose
    """

    try:
        globals.logger.debug('#' * 50)
        globals.logger.debug('CALL {}'.format(inspect.currentframe().f_code.co_name))
        globals.logger.debug('#' * 50)

        # ヘッダ情報 header info.
        post_headers = {
            'PRIVATE-TOKEN': request.headers["private-token"],
            'Content-Type': 'application/json',
        }

        # git_url (str): git url
        if request.args.get('git_url') is not None:
            git_url = urllib.parse.unquote(request.args.get('git_url'))
        else:
            raise Exception("gir_url parameter not found")

        json_url = get_url_split(git_url)

        # gitlab repo branches get call 
        api_url = "{}://{}:{}/api/v4/projects/{}%2F{}/repository/branches".format(API_PROTOCOL, API_BASE_URL, API_PORT, json_url['group_name'], json_url['repos_name'])

        globals.logger.debug("api_url:[{}]".format(api_url))
        response = requests.get(api_url, headers=post_headers)

        ret_status = response.status_code 
        if response.status_code == 200:
            rows = json.loads(response.text) 
            # globals.logger.debug("rows:[{}]".format(rows))
        else:
            rows = None
            globals.logger.debug("git branches get error:[{}] text:[{}]".format(response.status_code, response.text))

        # 取得したGit branches情報を返却 Return the acquired Git branches information
        return jsonify({"result": ret_status, "rows": rows}), ret_status

    except common.UserException as e:
        return common.server_error(e)
    except Exception as e:
        globals.logger.debug("Exception:[{}]".format(e.args))
        return common.server_error(e)


def get_git_commits(revision=None):
    """git commits 情報の取得 Get git commits information

    Args:
        revision (str): revision

    Returns:
        Response: HTTP Respose
    """

    try:
        globals.logger.debug('#' * 50)
        globals.logger.debug('CALL {} revision[{}]'.format(inspect.currentframe().f_code.co_name, revision))
        globals.logger.debug('#' * 50)

        # ヘッダ情報 header info.
        post_headers = {
            'PRIVATE-TOKEN': request.headers["private-token"],
            'Content-Type': 'application/json',
        }

        # git_url (str): git url
        if request.args.get('git_url') is not None:
            git_url = urllib.parse.unquote(request.args.get('git_url'))
        else:
            raise Exception("gir_url parameter not found")

        # branch (str): branch
        if request.args.get('branch') is not None:
            branch = urllib.parse.unquote(request.args.get('branch'))
        else:
            branch = None

        json_url = get_url_split(git_url)

        # gitlab repo commits get call 
        api_url = "{}://{}:{}/api/v4/projects/{}%2F{}/repository/commits".format(API_PROTOCOL, API_BASE_URL, API_PORT, json_url['group_name'], json_url['repos_name'])

        # 個別指定がある場合のみ、条件を設定
        # Set conditions only if there is an individual specification
        if revision is not None:
            api_url += "/{}".format(revision)

        if branch is not None:
            api_url += "?ref_name={}".format(urllib.parse.quote(branch))

        globals.logger.debug("api_url:[{}]".format(api_url))
        response = requests.get(api_url, headers=post_headers)

        ret_status = response.status_code 
        if response.status_code == 200:
            rows = json.loads(response.text) 
            # globals.logger.debug("rows:[{}]".format(rows))
        else:
            rows = None
            globals.logger.debug("git commits get error:[{}] text:[{}]".format(response.status_code, response.text))

        # 取得したGit commit情報を返却 Return the acquired Git commit information
        return jsonify({"result": ret_status, "rows": rows}), ret_status

    except common.UserException as e:
        return common.server_error(e)
    except Exception as e:
        globals.logger.debug("Exception:[{}]".format(e.args))
        return common.server_error(e)


def get_git_commits_branch(revision):
    """git commits branch情報の取得 Get git commits branch information

    Args:
        revision (str): revision

    Returns:
        Response: HTTP Respose
    """

    try:
        globals.logger.debug('#' * 50)
        globals.logger.debug('CALL {} revision[{}]'.format(inspect.currentframe().f_code.co_name, revision))
        globals.logger.debug('#' * 50)

        # ヘッダ情報 header info.
        post_headers = {
            'PRIVATE-TOKEN': request.headers["private-token"],
            'Content-Type': 'application/json',
        }

        # git_url (str): git url
        if request.args.get('git_url') is not None:
            git_url = urllib.parse.unquote(request.args.get('git_url'))
        else:
            raise Exception("gir_url parameter not found")

        json_url = get_url_split(git_url)

        # gitlab repo commits brach get call 
        api_url = "{}://{}:{}/api/v4/projects/{}%2F{}/repository/commits/{}/refs".format(API_PROTOCOL, API_BASE_URL, API_PORT, json_url['group_name'], json_url['repos_name'], revision)

        globals.logger.debug("api_url:[{}]".format(api_url))
        response = requests.get(api_url, headers=post_headers)

        ret_status = response.status_code 
        if response.status_code == 200:
            rows = json.loads(response.text) 
            # globals.logger.debug("rows:[{}]".format(rows))
        else:
            rows = None
            globals.logger.debug("git commits branch get error:[{}] text:[{}]".format(response.status_code, response.text))

        # 取得したGit commit branch 情報を返却 Return the acquired Git commit branch information
        return jsonify({"result": ret_status, "rows": rows}), ret_status

    except common.UserException as e:
        return common.server_error(e)
    except Exception as e:
        globals.logger.debug("Exception:[{}]".format(e.args))
        return common.server_error(e)

if __name__ == "__main__":
    app.run(debug=eval(os.environ.get('API_DEBUG', "False")), host='0.0.0.0', port=int(os.environ.get('API_INSIDE_GITLAB_PORT', '8000')), threaded=True)

