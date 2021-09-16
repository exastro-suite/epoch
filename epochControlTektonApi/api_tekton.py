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
from dbconnector import dbconnector
from dbconnector import dbcursor
import da_tekton

# 設定ファイル読み込み・globals初期化
app = Flask(__name__)
app.config.from_envvar('CONFIG_API_TEKTON_PATH')
globals.init(app)

# yamlテンプレートファイル
templates = {
    "namespace": [
        'namespace.yaml',
        'pipeline-pvc.yaml',
        'reverse-proxy.yaml',
        'sonarqube.yaml',
        'reverse-proxy-sonarqube.yaml',
    ],
    "pipeline" : [
        'pipeline-sa.yaml',
        'pipeline-task-start.yaml',
        'pipeline-task-git-clone.yaml',
        'pipeline-task-sonarqube-scanner.yaml',
        'pipeline-task-build-and-push.yaml',
        'pipeline-task-complete.yaml',
        'pipeline-build-and-push.yaml',
        'sonar-settings-config.yaml',
        'trigger-template-build-and-push.yaml',
        #'webhook-secret.yaml',
        'trigger-sa.yaml',
        'trigger-binding-common.yaml',
        'trigger-binding-webhook.yaml',
        'trigger-binding-pipeline.yaml',
        'trigger-template-build-and-push.yaml',
        'event-listener.yaml',
    ],
}

# event lstener名
event_listener_name='event-listener'

# yamlの出力先
dest_folder='/var/epoch/tekton'

TASK_STATUS_RUNNING='RUNNING'
TASK_STATUS_COMPLETE='COMPLETE'
TASK_STATUS_ERROR='ERROR'

# tekton_pipeline_yamlのkind値
YAML_KIND_NAMESPACE = 'namespace'
YAML_KIND_PIPELINE = 'pipeline'

@app.route('/alive', methods=["GET"])
def alive():
    """死活監視

    Returns:
        Response: HTTP Respose
    """
    return jsonify({"result": "200", "time": str(datetime.now(globals.TZ))}), 200


