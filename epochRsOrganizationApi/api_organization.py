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
import da_organization

# 設定ファイル読み込み・globals初期化
app = Flask(__name__)
app.config.from_envvar('CONFIG_API_ORGANIZATION_PATH')
globals.init(app)


@app.route('/alive', methods=['GET'])
def alive():
    """死活監視

    Returns:
        Response: HTTP Respose
    """
    return jsonify({"result": "200", "time": str(datetime.now(globals.TZ))}), 200

@app.route('/organization', methods=['POST'])
def create_organization():
    """オーガナイゼーション登録

    Returns:
        response: HTTP Respose
    """
    globals.logger.debug('CALL create_organization')

    try:
        # Requestからinfo項目を生成する
        info = request.json

        with dbconnector() as db, dbcursor(db) as cursor:
            # organization情報 insert実行(戻り値：追加したorganizationID)
            organization_id = da_organization.insert_organization(cursor, info)

            globals.logger.debug('insert organization_id:{}'.format(str(organization_id)))

            # organization履歴追加
            da_organization.insert_history(cursor, organization_id)

            # organization情報 データ再取得
            fetch_rows = da_organization.select_organization_id(cursor, organization_id)

        # Response用のjsonに変換
        response_rows = fetch_rows

        globals.logger.info('CREATED organization:{}'.format(str(organization_id)))

        return jsonify({"result": "200", "rows": response_rows }), 200

    except Exception as e:
        return common.serverError(e, "organization db registration error")


@app.route('/organization', methods=['GET'])
def list_organization():
    """オーガナイゼーション一覧取得

    Returns:
        response: HTTP Respose
    """
    globals.logger.debug('CALL list_organization')

    try:
        with dbconnector() as db, dbcursor(db) as cursor:
            # select実行
            fetch_rows = da_organization.select_organization(cursor)

        # Response用のjsonに変換
        response_rows = convert_organization_response(fetch_rows)

        return jsonify({"result": "200", "rows": response_rows, "time": str(datetime.now(globals.TZ))}), 200

    except Exception as e:
        return common.serverError(e)

@app.route('/organization/<int:organization_id>', methods=['GET'])
def get_organization(organization_id):
    """オーガナイゼーション詳細

    Args:
        organization_id (int): organization ID

    Returns:
        response: HTTP Respose
    """
    globals.logger.debug('CALL get_workspace:{}'.format(organization_id))

    try:
        with dbconnector() as db, dbcursor(db) as cursor:
            # organization情報データ取得
            fetch_rows = da_organization.select_organization_id(cursor, organization_id)

        if len(fetch_rows) > 0:
            # Response用のjsonに変換
            response_rows = convert_organization_response(fetch_rows)

            return jsonify({"result": "200", "rows": response_rows, "time": str(datetime.now(globals.TZ))}), 200

        else:
            # 0件のときは404応答
            return jsonify({"result": "404" }), 404

    except Exception as e:
        return common.serverError(e)

def convert_organization_response(fetch_rows):
    """レスポンス用JSON変換
        organization情報のselect(fetch)した結果をレスポンス用のjsonに変換する
    Args:
        fetch_rows (dict): organizationテーブル取得結果

    Returns:
        dict: レスポンス用json
    """
    result = []
    for fetch_row in fetch_rows:
        result_row['organization_id'] = fetch_row['organization_id']
        result_row['organization_name'] = fetch_row['organization_name']
        result_row = json.loads(fetch_row['additional_information'])
        result_row['create_at'] = fetch_row['create_at']
        result_row['update_at'] = fetch_row['update_at']
        result.append(result_row)
    return result

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('API_ORGANIZATION_PORT', '8000')), threaded=True)