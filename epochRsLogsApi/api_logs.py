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
import da_logs

# ログの種類 Log kind
LOG_KIND_ERROR='Error'
LOG_KIND_INFO='Infomation'
LOG_KIND_UPDATE='Update'

# 設定ファイル読み込み・globals初期化
app = Flask(__name__)
app.config.from_envvar('CONFIG_API_LOGS_PATH')
globals.init(app)


@app.route('/alive', methods=['GET'])
def alive():
    """死活監視

    Returns:
        Response: HTTP Respose
    """
    return jsonify({"result": "200", "time": str(datetime.now(globals.TZ))}), 200

@app.route('/logs', methods=['POST'])
def call_logs():
    """ログ出力処理

    Returns:
        response: HTTP Respose
    """

    try:
        globals.logger.debug('=' * 50)
        globals.logger.debug('CALL {}:from[{}]'.format(inspect.currentframe().f_code.co_name, request.method))
        globals.logger.debug('=' * 50)

        # log出力 log output
        return logs_insert()

    except Exception as e:
        return common.serverError(e, "{} error".format(inspect.currentframe().f_code.co_name))

@app.route('/logs/<string:log_kind>', methods=['POST'])
def call_logs_kind(log_kind):
    """ログ出力処理

    Args:
        log_kind (str): log_kind

    Returns:
        response: HTTP Respose
    """

    try:
        globals.logger.debug('=' * 50)
        globals.logger.debug('CALL {}:from[{}] log_kind[{}]'.format(inspect.currentframe().f_code.co_name, request.method, log_kind))
        globals.logger.debug('=' * 50)

        # log出力 log output
        return logs_insert(log_kind=log_kind)

    except Exception as e:
        return common.serverError(e, "{} error".format(inspect.currentframe().f_code.co_name))

@app.route('/workspace/<int:workspace_id>/logs/<string:log_kind>', methods=['POST'])
def call_workspace_logs(workspace_id, log_kind):
    """workspace情報毎のログ出力処理

    Args:
        workspace_id (int): workspace id
        log_kind (str): log_kind

    Returns:
        response: HTTP Respose
    """

    try:
        globals.logger.debug('=' * 50)
        globals.logger.debug('CALL {}:from[{}] workspace_id[{}] log_kind[{}]'.format(inspect.currentframe().f_code.co_name, request.method, workspace_id, log_kind))
        globals.logger.debug('=' * 50)

        # log出力 log output
        return logs_insert(workspace_id=workspace_id, log_kind=log_kind)

    except Exception as e:
        return common.serverError(e, "{} error".format(inspect.currentframe().f_code.co_name))

@app.route('/workspace/<int:workspace_id>/member/<string:username>/logs/<string:log_kind>', methods=['POST'])
def call_workspace_member_logs(workspace_id, username, log_kind):
    """workspace情報のメンバーごとのログ出力呼び出し Log output call for each member of workspace information

    Args:
        workspace_id (int): workspace id
        username (str): username
        log_kind (str): log_kind

    Returns:
        response: HTTP Respose
    """

    try:
        globals.logger.debug('=' * 50)
        globals.logger.debug('CALL {}:from[{}] workspace_id[{}] member[{}] log_kind[{}]'.format(inspect.currentframe().f_code.co_name, request.method, workspace_id, username, log_kind))
        globals.logger.debug('=' * 50)

        # log出力 log output
        return logs_insert(workspace_id=workspace_id, username=username, log_kind=log_kind)

    except Exception as e:
        return common.serverError(e, "{} error".format(inspect.currentframe().f_code.co_name))

def logs_insert(workspace_id=None, username=None, log_kind=None):
    """ログ出力 Log output

    Args:
        workspace_id (int): workspace id
        username (str): username
        log_kind (str): log_kind

    Returns:
        response: HTTP Respose
    """

    try:
        globals.logger.debug('CALL {}:from[{}] workspace_id[{}] member[{}] log_kind[{}]'.format(inspect.currentframe().f_code.co_name, request.method, workspace_id, username, log_kind))

        with dbconnector() as db, dbcursor(db) as cursor:
            
            # Requestからcontentsを設定 Set contents from Request
            contents = request.json.copy()

            # logs insert実行
            log_id = da_logs.insert_logs(cursor, workspace_id, username, log_kind, contents)

            globals.logger.debug('insert log_id:{}'.format(log_id))

        return jsonify({"result": "200"}), 200

    except Exception as e:
        return common.serverError(e, "{} error".format(inspect.currentframe().f_code.co_name))

if __name__ == "__main__":
    app.run(debug=eval(os.environ.get('API_DEBUG', "False")), host='0.0.0.0', port=int(os.environ.get('API_LOGS_PORT', '8000')), threaded=True)