@app.route('/workspace/<int:workspace_id>/tekton/pipeline', methods=['POST','PUT'])
def post_tekton_pipeline(workspace_id):
    """TEKTON pipeline生成

    Args:
        workspace_id (int): ワークスペースID

    Returns:
        Response: HTTP Respose
    """
    globals.logger.debug('CALL post_tekton_pipeline:{}'.format(workspace_id))

    try:
        #
        # パラメータ項目設定(テンプレート展開用変数設定)
        #
        param = request.json.copy()
        # namespace、eventlistener設定
        param['ci_config']['pipeline_namespace'] = tekton_pipeline_namespace(workspace_id)
        param['ci_config']['event_listener_name'] = event_listener_name
        # sonarqube設定
        param['ci_config']['sonarqube_password'] = os.environ['EPOCH_SONARQUBE_PASSWORD']
        # proxy設定
        param['proxy'] = {
            'http': os.environ['EPOCH_HTTP_PROXY'],
            'https': os.environ['EPOCH_HTTPS_PROXY'],
            'no_proxy': os.environ['EPOCH_NO_PROXY'],
        }

        # pipeline毎の設定（pipelinesで設定数分処理する）
        for pipeline in param['ci_config']['pipelines']:

            # git情報の設定（共通項目の取り込み）: pipelines_commonに設定されていれば設定値を優先、なければpipelineの値をそのまま使用
            git_repositry = param['ci_config']['pipelines_common']['git_repositry'].copy()
            git_repositry.update(pipeline['git_repositry'])
            pipeline['git_repositry'] = git_repositry

            container_registry = param['ci_config']['pipelines_common']['container_registry'].copy()
            container_registry.update(pipeline['container_registry'])
            pipeline['container_registry'] = container_registry

            # gitサーバー情報付加（secret用)
            giturl = urlparse(pipeline['git_repositry']['url'])
            pipeline['git_repositry']['secret_url'] = '{}://{}/'.format(giturl.scheme, giturl.netloc)

            # コンテナレジストリ情報付加
            pipeline['container_registry']['secret_server'] = 'index.docker.io/v1/'
            # 内部レジストリ時は実際作成されてから再度有効化
            # if pipeline['container_registry']['interface'] == 'dockerhub':
            #     pipeline['container_registry']['secret_server'] = 'index.docker.io/v1/'
            # else:
            #     giturl = urlparse('http://' + pipeline['container_registry']['image'])
            #     pipeline['container_registry']['secret_server'] = giturl.netloc + '/'
            
            pipeline['container_registry']['auth'] = base64.b64encode('{}:{}'.format(pipeline['container_registry']['user'], pipeline['container_registry']['password']).encode()).decode()

            # build branchの設定
            if pipeline['build']['branch'] is None:
                pipeline['build_refs'] = None
            elif len(pipeline['build']['branch']) == 0:
                pipeline['build_refs'] = None
            else:
                pipeline['build_refs'] = '[{}]'.format(','.join(map(lambda x: '\'refs/heads/'+x+'\'', pipeline['build']['branch'])))

            # sonarqube用
            pipeline['sonar_project_name'] = re.sub('\\.git$', '', re.sub('^https?://[^/][^/]*/', '', pipeline["git_repositry"]["url"]))
        #
        # TEKTON pipelineの削除
        #
        delete_workspace_pipeline(workspace_id, YAML_KIND_PIPELINE)

        #
        # TEKTON pipelineの適用
        #
        try:
            # TEKTON pipeline用のnamespaceの適用
            apply_tekton_pipeline(workspace_id, YAML_KIND_NAMESPACE, param)

            # SonarQubeの初期設定を行う
            sonar_token = sonarqube_initialize(workspace_id, param)
            param['ci_config']['sonar_token'] = sonar_token

            # TEKTON pipeline用の各種リソースの適用
            apply_tekton_pipeline(workspace_id, YAML_KIND_PIPELINE, param)

        except Exception as e:
            try:
                # 適用途中のpipelineを削除
                delete_workspace_pipeline(workspace_id, YAML_KIND_PIPELINE)
            except Exception as e:
                pass    # 失敗は無視

            raise   # エラーをスロー

        return jsonify({"result": "200"}), 200

    except Exception as e:
        return common.serverError(e)


def sonarqube_initialize(workspace_id, param):
    """SonarQubeの初期設定
        adminのパスワード変更, TOKENの払い出しを行う

    Args:
        workspace_id (int): ワークスペースID
        param (dict): ワークスペースパラメータ
    """
    globals.logger.debug('start sonarqube_initialize workspace_id:{}'.format(workspace_id))

    host = "http://sonarqube.{}.svc:9000/".format(param["ci_config"]["pipeline_namespace"])
    sonarqube_user_name = 'admin'
    sonarqube_user_password_old = 'admin'
    sonarqube_user_password = param['ci_config']['sonarqube_password']
    sonarqube_project_key_name = 'epoch_key'

    # パスワード変更
    try_count = 10
    for i in range(try_count):
        globals.logger.debug('password change count: ' + str(i))

        # SonarQubeコンテナが立ち上がるまで繰り返し試行
        try:
            time.sleep(10)

            api_path = "api/users/change_password"
            get_query = "?login={}&previousPassword={}&password={}".format(sonarqube_user_name, sonarqube_user_password_old, sonarqube_user_password)

            api_uri = host + api_path + get_query
            response = requests.post(api_uri, auth=HTTPBasicAuth(sonarqube_user_name, sonarqube_user_password_old), timeout=3)

            globals.logger.debug('code: {}, message: {}'.format(str(response.status_code), response.text))
            if response.status_code == 204:
                globals.logger.debug('SonarQube password change SUCCEED')
                break
            if response.status_code == 401:
                globals.logger.debug('SonarQube password has already changed')
                break

        except Exception as e:
            #globals.logger.error(''.join(list(traceback.TracebackException.from_exception(e).format())))
            #raise # 再スロー
            pass

    # TOKEN 削除 -> 払い出し
    try:
        get_query = '?login={}&name={}'.format(sonarqube_user_name, sonarqube_project_key_name)

        # 削除
        api_path = 'api/user_tokens/revoke'
        api_uri = host + api_path + get_query
        response = requests.post(api_uri, auth=HTTPBasicAuth(sonarqube_user_name, sonarqube_user_password), timeout=3)

        # 払い出し
        api_path = 'api/user_tokens/generate'
        api_uri = host + api_path + get_query
        response = requests.post(api_uri, auth=HTTPBasicAuth(sonarqube_user_name, sonarqube_user_password), timeout=3)
        response.raise_for_status()
        ret_data = json.loads(response.text)

        globals.logger.debug('SonarQube generate token SUCCEED')
        return ret_data['token']

    except Exception as e:
        globals.logger.error(''.join(list(traceback.TracebackException.from_exception(e).format())))
        raise # 再スロー


