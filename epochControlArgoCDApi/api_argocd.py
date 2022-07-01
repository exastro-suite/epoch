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
import common, multi_lang

# 設定ファイル読み込み・globals初期化
app = Flask(__name__)
app.config.from_envvar('CONFIG_API_ARGOCD_PATH')
globals.init(app)

WAIT_APPLICATION_DELETE = 180 # アプリケーションが削除されるまでの最大待ち時間

@app.route('/alive', methods=["GET"])
def alive():
    """死活監視

    Returns:
        Response: HTTP Respose
    """
    return jsonify({"result": "200", "time": str(datetime.now(globals.TZ))}), 200

@app.route('/workspace/<int:workspace_id>/argocd', methods=['POST'])
def call_argocd(workspace_id):
    """Call workspace/workspace_id/argocd

    Args:
        workspace_id (int): workspace id

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

@app.route('/workspace/<int:workspace_id>/argocd/app/<string:app_name>', methods=['GET'])
def call_argocd_app(workspace_id, app_name):
    """Call workspace/workspace_id/argocd/app

    Args:
        workspace_id (int): workspace id
        app_name (str): app name (same environment name)

    Returns:
        Response: HTTP Respose
    """
    try:
        globals.logger.debug('#' * 50)
        globals.logger.debug('CALL {}:from[{}] workspace_id[{}] app_name[{}]'.format(inspect.currentframe().f_code.co_name, request.method, workspace_id, app_name))
        globals.logger.debug('#' * 50)

        if request.method == 'GET':
            # argocd app情報取得 argocd app information get
            return get_argocd_app(workspace_id, app_name)
        else:
            # エラー
            raise Exception("method not support!")

    except Exception as e:
        return common.server_error(e)

@app.route('/workspace/<int:workspace_id>/argocd/app/<string:app_name>/sync', methods=['POST'])
def call_argocd_app_sync(workspace_id, app_name):
    """Call workspace/workspace_id/argocd/app/sync

    Args:
        workspace_id (int): workspace id
        app_name (str): app name (same environment name)

    Returns:
        Response: HTTP Respose
    """
    try:
        globals.logger.debug('#' * 50)
        globals.logger.debug('CALL {}:from[{}] workspace_id[{}]'.format(inspect.currentframe().f_code.co_name, request.method, workspace_id))
        globals.logger.debug('#' * 50)

        if request.method == 'POST':
            # post argocd sync - ArgoCD 同期処理
            return post_argocd_sync(workspace_id, app_name)
        else:
            # エラー
            raise Exception("method not support!")

    except Exception as e:
        return common.server_error(e)


@app.route('/workspace/<int:workspace_id>/argocd/app/<string:app_name>/rollback', methods=['POST'])
def call_argocd_app_rollback(workspace_id, app_name):
    """Call workspace/workspace_id/argocd/app/rollback

    Args:
        workspace_id (int): workspace id
        app_name (str): app name (same environment name)

    Returns:
        Response: HTTP Respose
    """
    try:
        globals.logger.debug('#' * 50)
        globals.logger.debug('CALL {}:from[{}] workspace_id[{}]'.format(inspect.currentframe().f_code.co_name, request.method, workspace_id))
        globals.logger.debug('#' * 50)

        if request.method == 'POST':
            # post argocd rollback - ArgoCD rollback処理
            return post_argocd_rollback(workspace_id, app_name)
        else:
            # エラー
            raise Exception("method not support!")

    except Exception as e:
        return common.server_error(e)


def create_argocd(workspace_id):
    """ Create pod argocd - ArgoCD Pod 作成

    Args:
        workspace_id (int): workspace id

    Returns:
        Response: HTTP Respose
    """

    app_name = multi_lang.get_text("EP035-0001", "ワークスペース情報:")
    exec_stat = multi_lang.get_text("EP035-0002", "ArgoCD環境構築")
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
        # globals.logger.debug(stdout_cd.decode('utf-8'))

        #
        # argocd apply rolebinding
        #
        with tempfile.TemporaryDirectory() as tempdir:
            # テンプレートファイルからyamlの生成
            yamltext = render_template('argocd_rolebinding.yaml',
                        param={
                            "workspace_id" : workspace_id,
                            "workspace_namespace": workspace_namespace(workspace_id),
                        })
            path_yamlfile = '{}/{}'.format(tempdir, "argocd_rolebinding.yaml")
            with open(path_yamlfile, mode='w') as fp:
                fp.write(yamltext)
            # yamlの適用
            globals.logger.debug('apply : argocd_rolebinding.yaml')
            stdout_cd = subprocess.check_output(["kubectl","apply","-n",workspace_namespace(workspace_id),"-f",path_yamlfile],stderr=subprocess.STDOUT)
            # globals.logger.debug(stdout_cd.decode('utf-8'))

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
        # globals.logger.debug(stdout_cd.decode('utf-8'))

        #
        # PROXY setting
        #
        # 対象となるdeploymentを定義
        deployments = [ "deployment/argocd-server",
                        "deployment/argocd-dex-server",
                        "deployment/argocd-redis",
                        "deployment/argocd-repo-server" ]

        # Proxyの設定値
        no_proxy = os.environ['EPOCH_ARGOCD_NO_PROXY']
        if 'EPOCH_HOSTNAME' in os.environ and os.environ['EPOCH_HOSTNAME'] != '':
            no_proxy = no_proxy + ',' + os.environ['EPOCH_HOSTNAME']

        envs = [ "HTTP_PROXY=" + os.environ['EPOCH_HTTP_PROXY'],
                 "HTTPS_PROXY=" + os.environ['EPOCH_HTTPS_PROXY'],
                 "http_proxy=" + os.environ['EPOCH_HTTP_PROXY'],
                 "https_proxy=" + os.environ['EPOCH_HTTPS_PROXY'],
                 "NO_PROXY=" + no_proxy,
                 "no_proxy=" + no_proxy]

        # PROXYの設定を反映
        for deployment_name in deployments:
            for env_name in envs:
                # 環境変数の設定
                # globals.logger.debug('set env : {} {}'.format(deployment_name, env_name))
                stdout_cd = subprocess.check_output(["kubectl","set","env",deployment_name,"-n",workspace_namespace(workspace_id),env_name],stderr=subprocess.STDOUT)
                # globals.logger.debug(stdout_cd.decode('utf-8'))

        # 戻り値をそのまま返却        
        return jsonify({"result": ret_status}), ret_status

    except common.UserException as e:
        return common.server_error_to_message(e, app_name + exec_stat, error_detail)
    except Exception as e:
        return common.server_error_to_message(e, app_name + exec_stat, error_detail)


def get_argocd_app(workspace_id, app_name):
    """get argocd info - ArgoCD情報取得

    Args:
        workspace_id (int): workspace id
        app_name (str): argocd app name

    Returns:
        Response: HTTP Respose
    """

    try:
        globals.logger.debug('#' * 50)
        globals.logger.debug('CALL {} workspace_id:[{}], app_name:[{}]'.format(inspect.currentframe().f_code.co_name, workspace_id, app_name))
        globals.logger.debug('#' * 50)

        # ワークスペースアクセス情報取得 Get workspace access information
        access_data = get_access_info(workspace_id)

        argo_host = 'argocd-server.epoch-ws-{}.svc'.format(workspace_id)
        argo_id = access_data['ARGOCD_USER']
        argo_password = access_data['ARGOCD_PASSWORD']
        
        #
        # argocd login
        #
        globals.logger.debug("argocd login :")
        stdout_cd = common.subprocess_check_output_with_retry(["argocd","login",argo_host,"--insecure","--username",argo_id,"--password",argo_password],stderr=subprocess.STDOUT)
        # globals.logger.debug(stdout_cd.decode('utf-8'))

        #
        # argocd app get
        #
        globals.logger.debug("argocd app get :")
        stdout_cd = subprocess.check_output(["argocd","app","get", app_name, "-o","json"],stderr=subprocess.STDOUT)
        # globals.logger.debug(stdout_cd.decode('utf-8'))

        result = json.loads(stdout_cd)

        # ヘッダ情報
        post_headers = {
            'Content-Type': 'application/json',
        }

        # argocd tree info get
        api_info = "https://{}".format(argo_host)

        post_data = {
            "username" : argo_id,
            "password" : argo_password,
        }
        from requests.packages.urllib3.exceptions import InsecureRequestWarning
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

        # Toekn取得 get token
        globals.logger.debug ("argocd token get call:")
        response = requests.post( "{}/api/v1/session".format(api_info), headers=post_headers, data=json.dumps(post_data), verify=False)

        # 正常時以外はExceptionを発行して終了する
        # Exception is issued and ends except when it is normal.
        if response.status_code != 200:
            globals.logger.error(response.text)
            error_detail = "argocd token get error : status_code:{}".format(response.status_code)
            raise common.UserException(error_detail)

        ret_token = json.loads(response.text)

        post_headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer {}'.format(ret_token["token"]),
        }

        # Node情報取得 get node information
        globals.logger.debug ("argocd tree info get call:")
        response = requests.get( "{}/api/v1/applications/{}/resource-tree".format(api_info, app_name), headers=post_headers, verify=False)

        # 正常時以外はExceptionを発行して終了する
        # Exception is issued and ends except when it is normal.
        if response.status_code != 200:
            globals.logger.error(response.text)
            error_detail = "argocd tree info get error : status_code:{}".format(response.status_code)
            raise common.UserException(error_detail)

        ret_tree = json.loads(response.text)
        # globals.logger.debug(ret_tree)

        result.update(ret_tree)
        # globals.logger.debug(result)

        ret_status = 200

        # 戻り値をそのまま返却        
        return jsonify({"result": ret_status, "result": result}), ret_status

    except common.UserException as e:
        return common.server_error(e)
    except Exception as e:
        return common.server_error(e)


def post_argocd_sync(workspace_id, app_name):
    """post argocd sync - ArgoCD同期処理

    Args:
        workspace_id (int): workspace id
        app_name (str): app name (same environment name)

    Returns:
        Response: HTTP Respose
    """

    try:
        globals.logger.debug('#' * 50)
        globals.logger.debug('CALL {} workspace_id[{}] app_name[{}]'.format(inspect.currentframe().f_code.co_name, workspace_id, app_name))
        globals.logger.debug('#' * 50)

        # ワークスペースアクセス情報取得 Get workspace access information
        access_data = get_access_info(workspace_id)

        argo_host = 'argocd-server.epoch-ws-{}.svc'.format(workspace_id)
        argo_id = access_data['ARGOCD_USER']
        argo_password = access_data['ARGOCD_PASSWORD']
        
        #
        # argocd login
        #
        globals.logger.debug("argocd login :")
        stdout_cd = common.subprocess_check_output_with_retry(["argocd","login",argo_host,"--insecure","--username",argo_id,"--password",argo_password],stderr=subprocess.STDOUT)
        # globals.logger.debug(stdout_cd.decode('utf-8'))

        #
        # app sync
        #
        globals.logger.debug("argocd app sync :")
        try:
            stdout_cd = subprocess.check_output(["argocd","app","sync",app_name],stderr=subprocess.STDOUT)
            # globals.logger.debug(stdout_cd.decode('utf-8'))
        except subprocess.CalledProcessError as e:
            globals.logger.debug("command '{}' return with error (code {})".format(e.cmd, e.returncode))
            # globals.logger.debug(e.output)
            raise

        ret_status = 200
        
        # 正常終了 normal end       
        return jsonify({"result": ret_status}), ret_status

    except common.UserException as e:
        return common.server_error(e)
    except Exception as e:
        return common.server_error(e)


def post_argocd_rollback(workspace_id, app_name):
    """post argocd rollback - ArgoCD rollback処理

    Args:
        workspace_id (int): workspace id
        app_name (str): app name (same environment name)

    Returns:
        Response: HTTP Respose
    """

    try:
        globals.logger.debug('#' * 50)
        globals.logger.debug('CALL {} workspace_id[{}] app_name[{}]'.format(inspect.currentframe().f_code.co_name, workspace_id, app_name))
        globals.logger.debug('#' * 50)

        # ワークスペースアクセス情報取得 Get workspace access information
        access_data = get_access_info(workspace_id)

        argo_host = 'argocd-server.epoch-ws-{}.svc'.format(workspace_id)
        argo_id = access_data['ARGOCD_USER']
        argo_password = access_data['ARGOCD_PASSWORD']
        
        #
        # argocd login
        #
        globals.logger.debug("argocd login :")
        stdout_cd = common.subprocess_check_output_with_retry(["argocd","login",argo_host,"--insecure","--username",argo_id,"--password",argo_password],stderr=subprocess.STDOUT)
        # globals.logger.debug(stdout_cd.decode('utf-8'))

        #
        # app rollback
        #
        globals.logger.debug("argocd app rollback :")
        try:
            stdout_cd = subprocess.check_output(["argocd","app","rollback",app_name],stderr=subprocess.STDOUT)
            # globals.logger.debug(stdout_cd.decode('utf-8'))
        except subprocess.CalledProcessError as e:
            globals.logger.debug("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))
            raise

        ret_status = 200
        
        # 正常終了 normal end       
        return jsonify({"result": ret_status}), ret_status

    except common.UserException as e:
        return common.server_error(e)
    except Exception as e:
        return common.server_error(e)

@app.route('/workspace/<int:workspace_id>/argocd/settings', methods=['POST'])
def call_argocd_settings(workspace_id):
    """Call workspace/workspace_id/argocd/settings

    Args:
        workspace_id (int): workspace id

    Returns:
        Response: HTTP Respose
    """
    try:
        globals.logger.debug('#' * 50)
        globals.logger.debug('CALL {}:from[{}] workspace_id[{}]'.format(inspect.currentframe().f_code.co_name, request.method, workspace_id))
        globals.logger.debug('#' * 50)

        if request.method == 'POST':
            # settig argocd - ArgoCD設定
            return argocd_settings(workspace_id)
        else:
            # error
            raise Exception("method not support!")

    except Exception as e:
        return common.server_error(e)


def argocd_settings(workspace_id):
    """Setting argocd - ArgoCD設定

    Args:
        workspace_id (int): workspace id

    Returns:
        Response: HTTP Respose
    """

    app_name = multi_lang.get_text("EP035-0001", "ワークスペース情報:")
    exec_stat = multi_lang.get_text("EP035-0004", "ArgoCD設定")
    error_detail = ""

    try:
        # ワークスペースアクセス情報取得
        access_data = get_access_info(workspace_id)

        argo_host = 'argocd-server.epoch-ws-{}.svc'.format(workspace_id)
        argo_id = access_data['ARGOCD_USER']
        argo_password = access_data['ARGOCD_PASSWORD']

        # 引数で指定されたCD環境を取得
        request_json = json.loads(request.data)
        request_ci_env = request_json["ci_config"]["environments"]
        request_cd_env = request_json["cd_config"]["environments"]
        gitUsername = request_json["cd_config"]["environments_common"]["git_repositry"]["user"]
        gitPassword = request_json["cd_config"]["environments_common"]["git_repositry"]["token"]
        housing = request_json["cd_config"]["environments_common"]["git_repositry"]["housing"]

        #
        # argocd login
        #
        globals.logger.debug("argocd login :")
        stdout_cd = common.subprocess_check_output_with_retry(["argocd","login",argo_host,"--insecure","--username",argo_id,"--password",argo_password],stderr=subprocess.STDOUT)
        globals.logger.debug(stdout_cd.decode('utf-8'))

        #
        # repo setting
        #
        # リポジトリ情報の一覧を取得する
        globals.logger.debug("argocd repo list :")
        stdout_cd = subprocess.check_output(["argocd","repo","list","-o","json"],stderr=subprocess.STDOUT)
        globals.logger.debug(stdout_cd.decode('utf-8'))

        # 設定済みのリポジトリ情報をクリア
        repo_list = json.loads(stdout_cd)
        for repo in repo_list:
            globals.logger.debug("argocd repo rm [repo] {} :".format(repo['repo']))
            stdout_cd = subprocess.check_output(["argocd","repo","rm",repo['repo']],stderr=subprocess.STDOUT)
            globals.logger.debug(stdout_cd.decode('utf-8'))


        # 環境群数分処理を実行
        for env in request_cd_env:
            env_name = env["name"]
            gitUrl = env["git_repositry"]["url"]

            exec_stat = multi_lang.get_text("EP035-0005", "ArgoCD設定 - リポジトリ作成")
            error_detail = multi_lang.get_text("EP035-0006", "IaCリポジトリの設定内容を確認してください")

            # レポジトリの情報を追加
            globals.logger.debug ("argocd repo add :")
            if housing == "inner":
                stdout_cd = subprocess.check_output(["argocd","repo","add","--insecure-ignore-host-key",gitUrl,"--username",gitUsername,"--password",gitPassword],stderr=subprocess.STDOUT)
            else:
                stdout_cd = subprocess.check_output(["argocd","repo","add",gitUrl,"--username",gitUsername,"--password",gitPassword],stderr=subprocess.STDOUT)
            globals.logger.debug(stdout_cd.decode('utf-8'))

        #
        # cluster setting
        #
        # クラスタ情報の一覧を取得する
        globals.logger.debug("argocd cluster list :")
        stdout_cd = subprocess.check_output(["argocd","cluster","list","-o","json"],stderr=subprocess.STDOUT)
        # globals.logger.debug(stdout_cd.decode('utf-8'))

        #
        # cluster rm
        #
        # 設定済みのクラスタ情報をクリア
        cluster_list = json.loads(stdout_cd)
        for cluster in cluster_list:
            if cluster['name'] == 'in-cluster':
                # 内部クラスターは削除しない
                continue

            globals.logger.debug('delete : secret {}'.format(cluster['name']))
            stdout_cd = subprocess.check_output(["kubectl","delete","secret","-n",workspace_namespace(workspace_id),cluster['name']],stderr=subprocess.STDOUT)
            globals.logger.debug(stdout_cd.decode('utf-8'))

        #
        # cluster add each environment
        #
        # 環境群数分処理を実行
        for env in request_cd_env:
            cluster_kind = env["deploy_destination"]["cluster_kind"]
            if cluster_kind == 'internal':
                # 内部クラスターは追加しない
                continue

            cluster_name = get_argo_cluster_name(workspace_id, env['environment_id'])
            cluster_url = env["deploy_destination"]["cluster_url"]
            authentication_token = env["deploy_destination"]["authentication_token"]
            base64_encoded_certificate = env["deploy_destination"]["base64_encoded_certificate"]

            exec_stat = multi_lang.get_text("EP035-0009", "ArgoCD設定 - クラスター登録")
            error_detail = multi_lang.get_text("EP035-0008", "ArgoCDの入力内容を確認してください")

            # クラスタ情報を追加
            with tempfile.TemporaryDirectory() as tempdir:
                # テンプレートファイルからyamlの生成
                yamltext = render_template(
                    'argocd_cluster_secret.yaml',
                    param={
                        "environment_id": env['environment_id'],
                        "cluster_name": cluster_name,
                        "cluster_url": cluster_url,
                        "authentication_token": authentication_token,
                        "base64_encoded_certificate": base64_encoded_certificate,
                })
                path_yamlfile = '{}/{}'.format(tempdir, "argocd_cluster_secret_{}.yaml".format(env['environment_id']))
                with open(path_yamlfile, mode='w') as fp:
                    fp.write(yamltext)
                # yamlの適用
                globals.logger.debug('apply : argocd_cluster_secret.yaml')
                stdout_cd = subprocess.check_output(["kubectl","apply","-n",workspace_namespace(workspace_id),"-f",path_yamlfile],stderr=subprocess.STDOUT)
                globals.logger.debug(stdout_cd.decode('utf-8'))

        #
        # app setting
        #
        # アプリケーション情報の一覧を取得する
        globals.logger.debug("argocd app list :")
        stdout_cd = subprocess.check_output(["argocd","app","list","-o","json"],stderr=subprocess.STDOUT)
        # globals.logger.debug(stdout_cd.decode('utf-8'))


        # 環境が無くなったものについて、アプリケーション情報を削除する
        app_list = json.loads(stdout_cd)
        for app in app_list:
            not_found_env = (next(filter(lambda env: (get_argo_app_name(workspace_id, env['environment_id']) == app['metadata']['name']), request_cd_env), None) is None)
            if not_found_env:
                globals.logger.debug('argocd app delete [app] {} :'.format(app['metadata']['name']))
                stdout_cd = subprocess.check_output(["argocd","app","delete",app['metadata']['name'],"--cascade=false"],stderr=subprocess.STDOUT)

        # 環境群数分処理を実行
        for env in request_cd_env:
            argo_app_name = get_argo_app_name(workspace_id, env['environment_id'])
            cluster_kind = env["deploy_destination"]["cluster_kind"]

            if cluster_kind == 'internal':
                # 内部Cluster
                cluster = 'in-cluster'
            else:
                cluster = get_argo_cluster_name(workspace_id, env['environment_id'])

            namespace = env["deploy_destination"]["namespace"]
            gitUrl = env["git_repositry"]["url"]

            argo_app = next(filter(lambda app: (argo_app_name == app['metadata']['name']), app_list), None)

            if argo_app is None:
                # create application
                exec_stat = multi_lang.get_text("EP035-0007", "ArgoCD設定 - アプリケーション作成")
                error_detail = multi_lang.get_text("EP035-0008", "ArgoCDの入力内容を確認してください")

                globals.logger.debug('argocd app create [app] {} / {}'.format(argo_app_name, env['name']))

                # アプリケーション作成
                stdout_cd = subprocess.check_output(["argocd","app","create",argo_app_name,
                    "--repo",gitUrl,
                    "--path","./",
                    "--dest-name",cluster,
                    "--dest-namespace",namespace,
                    "--sync-option","CreateNamespace=true",
                    ],stderr=subprocess.STDOUT)
                globals.logger.debug(stdout_cd.decode('utf-8'))

            else:
                # update application
                exec_stat = multi_lang.get_text("EP035-0009", "ArgoCD設定 - アプリケーション更新")
                error_detail = multi_lang.get_text("EP035-0008", "ArgoCDの入力内容を確認してください")

                if ( 'name' in argo_app["spec"]["destination"] and cluster == argo_app["spec"]["destination"]["name"] ) \
                and namespace == argo_app["spec"]["destination"]["namespace"] \
                and gitUrl == argo_app["spec"]["source"]["repoURL"]:
                    # unchanged
                    globals.logger.debug('argocd app unchanged skip [app] {} / {}:'.format(argo_app_name, env['name']))

                else:
                    # update application
                    globals.logger.debug('argocd app set [app] {} / {}:'.format(argo_app_name, env['name']))
                    stdout_cd = subprocess.check_output(["argocd","app","set",argo_app_name,
                        "--repo",gitUrl,
                        "--path","./",
                        "--dest-name",cluster,
                        "--dest-namespace",namespace,
                        "--sync-option","CreateNamespace=true",
                        ],stderr=subprocess.STDOUT)

                    globals.logger.debug(stdout_cd.decode('utf-8'))

        ret_status = 200

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
    return  'epoch-ws-{}'.format(workspace_id)

def get_argo_cluster_name(workspace_id, environment_id):
    """ArgoCD cluster name

    Args:
        workspace_id (int): workspace_id
        environment_id (str): environment_id

    Returns:
        str: ArgoCD cluster name
    """
    return 'ws-{}-cluster-{}'.format(workspace_id,environment_id)

def get_argo_app_name(workspace_id,environment_id):
    """ArgoCD app name

    Args:
        workspace_id (int): workspace_id
        environment_id (str): environment_id

    Returns:
        str: ArgoCD app name
    """
    return 'ws-{}-{}'.format(workspace_id,environment_id)


def env_name_to_argo_app_name(workspace_id, environments, env_name):
    """Get the app name of ArgoCD from the environment name - 環境名からArgoCDのapp nameを取得します

    Args:
        workspace_id (int): workspace id
        enviroments (arr): Environment information list of workspace - workspaceの環境情報リスト
        env_name (str): enviroment name

    Returns:
        str: ArgoCD app name
    """
    for env in environments:
        if env["name"] == env_name:
            return get_argo_app_name(workspace_id, env["environment_id"])

    return None


if __name__ == "__main__":
    app.run(debug=eval(os.environ.get('API_DEBUG', "False")), host='0.0.0.0', port=int(os.environ.get('API_ARGOCD_PORT', '8000')), threaded=True)
