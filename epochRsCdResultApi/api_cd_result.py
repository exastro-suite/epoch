#   Copyright 2022 NEC Corporation
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
import inspect
import os
import json
import re

import globals
import common
from dbconnector import dbconnector
from dbconnector import dbcursor
import da_cd_result

# 設定ファイル読み込み・globals初期化
app = Flask(__name__)
app.config.from_envvar('CONFIG_API_CD_RESULT_PATH')
globals.init(app)


@app.route('/alive', methods=['GET'])
def alive():
    """死活監視 alive monitoring

    Returns:
        Response: HTTP Respose
    """
    return jsonify({"result": "200", "time": str(datetime.now(globals.TZ))}), 200

@app.route('/workspace/<int:workspace_id>/cd/result', methods=['GET'])
def call_cd_result(workspace_id):
    """CD結果の呼び出し口 CD result call

    Args:
        workspace_id (int): workspace id

    Returns:
        response: HTTP Respose
    """

    try:
        globals.logger.debug('=' * 50)
        globals.logger.debug('CALL {}:from[{}] workspace_id[{}]'.format(inspect.currentframe().f_code.co_name, request.method, workspace_id))
        globals.logger.debug('=' * 50)

        if request.method == 'GET':
            # cd execute (get)
            return cd_result_list(workspace_id=workspace_id)
        else:
            # Error
            raise Exception("method not support!")

    except Exception as e:
        return common.serverError(e, "{} error".format(inspect.currentframe().f_code.co_name))

@app.route('/workspace/<int:workspace_id>/cd/result/<int:cd_result_id>', methods=['PUT', 'GET'])
def call_cd_result_by_id(workspace_id, cd_result_id):
    """結果IDによるCD結果の呼び出し口 CD result call by cd_result_id

    Args:
        workspace_id (int): workspace id
        cd_result_id (int): cd-result id

    Returns:
        response: HTTP Respose
    """

    try:
        globals.logger.debug('=' * 50)
        globals.logger.debug('CALL {}:from[{}] workspace_id[{}] cd_result_id[{}]'.format(inspect.currentframe().f_code.co_name, request.method, workspace_id, cd_result_id))
        globals.logger.debug('=' * 50)

        if request.method == 'PUT':
            # cd execute (get)
            return cd_result_update(workspace_id, cd_result_id)
        if request.method == 'GET':
            # cd execute (get)
            return cd_result_list(workspace_id=workspace_id, cd_result_id=cd_result_id)
        else:
            # Error
            raise Exception("method not support!")

    except Exception as e:
        return common.serverError(e, "{} error".format(inspect.currentframe().f_code.co_name))

@app.route('/workspace/<int:workspace_id>/member/<string:username>/cd/result/<int:cd_result_id>', methods=['POST','GET'])
def call_cd_result_member(workspace_id, username, cd_result_id):
    """メンバーによるCD結果の呼び出し口 CD result call by members

    Args:
        workspace_id (int): workspace id
        username (str): username
        cd_result_id (int): cd-result id

    Returns:
        response: HTTP Respose
    """

    try:
        globals.logger.debug('=' * 50)
        globals.logger.debug('CALL {}:from[{}] workspace_id[{}] member[{}] cd_result_id[{}]'.format(inspect.currentframe().f_code.co_name, request.method, workspace_id, username, cd_result_id))
        globals.logger.debug('=' * 50)

        if request.method == 'POST':
            # cd execute (post)
            return cd_result_insert(workspace_id, cd_result_id, username)
        elif request.method == 'GET':
            # cd execute (get)
            return cd_result_list(workspace_id=workspace_id, cd_result_id=cd_result_id, username=username)
        else:
            # Error
            raise Exception("method not support!")

    except Exception as e:
        return common.serverError(e, "{} error".format(inspect.currentframe().f_code.co_name))

def cd_result_insert(workspace_id, cd_result_id, username):
    """CD結果登録 cd result insert

    Args:
        workspace_id (int): workspace id
        cd_result_id (int): cd-result id
        username (str): username

    Returns:
        response: HTTP Respose
    """

    try:
        globals.logger.debug('CALL {}:from[{}] workspace_id[{}] member[{}]'.format(inspect.currentframe().f_code.co_name, request.method, workspace_id, username))

        with dbconnector() as db, dbcursor(db) as cursor:
            
            # Requestからcontentsを設定 Set contents from Request
            contents = request.json.copy()

            # cd-result insert実行
            lastrowid = da_cd_result.insert_cd_result(cursor, workspace_id, cd_result_id, username, contents)

            globals.logger.debug('insert lastrowid:{}'.format(lastrowid))

        return jsonify({"result": "200", "lastrowid": lastrowid}), 200

    except Exception as e:
        return common.serverError(e, "{} error".format(inspect.currentframe().f_code.co_name))

def cd_result_update(workspace_id, cd_result_id):
    """CD結果更新 cd result update

    Args:
        workspace_id (int): workspace id
        cd_result_id (int): cd-result id

    Returns:
        response: HTTP Respose
    """

    try:
        globals.logger.debug('CALL {}:from[{}] workspace_id[{}] cd_result_id[{}]'.format(inspect.currentframe().f_code.co_name, request.method, workspace_id, cd_result_id))

        with dbconnector() as db, dbcursor(db) as cursor:
            
            # Requestからcontentsを設定 Set contents from Request
            contents = request.json.copy()

            # cd-result update実行
            upd_cnt = da_cd_result.update_cd_result(cursor, workspace_id, cd_result_id, contents)

            if upd_cnt == 0:
                # データがないときは404応答
                db.rollback()
                return jsonify({"result": "404"}), 404

            globals.logger.debug('update cd_result_id:{}'.format(cd_result_id))

        return jsonify({"result": "200"}), 200

    except Exception as e:
        return common.serverError(e, "{} error".format(inspect.currentframe().f_code.co_name))

def cd_result_list(workspace_id, cd_result_id=None, username=None, latest=False):
    """CD結果取得 cd result list

    Args:
        workspace_id (int): workspace id
        cd_result_id (int): cd-result id
        username (str): username
        latest (Bool): latest True or False

    Returns:
        response: HTTP Respose
    """

    try:
        globals.logger.debug('CALL {}:from[{}] workspace_id[{}] cd_result_id[{}] username[{}] latest[{}]'.format(inspect.currentframe().f_code.co_name, request.method, workspace_id, cd_result_id, username, latest))

        globals.logger.debug('CALL {}:args[{}]'.format(inspect.currentframe().f_code.co_name, request.args))
        #    latest (bool): 最新のみ
        if request.args.get('latest') is not None:
            latest = request.args.get('latest') == "True"
        else:
            latest = False

        #    latest (bool): 最新のみ
        if request.args.get('cd_status_in') is not None:
            cd_status_in = request.args.get('cd_status_in').split(".")
        else:
            cd_status_in = []

        with dbconnector() as db, dbcursor(db) as cursor:
            
            # CD結果履歴の取得 Get CD result history
            fetch_rows = da_cd_result.select_cd_result(cursor, workspace_id, cd_result_id, cd_status_in, username, latest)

        return jsonify({"result": "200", "rows": fetch_rows })

    except Exception as e:
        return common.serverError(e, "{} error".format(inspect.currentframe().f_code.co_name))

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('API_CD_RESULT_PORT', '8000')), threaded=True)