def apply_tekton_pipeline(workspace_id, kind, param):
    """tekton pipelineの適用
        templateにパラメータを埋込、適用する

    Args:
        workspace_id (int): ワークスペースID
        kind (str): 区分 "namespace"/"pipeline"
        param (dict): ワークスペースパラメータ
    """
    globals.logger.debug('start apply_tekton_pipeline_files workspace_id:{} kind:{}'.format(workspace_id, kind))

    with dbconnector() as db, dbcursor(db) as cursor:

        for template in templates[kind]:
            globals.logger.debug('* tekton pipeline apply start workspace_id:{} template:{}'.format(workspace_id, template))

            try:
                # templateの展開
                yamltext = render_template('tekton/{}/{}'.format(kind, template), param=param, workspace_id=workspace_id)
                globals.logger.debug(' render_template finish')

                # ディレクトリ作成
                os.makedirs(dest_folder, exist_ok=True)

                # yaml一時ファイル生成
                path_yamlfile = '{}/{}'.format(dest_folder, template)
                with open(path_yamlfile, mode='w') as fp:
                    fp.write(yamltext)

                globals.logger.debug(' yamlfile output finish')

            except Exception as e:
                globals.logger.error('tekton pipeline yamlfile create workspace_id:{} template:{}'.format(workspace_id, template))
                raise

            # yaml情報の変数設定
            info = {
                "workspace_id" :    workspace_id,
                "kind" :            kind,
                "template" :        template,
                "yamltext" :        yamltext,
            }

            # 適用yaml情報の書き込み
            da_tekton.insert_tekton_pipeline_yaml(cursor, info)

            db.commit()

            # kubectl実行
            try:
                result_kubectl = subprocess.check_output(['kubectl', 'apply', '-f', path_yamlfile], stderr=subprocess.STDOUT)
                globals.logger.debug('COMMAAND SUCCEED: kubectl apply -f {}\n{}'.format(path_yamlfile, result_kubectl.decode('utf-8')))

            except subprocess.CalledProcessError as e:
                globals.logger.error('COMMAND ERROR RETURN:{}\n{}'.format(e.returncode, e.output.decode('utf-8')))
                raise # 再スロー


