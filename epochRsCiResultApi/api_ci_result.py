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

from flask import Flask, request, abort, jsonify
from datetime import datetime
import os
import json
import re
import inspect
import globals
import common
from dbconnector import dbconnector
from dbconnector import dbcursor
import da_ci_result

# タスクのステータス保存用
TASK_STATUS_RUNNING='RUNNING'
TASK_STATUS_COMPLETE='COMPLETE'
TASK_STATUS_ERROR='ERROR'

# 設定ファイル読み込み・globals初期化
app = Flask(__name__)
app.config.from_envvar('CONFIG_API_CI_RESULT_PATH')
globals.init(app)


@app.route('/alive', methods=['GET'])
def alive():
    """死活監視

    Returns:
        Response: HTTP Respose
    """
    return jsonify({"result": "200", "time": str(datetime.now(globals.TZ))}), 200

@app.route('/workspace/<int:workspace_id>/tekton/task', methods=['POST','PUT'])
def post_tekton_task(workspace_id):
    """CI結果情報登録

    Returns:
        response: HTTP Respose
    """
    globals.logger.info('Register CI result information. workspace_id={}'.format(workspace_id))

    try:
        # image tagの生成
        image_tag = '{}.{}'.format(re.sub(r'.*/', '', request.json['git_branch']), datetime.now(globals.TZ).strftime("%Y%m%d-%H%M%S"))

        with dbconnector() as db, dbcursor(db) as cursor:
            
            # Requestからinfo項目を生成する
            info = request.json
            info['workspace_id'] = workspace_id
            info['status'] = TASK_STATUS_RUNNING
            info['container_registry_image_tag'] = image_tag

            # CI結果情報 insert実行(戻り値：追加したtask_id)
            task_id = da_ci_result.insert_tekton_pipeline_task(cursor, info)

            globals.logger.debug('insert task_id:{}'.format(str(task_id)))

        globals.logger.info('SUCCESS: Register CI result information. workspace_id={}, task_id={}, pipeline_id={}, status={}'.format(workspace_id, task_id,info['pipeline_id'], 200))

        return jsonify({"result": "200", "param" : { "task_id": task_id, "container_registry_image_tag": image_tag }}), 200

    except Exception as e:
        globals.logger.info('Fail: Register CI result information. workspace_id={}, task_id={}, pipeline_id={}, status={}'.format(workspace_id, task_id, task_id,info['pipeline_id'], 500))
        return common.serverError(e, "tekton_pipeline_task db registration error")

@app.route('/workspace/<int:workspace_id>/tekton/task/<int:task_id>', methods=['PATCH'])
def patch_tekton_task(workspace_id, task_id):
    """CI結果情報更新

    Args:
        workspace_id (int): ワークスペース ID
        task_id (int): task ID

    Returns:
        response: HTTP Respose
    """
    globals.logger.info('Update CI result information. workspace_id={}, task_id={}'.format(workspace_id, task_id))

    try:
        # Requestからinfo項目を生成する
        info = request.json

        with dbconnector() as db, dbcursor(db) as cursor:
            # CI結果情報更新
            upd_cnt = da_ci_result.update_tekton_pipeline_task(cursor, info, task_id)
            if upd_cnt == 0:
                # データがないときは404応答
                db.rollback()
                globals.logger.info('Fail: Update CI result information. ret_status={}, workspace_id={}, task_id={}, '.format(404, workspace_id, task_id))
                return jsonify({"result": "404" }), 404

            # 正常終了
            globals.logger.info('SUCCESS: Update CI result information. ret_status={}, workspace_id={}, task_id={} update_information_count={}'.format(200, workspace_id, task_id, upd_cnt))
            return jsonify({"result": "200"}), 200

    except Exception as e:
        return common.serverError(e, "tekton_pipeline_task db update error")

@app.route('/workspace/<int:workspace_id>/tekton/task', methods=['GET'])
def get_tekton_task(workspace_id):
    """CI結果情報取得

    Returns:
        response: HTTP Respose
    """

    try:
        globals.logger.info('Get CI result information. method={}, workspace_id={}'.format(request.method, workspace_id))

        with dbconnector() as db, dbcursor(db) as cursor:
            
            # CI result information select execution - CI結果情報 select実行
            fetch_rows = da_ci_result.select_tekton_pipeline_task(cursor, workspace_id)

        # Successful completion - 正常終了
        res_status = 200
        
        globals.logger.info('SUCCESS: Get CI result information. res_status={}, workspace_id={}, CI_result_information_count={}'.format(200, workspace_id, len(fetch_rows)))
        
        return jsonify({ "result": res_status, "rows": fetch_rows }), res_status

    except Exception as e:
        return common.serverError(e, "tekton_pipeline_task db registration error")


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('API_CI_RESULT_PORT', '8000')), threaded=True)