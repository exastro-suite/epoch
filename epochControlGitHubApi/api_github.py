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

from flask import Flask, request, abort, jsonify, render_template
from datetime import datetime
import inspect
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

# 設定ファイル読み込み・globals初期化
app = Flask(__name__)
app.config.from_envvar('CONFIG_API_GITHUB_PATH')
globals.init(app)

# github webhook base url
github_webhook_base_url = 'https://api.github.com/repos/'
github_webhook_base_hooks = '/hooks'

@app.route('/alive', methods=["GET"])
def alive():
    """死活監視

    Returns:
        Response: HTTP Respose
    """
    return jsonify({"result": "200", "time": str(datetime.now(globals.TZ))}), 200


@app.route('/workspace/<int:workspace_id>/github/webhooks', methods=['GET','POST'])
def call_github_webhooks(workspace_id):
    """workspace/workspace_id/github/wehbooks 呼び出し

    Args:
        workspace_id (int): ワークスペースID

    Returns:
        Response: HTTP Respose
    """
    try:
        globals.logger.debug('#' * 50)
        globals.logger.debug('CALL {}:from[{}] workspace_id[{}]'.format(inspect.currentframe().f_code.co_name, request.method, workspace_id))
        globals.logger.debug('#' * 50)

        if request.method == 'POST':
            # webhooks 生成
            return create_github_webhooks(workspace_id)
        else:
            # webhooks 取得
            return get_github_webhooks(workspace_id)

    except Exception as e:
        return common.server_error(e)

def create_github_webhooks(workspace_id):
    """webhooks 設定

    Args:
        workspace_id (int): ワークスペースID

    Returns:
        Response: HTTP Respose
    """

    app_name = "ワークスペース情報:"
    exec_stat = "GitHub WebHooks設定"
    error_detail = ""
    apache_path = '/api/listener/{}'.format(workspace_id)

    try:
        globals.logger.debug('#' * 50)
        globals.logger.debug('CALL {}'.format(inspect.currentframe().f_code.co_name))
        globals.logger.debug('#' * 50)

        # 引数で指定されたCD環境を取得
        request_json = json.loads(request.data)
        request_ci_confg = request_json["ci_config"]

        # パイプライン数分繰り返し
        for pipeline in request_ci_confg["pipelines"]:
            git_repos = re.sub('\\.git$','',re.sub('^https?://[^/][^/]*/','',pipeline["git_repositry"]["url"]))
            web_hooks_url = pipeline["webhooks_url"] + ':' + os.environ['EPOCH_WEBHOOK_PORT'] + apache_path
            token = request_ci_confg["pipelines_common"]["git_repositry"]["token"]

            # GitHubへPOST送信
            # ヘッダ情報
            post_headers = {
                'Authorization': 'token ' + token,
                'Accept': 'application/vnd.github.v3+json',
            }

            # 引数をJSON形式で構築
            post_data = json.dumps({
                "config":{
                    "url": web_hooks_url,
                    "content_type":"json",
                    "secret":"",
                    "insecure_ssl":"1",
                    "token":"token",
                    "digest":"digest",
                }
            })

            # hooksのPOST送信
            globals.logger.debug('- github.webhooks setting to git')
            globals.logger.debug('- https_proxy:{}, http_proxy:{}'.format(os.environ['HTTPS_PROXY'], os.environ['HTTP_PROXY']))
            globals.logger.debug('- request URL:' + github_webhook_base_url + git_repos + github_webhook_base_hooks)
            globals.logger.debug('- webhook URL :' + web_hooks_url)
            request_response = requests.post( github_webhook_base_url + git_repos + github_webhook_base_hooks, headers=post_headers, data=post_data)

            globals.logger.debug('- response headers')
            globals.logger.debug(request_response.headers)
            globals.logger.debug('- response body')
            globals.logger.debug(request_response.text)

        # 成功(201) または、Webhook URLの重複(422)のステータスコードが返ってきた場合、コード200を返し後続の処理を実行する
        if request_response.status_code == 201 or request_response.status_code == 422:
            ret_status = 200

        # 戻り値をそのまま返却
        return jsonify({"result": ret_status}), ret_status

    except common.UserException as e:
        return common.server_error_to_message(e, app_name + exec_stat, error_detail)
    except Exception as e:
        return common.server_error_to_message(e, app_name + exec_stat, error_detail)


def get_github_webhooks(workspace_id):
    """webhooks 取得

    Args:
        workspace_id (int): ワークスペースID

    Returns:
        Response: HTTP Respose
    """

    app_name = "ワークスペース情報:"
    exec_stat = "GitHub WebHooks取得"
    error_detail = ""

    try:
        globals.logger.debug('#' * 50)
        globals.logger.debug('CALL {}'.format(inspect.currentframe().f_code.co_name))
        globals.logger.debug('#' * 50)


        # 引数で指定されたCD環境を取得
        request_json = json.loads(request.data)
        request_ci_confg = request_json["ci_config"]

        # パイプライン数分繰り返し
        for pipeline in request_ci_confg["pipelines"]:
            git_repos = re.sub('\\.git$','',re.sub('^https?://[^/][^/]*/','',pipeline["git_repositry"]["url"]))
            token = request_ci_confg["pipelines_common"]["git_repositry"]["token"]

            # GitHubへGET送信
            # ヘッダ情報
            request_headers = {
                'Authorization': 'token ' + token,
                'Accept': 'application/vnd.github.v3+json',
            }

            globals.logger.debug(git_repos)
            # GETリクエスト送信
            request_response = requests.get( github_webhook_base_url + git_repos + github_webhook_base_hooks, headers=request_headers)

        ret_status = request_response.status_code

        if ret_status == '200':
            rows = request_response.text
        else:
            rows = []

        # 戻り値をそのまま返却
        return jsonify({"result": ret_status, "rows": rows}), ret_status

    except common.UserException as e:
        return common.server_error_to_message(e, app_name + exec_stat, error_detail)
    except Exception as e:
        return common.server_error_to_message(e, app_name + exec_stat, error_detail)


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('API_GITHUB_PORT', '8000')), threaded=True)