def delete_workspace_pipeline(workspace_id, kind):
    """tekton pipelineの削除
        tekton_pipeline_yamlテーブルから適用済みのyamlを取得し削除する

    Args:
        workspace_id (int): ワークスペースID
        kind (str): 区分 "namespace"/"pipeline"
    """
    globals.logger.debug('start delete_workspace_pipeline_files workspace_id:{} kind:{}'.format(workspace_id, kind))

    with dbconnector() as db, dbcursor(db) as cursor:
        # 適用済みのyaml取得
        fetch_rows = da_tekton.select_tekton_pipeline_yaml_id(cursor, workspace_id, kind)

    with tempfile.TemporaryDirectory() as tempdir, dbconnector() as db, dbcursor(db) as cursor:
        for fetch_row in fetch_rows:
            globals.logger.debug('tekton pipeline delete workspace_id:{} template:{}'.format(workspace_id, fetch_row['filename']))

            # yaml一時ファイル生成
            path_yamlfile = '{}/{}'.format(tempdir, fetch_row['filename'])
            with open(path_yamlfile, mode='w') as fp:
                fp.write(fetch_row['yamltext'])

            # kubectl実行
            try:
                result_kubectl = subprocess.check_output(['kubectl', 'delete', '-f', path_yamlfile], stderr=subprocess.STDOUT)
                globals.logger.debug('COMMAAND SUCCEED: kubectl delete -f {}\n{}'.format(path_yamlfile, result_kubectl.decode('utf-8')))

            except subprocess.CalledProcessError as e:
                globals.logger.error('COMMAND ERROR RETURN:{}\n{}'.format(e.returncode, e.output.decode('utf-8')))
                # 削除失敗は無視

            # リソースを削除したら適用済みのyaml情報を削除する
            da_tekton.delete_tekton_pipeline_yaml(cursor, fetch_row['yaml_id'])

            db.commit()


@app.route('/workspace/<int:workspace_id>/tekton/pipeline', methods=['DELETE'])
def delete_tekton_pipeline(workspace_id):
    """TEKTON pipeline削除

    Args:
        workspace_id (int): ワークスペースID

    Returns:
        Response: HTTP Respose
    """
    globals.logger.debug('CALL delete_tekton_pipeline:{}'.format(workspace_id))

    try:
        # pipelineを削除
        delete_workspace_pipeline(workspace_id, YAML_KIND_PIPELINE)
        # tektonの実行情報を削除（削除しないと止まってしまうため）
        delete_tekton_pipelinerun(workspace_id)
        # namespaceを削除
        delete_workspace_pipeline(workspace_id, YAML_KIND_NAMESPACE)

        return jsonify({"result": "200"}), 200

    except Exception as e:
        return common.serverError(e)


def delete_tekton_pipelinerun(workspace_id):
    """tekton pipelinerun情報削除

    Args:
        workspace_id (int): ワークスペースID
    """
    globals.logger.debug('start delete_tekton_pipelinerun workspace_id:{}'.format(workspace_id))

    try:
        result_kubectl = subprocess.check_output(
            ['kubectl', 'tkn', 'pipelinerun', 'delete', '--all', '-f',
            '-n', tekton_pipeline_namespace(workspace_id),
            ], stderr=subprocess.STDOUT)
        
        globals.logger.debug('COMMAAND SUCCEED: kubectl tkn pipelinerun delete --all -f\n{}'.format(result_kubectl.decode('utf-8')))

    except subprocess.CalledProcessError as e:
        globals.logger.error('COMMAND ERROR RETURN:{}\n{}'.format(e.returncode, e.output.decode('utf-8')))
        raise # 再スロー

