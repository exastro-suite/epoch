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
import bcrypt
import pytz

import globals
import common

# 設定ファイル読み込み・globals初期化
app = Flask(__name__)
app.config.from_envvar('CONFIG_API_ARGOCD_PATH')
globals.init(app)

@app.route('/alive', methods=["GET"])
def alive():
    """死活監視

    Returns:
        Response: HTTP Respose
    """
    return jsonify({"result": "200", "time": str(datetime.now(globals.TZ))}), 200

@app.route('/workspace/<int:workspace_id>/agrocd', methods=['POST'])
def call_argocd(workspace_id):
    """workspace/workspace_id/argocd 呼び出し

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
            # argocd pod 生成
            return create_argocd(workspace_id)
        else:
            # エラー
            raise Exception("method not support!")

    except Exception as e:
        return common.server_error(e)

# def create_argocd(workspace_id):
#     """argoCD Pod 作成

#     Args:
#         workspace_id (int): ワークスペースID

#     Returns:
#         Response: HTTP Respose
#     """

#     app_name = "ワークスペース情報:"
#     exec_stat = "ArgoCD環境構築"
#     error_detail = ""

#     try:
#         globals.logger.debug('#' * 50)
#         globals.logger.debug('CALL {}'.format(inspect.currentframe().f_code.co_name))
#         globals.logger.debug('#' * 50)

#         ret_status = 200

#         # 戻り値をそのまま返却        
#         return jsonify({"result": ret_status}), ret_status

#     except common.UserException as e:
#         return common.server_error_to_message(e, app_name + exec_stat, error_detail)
#     except Exception as e:
#         return common.server_error_to_message(e, app_name + exec_stat, error_detail)


def create_argocd(workspace_id):
    """argoCD Pod 作成

    Args:
        workspace_id (int): ワークスペースID

    Returns:
        Response: HTTP Respose
    """

    app_name = "ワークスペース情報:"
    exec_stat = "ArgoCD環境構築"
    error_detail = ""

    try:
        globals.logger.debug('#' * 50)
        globals.logger.debug('CALL {}'.format(inspect.currentframe().f_code.co_name))
        globals.logger.debug('#' * 50)

        ret_status = 200

        template_dir = os.path.dirname(os.path.abspath(__file__)) + "/templates"

        # argocd apply pod create
        globals.logger.debug('apply : argocd_install_v2_1_1.yaml')
        stdout_cd = subprocess.check_output(["kubectl","apply","-n",workspace_namespace(workspace_id),"-f",(template_dir + "/argocd_install_v2_1_1.yaml")],stderr=subprocess.STDOUT)
        globals.logger.debug(stdout_cd.decode('utf-8'))

        #
        # argocd apply rolebinding
        #
        with tempfile.TemporaryDirectory() as tempdir:
            # テンプレートファイルからyamlの生成
            yamltext = render_template('argocd_rolebinding.yaml',
                        param={
                            "workspace_namespace": workspace_namespace(workspace_id)
                        })
            path_yamlfile = '{}/{}'.format(tempdir, "argocd_rolebinding.yaml")
            with open(path_yamlfile, mode='w') as fp:
                fp.write(yamltext)
            # yamlの適用
            globals.logger.debug('apply : argocd_rolebinding.yaml')
            stdout_cd = subprocess.check_output(["kubectl","apply","-n",workspace_namespace(workspace_id),"-f",path_yamlfile],stderr=subprocess.STDOUT)
            globals.logger.debug(stdout_cd.decode('utf-8'))

        #
        # パスワードの初期化
        #

        # Access情報の取得
        access_data = get_access_info(workspace_id)
        argo_password = access_data['ARGOCD_PASSWORD']

        salt = bcrypt.gensalt(rounds=10, prefix=b'2a')
        password = argo_password.encode("ascii")
        argoLogin = bcrypt.hashpw(password, salt).decode("ascii")
        datenow = datetime.now(pytz.timezone('Asia/Tokyo')).strftime('%Y-%m-%dT%H:%M:%S%z')
        pdata ='{"stringData": { "admin.password": "' + argoLogin + '", "admin.passwordMtime": "\'' + datenow + '\'" }}'

        globals.logger.debug('patch argocd-secret :')
        stdout_cd = subprocess.check_output(["kubectl","-n",workspace_namespace(workspace_id),"patch","secret","argocd-secret","-p",pdata],stderr=subprocess.STDOUT)
        globals.logger.debug(stdout_cd.decode('utf-8'))

        #
        # PROXY setting
        #
        # 対象となるdeploymentを定義
        deployments = [ "deployment/argocd-server",
                        "deployment/argocd-dex-server",
                        "deployment/argocd-redis",
                        "deployment/argocd-repo-server" ]

        # Proxyの設定値
        envs = [ "HTTP_PROXY=" + os.environ['EPOCH_HTTP_PROXY'],
                 "HTTPS_PROXY=" + os.environ['EPOCH_HTTPS_PROXY'],
                 "http_proxy=" + os.environ['EPOCH_HTTP_PROXY'],
                 "https_proxy=" + os.environ['EPOCH_HTTPS_PROXY'],
                 "NO_PROXY=" + os.environ['EPOCH_ARGOCD_NO_PROXY'],
                 "no_proxy=" + os.environ['EPOCH_ARGOCD_NO_PROXY'] ]

        # PROXYの設定を反映
        for deployment_name in deployments:
            for env_name in envs:
                # 環境変数の設定
                globals.logger.debug('set env : {} {}'.format(deployment_name, env_name))
                stdout_cd = subprocess.check_output(["kubectl","set","env",deployment_name,"-n",workspace_namespace(workspace_id),env_name],stderr=subprocess.STDOUT)
                globals.logger.debug(stdout_cd.decode('utf-8'))

        # 戻り値をそのまま返却        
        return jsonify({"result": ret_status}), ret_status

    except common.UserException as e:
        return common.server_error_to_message(e, app_name + exec_stat, error_detail)
    except Exception as e:
        return common.server_error_to_message(e, app_name + exec_stat, error_detail)

def get_access_info(workspace_id):
    """ワークスペースアクセス情報取得

    Args:
        workspace_id (int): ワークスペースID

    Returns:
        json: アクセス情報
    """
    try:
        # url設定
        api_info = "{}://{}:{}".format(os.environ['EPOCH_RS_WORKSPACE_PROTOCOL'], os.environ['EPOCH_RS_WORKSPACE_HOST'], os.environ['EPOCH_RS_WORKSPACE_PORT'])

        # アクセス情報取得
        # Select送信（workspace_access取得）
        globals.logger.debug ("workspace_access get call: worksapce_id:{}".format(workspace_id))
        request_response = requests.get( "{}/workspace/{}/access".format(api_info, workspace_id))

        # 情報が存在する場合は、更新、存在しない場合は、登録
        if request_response.status_code == 200:
            ret = json.loads(request_response.text)
        else:
            raise Exception("workspace_access get error status:{}, responce:{}".format(request_response.status_code, request_response.text))

        return ret

    except Exception as e:
        globals.logger.debug ("get_access_info Exception:{}".format(e.args))
        raise # 再スロー

def workspace_namespace(workspace_id):
    """workspace用namespace取得

    Args:
        workspace_id (int): ワークスペースID

    Returns:
        str: workspace用namespace
    """
    return  'epoch-workspace-{}'.format(workspace_id)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('API_ARGOCD_PORT', '8000')), threaded=True)
