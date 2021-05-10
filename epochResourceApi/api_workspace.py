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

from flask import Flask, request, abort, jsonify
from datetime import datetime
import os
import json

import globals
import common
from dbconnector import dbconnector
from dbconnector import dbcursor

# 設定ファイル読み込み・globals初期化
app = Flask(__name__)
app.config.from_envvar('CONFIG_API_WORKSPACE_PATH')
globals.init(app)

# workspaceテーブルに確保済みのcolumn
workspace_allocated_columns=['workspace_id','create_at','update_at']

@app.route('/alive', methods=['GET'])
def alive():
    """死活監視

    Returns:
        Response: HTTP Respose
    """
    return jsonify({"result": "200", "time": str(datetime.now(globals.TZ))}), 200


@app.route('/workspace', methods=['POST'])
def create_workspace():
    """ワークスペース生成

    Returns:
        response: HTTP Respose
    """
    globals.logger.debug('CALL create_workspace')

    try:
        # Requestからspecification項目を生成する
        specification = convert_workspace_specification(request.json)

        with dbconnector() as db, dbcursor(db) as cursor:
            # workspace情報 insert実行
            cursor.execute('INSERT INTO workspace ( specification ) VALUES ( %(specification)s )',
                {
                    'specification' : json.dumps(specification)
                }
            )
            # 追加したワークスペースID
            workspace_id = cursor.lastrowid
            # workspace情報 データ再取得
            fetch_rows = select_workspace(cursor, workspace_id)

        # Response用のjsonに変換
        response_rows = convert_workspace_response(fetch_rows)

        globals.logger.info('CREATED workspace:{}'.format(str(id)))

        return jsonify({"result": "200", "rows": response_rows })

    except Exception as e:
        return common.serverError(e)


@app.route('/workspace', methods=['GET'])
def list_workspace():
    """ワークスペース一覧取得

    Returns:
        response: HTTP Respose
    """
    globals.logger.debug('CALL list_workspace')

    return jsonify({"result": "200", "time": str(datetime.now(globals.TZ))}), 200

@app.route('/workspace/<int:workspace_id>', methods=['GET'])
def get_workspace(workspace_id):
    """ワークスペース詳細

    Args:
        workspace_id (int): ワークスペースID

    Returns:
        response: HTTP Respose
    """
    globals.logger.debug('CALL get_workspace:{}'.format(workspace_id))

    return jsonify({"result": "200", "time": str(datetime.now(globals.TZ))}), 200

@app.route('/workspace/<int:workspace_id>', methods=['PUT'])
def update_workspace(workspace_id):
    """ワークスペース変更

    Args:
        workspace_id (int): ワークスペースID

    Returns:
        response: HTTP Respose
    """
    globals.logger.debug('CALL update_workspace:{}'.format(workspace_id))

    return jsonify({"result": "200", "time": str(datetime.now(globals.TZ))}), 200

@app.route('/workspace/<int:workspace_id>', methods=['DELETE'])
def delete_workspace(workspace_id):
    """ワークスペース削除

    Args:
        workspace_id (int): ワークスペースID

    Returns:
        response: HTTP Respose
    """
    globals.logger.debug('CALL delete_workspace:{}'.format(workspace_id))

    return jsonify({"result": "200", "time": str(datetime.now(globals.TZ))}), 200


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('API_WORKSPACE_PORT', '8000')), threaded=True)