@app.route('/workspace/<int:workspace_id>/tekton/pipelinerun', methods=['GET'])
def get_tekton_pipelinerun(workspace_id):
    """TEKTON pipeline実行結果取得

    Args:
        workspace_id (int): ワークスペースID

    Returns:
        Response: HTTP Respose
    """
    globals.logger.debug('CALL get_tekton_pipelinerun:{}'.format(workspace_id))

    try:
        #    latest (bool): 最新のみ
        if request.args.get('latest') is not None:
            latest = request.args.get('latest') == "True"
        else:
            latest = False

        try:
            # TEKTON CLIにてpipelinerunのListを取得
            result_kubectl = subprocess.check_output(
                ['kubectl', 'tkn', 'pipelinerun', 'list', '-o', 'json', '-n', tekton_pipeline_namespace(workspace_id),], stderr=subprocess.STDOUT)

        except subprocess.CalledProcessError as e:
            # コマンド実行エラー
            globals.logger.debug('COMMAND ERROR RETURN:{}\n{}'.format(e.returncode, e.output.decode('utf-8')))
            raise # 再スロー

        # TEKTON CLIにてpipelinerunのListの結果jsonをdictに変換
        plRunlist = json.loads(result_kubectl.decode('utf-8'))

        if latest:
            #
            # 最新のみ返すとき
            #
            resRowsDict = {}
            for plRunitem in plRunlist['items']:
                resPlRunitem = get_responsePipelineRunItem(plRunitem)

                idx = int(resPlRunitem['pipeline_id'])

                if idx in resRowsDict:
                    # そのpipeline idの結果が既に存在するときはstart_timeで比較し、大きい方を残す                
                    if resRowsDict[idx]['start_time'] < resPlRunitem['start_time']:
                        resRowsDict[idx] = resPlRunitem
                else:
                    # そのpipeline idの結果が無いときは格納
                    resRowsDict[idx] = resPlRunitem

            # 結果をソートして格納
            resRows = []
            for idx in sorted(resRowsDict):
                resRows.append(resRowsDict[idx])
        else:
            #
            # 全件返すとき
            #
            resRows = []
            for plRunitem in plRunlist['items']:
                resPlRunitem = get_responsePipelineRunItem(plRunitem)
                resRows.append(resPlRunitem)

        globals.logger.debug(json.dumps(resRows))

        # 正常応答
        return jsonify({"result": "200", "rows": resRows}), 200

    except Exception as e:
        return common.serverError(e)

def get_responsePipelineRunItem(plRunitem):
    """TEKTON CLI pipelinerun list結果の 1 pipelinerun結果を解析し、レスポンスの1明細分データを生成する

    Args:
        plRunitem (dict): TEKTON CLI pipelinerun listの結果明細(1 pipelinerun)

    Returns:
        dict: レスポンスの1明細分データ
    """
    # レスポンス用情報格納変数の初期化
    resPlRunitem = {}

    # 情報格納
    resPlRunitem['task_id'] = int(get_taskResult(plRunitem, 'task-start', 'task_id'))
    resPlRunitem['pipeline_id'] = int(plRunitem['metadata']['labels']['pipeline_id'])
    resPlRunitem['pipelinerun_name'] = plRunitem['metadata']['name']
    resPlRunitem['repository_url'] = get_pipelineParameter(plRunitem,'git_repository_url')
    resPlRunitem['build_branch'] = convert_branch(get_pipelineParameter(plRunitem,'git_branch'))
    resPlRunitem['start_time'] = convert_date_format(plRunitem['status']['startTime'])
    resPlRunitem['finish_time'] = convert_date_format(plRunitem['status']['completionTime'])
    resPlRunitem['status'] = plRunitem['status']['conditions'][0]['reason']
    resPlRunitem['container_image'] = '{}:{}'.format(get_pipelineParameter(plRunitem,'container_registry_image'), get_taskResult(plRunitem, 'task-start', 'container_registry_image_tag'))

    # タスク情報の格納
    resPlRunitem['tasks'] = []
    for task in plRunitem['status']['pipelineSpec']['tasks']:
        resPlRunitem['tasks'].append(
            dict({'name' : task['name']}, **get_taskStatus(plRunitem, task['name']))            
        )

    return  resPlRunitem


def get_pipelineParameter(plRunitem, parameterName):
    """パイプラインパラメータ値取得

    Args:
        plRunitem (dict): TEKTON CLI pipelinerun listの結果明細(1 pipelinerun)
        parameterName (str): パラメータ名

    Returns:
        str: パラメータ値
    """
    # spec.params配下にpipelinerunのパラメータが配列化されているので、nameが合致するものを探してvalueを返す
    for param in plRunitem['spec']['params']:
        if param['name'] == parameterName:
            return param['value']

    return None

