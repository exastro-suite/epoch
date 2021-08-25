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
    ],
    "pipeline" : [
        'pipeline-sa.yaml',
        'pipeline-task-start.yaml',
        'pipeline-task-git-clone.yaml',
        'pipeline-task-build-and-push.yaml',
        'pipeline-task-complete.yaml',
        'pipeline-build-and-push.yaml',
        'trigger-template-build-and-push.yaml',
        'webhook-secret.yaml',
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
dest_folder='/var/epoch/tekton/'

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
        param['proxy'] = {
            'http': os.environ['EPOCH_HTTP_PROXY'],
            'https': os.environ['EPOCH_HTTPS_PROXY'],
            'no_proxy': os.environ['EPOCH_NO_PROXY'],
        }

        # pipeline毎の設定（pipelinesで設定数分処理する）
        for pipeline in param['ci_config']['pipelines']:

            # git情報の設定（共通項目の取り込み）: pipelines_commonに設定されていれば設定値を優先、なければpipelineの値をそのまま使用
            pipeline['git_repositry'] = ( param['ci_config']['pipelines_common']['git_repositry'] | pipeline['git_repositry'] )
            pipeline['container_registry'] = ( param['ci_config']['pipelines_common']['container_registry'] | pipeline['container_registry'] )

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

            # TEKTON pipeline用の各種リソースの適用
            apply_tekton_pipeline(workspace_id, YAML_KIND_PIPELINE, param)

            # event listen情報取得(response用)
            eventlistener = get_event_listener_info(workspace_id)

        except Exception as e:
            try:
                # 適用途中のpipelineを削除
                delete_workspace_pipeline(workspace_id, YAML_KIND_PIPELINE)
            except Exception as e:
                pass    # 失敗は無視

            raise   # エラーをスロー

        return jsonify({"result": "200", "eventlistener": eventlistener}), 200

    except Exception as e:
        return common.serverError(e)


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
            globals.logger.debug('tekton pipeline apply start workspace_id:{} template:{}'.format(workspace_id, template))

            # templateの展開
            yamltext = render_template('tekton/{}/{}'.format(kind, template), param=param, workspace_id=workspace_id)

            # yaml一時ファイル生成
            path_yamlfile = '{}/{}'.format(dest_folder, template)
            with open(path_yamlfile, mode='w') as fp:
                fp.write(yamltext)

            # yaml情報の変数設定
            info = {
                "workspace_id" :    workspace_id,
                "kind" :            kind,
                "template" :        template,
                "yamltext" :        yamltext,
            }

            # 適用yaml情報の書き込み
            da_tekton.insert_organization(cursor, info)

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
            da_tekton.delete_tekton_pipeline_yaml(fetch_row['yaml_id'])

            db.commit()


def get_event_listener_info(workspace_id):
    """tekton event listener情報取得

    Args:
        workspace_id (int): ワークスペースID

    Returns:
        dict: tekton event listener情報
    """
    globals.logger.debug('start get_event_listener_info workspace_id:{}'.format(workspace_id))

    for i in range(globals.config['RESOURCE_CREATION_WAIT']):   # 作成されるまで繰り返し

        # kubectlにてeventlistener情報を取得する
        try:
            result_kubectl = subprocess.check_output(
                ['kubectl', 'get', 'eventlistener',
                '-n', tekton_pipeline_namespace(workspace_id),
                '-o', 'json',
                '--field-selector', 'metadata.name={}'.format(event_listener_name)
                ], stderr=subprocess.STDOUT)

        except subprocess.CalledProcessError as e:
            globals.logger.error('COMMAND ERROR RETURN:{}\n{}'.format(e.returncode, e.output.decode('utf-8')))
            raise # 再スロー

        eventlisterinfo = json.loads(result_kubectl.decode('utf-8'))

        if len(eventlisterinfo['items']) > 0:
            try:
                eventlistener = {}
                eventlistener['name'] = eventlisterinfo['items'][0]['status']['configuration']['generatedName']
                eventlistener['address'] = eventlisterinfo['items'][0]['status']['address']['url']
                # 情報取得に成功したらreturnする
                globals.logger.debug('event listener:{}'.format(json.dumps(eventlistener)))
                return eventlistener
            except Exception as e:
                pass

        time.sleep(1)

    # ループする間にリソースが作成されないときは例外を発生させて終了
    raise Exception('tekton event listener not found')



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


@app.route('/workspace/<int:workspace_id>/tekton/task', methods=['POST'])
def post_tekton_task(workspace_id):
    """tekton_pipeline_task生成

    Args:
        workspace_id (int): ワークスペースID

    Returns:
        Response: HTTP Respose
    """
    globals.logger.debug('CALL post_tekton_task:{}'.format(workspace_id))

    try:
        # image tagの生成
        image_tag = '{}.{}'.format(re.sub(r'.*/', '', request.json['git_branch']), datetime.now(globals.TZ).strftime("%Y%m%d-%H%M%S"))

        with dbconnector() as db, dbcursor(db) as cursor:

            info = request.json
            info['woekspace_id'] = workspace_id
            info['status'] = TASK_STATUS_RUNNING
            info['container_registry_image_tag'] = image_tag

            # tekton_pipeline_task情報の登録(戻り値:task_id)
            task_id = da_tekton.insert_tekton_pipeline_task(cursor, info)

            # こちらはDBCloseに纏めてコミットされることを考慮しているため単一コミットはしない

        return jsonify({"result": "200", "param" : { "task_id": task_id, "container_registry_image_tag": image_tag }}), 200

    except Exception as e:
        return common.serverError(e)


@app.route('/workspace/<int:workspace_id>/tekton/task/<int:task_id>', methods=['PATCH'])
def patch_tekton_task(workspace_id, task_id):
    """tekton_pipeline_task更新

    Args:
        workspace_id (int): ワークスペースID
        task_id (int): タスクID

    Returns:
        Response: HTTP Respose
    """
    globals.logger.debug('CALL patch_tekton_task:{},{}'.format(workspace_id, task_id))

    try:
        # # SQL生成
        # sqlstmt = ( 'UPDATE tekton_pipeline_task SET '
        #             + ','.join(map(lambda x: '{} = %({})s'.format(x,x), request.json.keys()))
        #             + ' WHERE task_id = %(task_id)s' )

        # # 更新パラメータ
        # update_param = request.json.copy()
        # update_param['task_id'] = task_id

        # 更新実行
        with dbconnector() as db, dbcursor(db) as cursor:
            upd_cnt = da_tekton.update_tekton_pipeline_task(cursor, request.json, task_id)

            if upd_cnt == 0:
                # データがないときは404応答
                db.rollback()
                return jsonify({"result": "404" }), 404

        # 正常応答
        return jsonify({"result": "200"}), 200

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