def get_taskResult(plRunitem, taskname, resultName):
    """タスク名、Result項目名を指定しタスクResult値を取得する

    Args:
        plRunitem (dict): TEKTON CLI pipelinerun listの結果明細(1 pipelinerun)
        taskname (str): タスク名
        resultName (str): Result項目名

    Returns:
        (str): タスクResult値
    """
    # status.taskRuns[*]にtask毎、Result項目毎で格納されているので、タスク名、Result項目名が合致するものを探して値を返します
    for taskRun in plRunitem['status']['taskRuns'].values():
        if taskRun['pipelineTaskName'] == taskname:
            for taskResult in taskRun['status']['taskResults']:
                if taskResult['name'] == resultName:
                    return taskResult['value']
    return None

def get_taskStatus(plRunitem, taskname):
    """タスクステータス（状態、開始日時、終了日時）取得

    Args:
        plRunitem (dict): TEKTON CLI pipelinerun listの結果明細(1 pipelinerun)
        taskname (str): タスク名

    Returns:
        (dict): タスクステータス情報
    """
    # status.taskRuns[*]にtaskの結果が格納されているので、指定タスク名の情報を探して値を返します
    for taskrunname, taskrun in plRunitem['status']['taskRuns'].items():
        if taskrun['pipelineTaskName'] == taskname:
            return  {
                        "taskrun_name" : taskrunname,
                        "start_time" : convert_date_format(taskrun['status']['startTime']),
                        "finish_time" : convert_date_format(taskrun['status']['completionTime']),
                        "status" : taskrun['status']['conditions'][0]['reason'],
                    }
    return {}

def convert_branch(branch):
    """branchパラメータをレスポンス(表示)形式に変換

    Args:
        branch (str): branchパラメータ

    Returns:
        str: branchパラメータ レスポンス(表示)形式
    """
    # branchパラメータの"refs/heads/"の部分を取り除く
    return re.sub('^.*/', '', branch)


def convert_date_format(tekton_date_string):
    """TEKTON結果日時を表示形式(JST)に変換

    Args:
        tekton_date_string (str): TEKTON結果日時

    Returns:
        str: 日時表示形式(JST)
    """
    # TEKTONのGMT時間を日本時間(JST)で取得
    return datetime.strptime(tekton_date_string, '%Y-%m-%dT%H:%M:%SZ').astimezone(timezone(timedelta(hours=9))).strftime('%Y/%m/%d %H:%M:%S')

@app.route('/workspace/<int:workspace_id>/tekton/taskrun/<taskrun_name>/logs', methods=['GET'])
def get_tekton_taskrun_logs(workspace_id, taskrun_name):
    """TEKTON taskログ取得

    Args:
        workspace_id (int): ワークスペースID
        taskrun_name (string): taskrun名
    Returns:
        Response: HTTP Respose
    """
    globals.logger.debug('CALL get_tekton_taskrun:{},{}'.format(workspace_id, taskrun_name))

    try:
        result_kubectl = subprocess.check_output(
            ['kubectl', 'tkn', 'taskrun', 'logs', taskrun_name,
            '-n', tekton_pipeline_namespace(workspace_id),
            ], stderr=subprocess.STDOUT)
        
        globals.logger.debug('COMMAAND SUCCEED: kubectl tkn taskrun logs')

        # 正常応答
        return jsonify({"result": "200", "log" : result_kubectl.decode('utf-8')}), 200

    except Exception as e:
        return common.serverError(e)


def tekton_pipeline_namespace(workspace_id):
    """TEKTON pipeline用namespace取得

    Args:
        workspace_id (int): ワークスペースID

    Returns:
        str: TEKTON pipeline用namespace
    """
    # 複数のnamespace名は、workspace複数化時に検討する
    # return  'ws-tekton-pipeline-{}'.format(workspace_id)
    return  'epoch-tekton-pipeline-{}'.format(workspace_id)


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('API_TEKTON_PORT', '8000')), threaded=True)
