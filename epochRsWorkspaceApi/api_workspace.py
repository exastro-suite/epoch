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
import da_workspace
import da_manifest
import da_workspace_access

# 設定ファイル読み込み・globals初期化
app = Flask(__name__)
app.config.from_envvar('CONFIG_API_WORKSPACE_PATH')
globals.init(app)
app_name = ""
exec_stat = ""
exec_detail = ""

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
    app_name = "ワークスペース情報登録:"
    exec_stat = "初期化"
    exec_detail = ""
    globals.logger.debug(request.json)

    try:
        # Requestからspecification項目を生成する
        specification = convert_workspace_specification(request.json)

        exec_stat = "DB接続"
        with dbconnector() as db, dbcursor(db) as cursor:
            # workspace情報 insert実行(戻り値：追加したワークスペースID)
            exec_stat = "登録実行"
            workspace_id = da_workspace.insert_workspace(cursor, specification)

            globals.logger.debug('insert workspaced_id:{}'.format(str(workspace_id)))

            # workspace履歴追加
            exec_stat = "登録実行(履歴)"
            da_workspace.insert_history(cursor, workspace_id)

            # workspace情報 データ再取得
            exec_stat = "登録データ確認"
            fetch_rows = da_workspace.select_workspace_id(cursor, workspace_id)

        # Response用のjsonに変換
        response_rows = fetch_rows

        globals.logger.info('CREATED workspace:{}'.format(str(workspace_id)))

        return jsonify({"result": "200", "rows": response_rows })

    except Exception as e:
        return common.serverError(e, app_name + exec_stat, exec_detail)


@app.route('/workspace', methods=['GET'])
def list_workspace():
    """ワークスペース一覧取得

    Returns:
        response: HTTP Respose
    """
    globals.logger.debug('CALL list_workspace')

    try:
        with dbconnector() as db, dbcursor(db) as cursor:
            # select実行
            fetch_rows = da_workspace.select_workspace(cursor)

        # Response用のjsonに変換
        response_rows = convert_workspace_response(fetch_rows)

        return jsonify({"result": "200", "rows": response_rows, "time": str(datetime.now(globals.TZ))}), 200

    except Exception as e:
        return common.serverError(e)

@app.route('/workspace/<int:workspace_id>', methods=['GET'])
def get_workspace(workspace_id):
    """ワークスペース詳細

    Args:
        workspace_id (int): ワークスペースID

    Returns:
        response: HTTP Respose
    """
    globals.logger.debug('CALL get_workspace:{}'.format(workspace_id))

    try:
        with dbconnector() as db, dbcursor(db) as cursor:
            # workspace情報データ取得
            fetch_rows = da_workspace.select_workspace_id(cursor, workspace_id)

        if len(fetch_rows) > 0:
            # Response用のjsonに変換
            response_rows = convert_workspace_response(fetch_rows)

            return jsonify({"result": "200", "rows": response_rows, "time": str(datetime.now(globals.TZ))}), 200

        else:
            # 0件のときは404応答
            return jsonify({"result": "404" }), 404

    except Exception as e:
        return common.serverError(e)

@app.route('/workspace/<int:workspace_id>', methods=['PUT', 'PATCH'])
def update_workspace(workspace_id):
    """ワークスペース変更

    Args:
        workspace_id (int): ワークスペースID

    Returns:
        response: HTTP Respose
    """
    try:
        if request.method == 'PUT':
            # ワークスペース更新 put workspace
            put_workspace(workspace_id)
        elif request.method == 'PATCH':
            # ワークスペース更新パッチ patch update workspace
            patch_workspace(workspace_id)
        else:
            # Error
            raise Exception("method not support!")
        
    except Exception as e:
        return common.serverError(e)

def put_workspace(workspace_id):
    """ワークスペース更新

    Args:
        workspace_id (int): ワークスペースID

    Returns:
        response: HTTP Respose
    """
    globals.logger.debug("CALL put_workspace:{}".format(workspace_id))
    app_name = "ワークスペース情報更新:"
    exec_stat = "初期化"
    exec_detail = ""

    try:
        # Requestからspecification項目を生成する
        specification = convert_workspace_specification(request.json)

        exec_stat = "DB接続"
        with dbconnector() as db, dbcursor(db) as cursor:
            # workspace情報 update実行
            exec_stat = "更新実行"
            upd_cnt = da_workspace.update_workspace(cursor, specification, workspace_id)

            if upd_cnt == 0:
                # データがないときは404応答
                db.rollback()
                return jsonify({"result": "404", "errorStatement": app_name + exec_stat, "errorDetail" : "更新するデータがありません"}), 404

            # workspace履歴追加
            exec_stat = "登録実行(履歴)"
            da_workspace.insert_history(cursor, workspace_id)

            # workspace情報の再取得
            exec_stat = "登録データ確認"
            fetch_rows = da_workspace.select_workspace_id(cursor, workspace_id)

        # Response用のjsonに変換
        response_rows = fetch_rows

        return jsonify({"result": "200", "rows": response_rows })

    except Exception as e:
        return common.serverError(e, app_name + exec_stat, exec_detail)

def patch_workspace(workspace_id):
    """ワークスペース更新パッチ patch update workspace

    Args:
        workspace_id (int): ワークスペースID

    Returns:
        response: HTTP Respose
    """
    globals.logger.debug("CALL patch_workspace:{}".format(workspace_id))
    app_name = "ワークスペース更新パッチ:"
    exec_stat = "更新"
    exec_detail = ""

# 更新対象のカラム（specification以外）
# {
#   "parameter-info": {},
#   "workspace_id": 1,
#   "create_at": "Thu, 25 Nov 2021 04:22:31 GMT",
#   "update_at": "Thu, 25 Nov 2021 04:22:31 GMT",
#   "role_update_at": "Thu, 25 Nov 2021 04:22:31 GMT"
# }

    try:
        # 更新対象の項目をセット
        request_json = request.json.copy()

        exec_stat = "DB接続"
        with dbconnector() as db, dbcursor(db) as cursor:
            # workspace情報 update実行
            exec_stat = "更新実行"
            upd_cnt = da_workspace.patch_workspace(cursor, workspace_id, request_json)

            globals.logger.debug('workspace update complete update_count:{}'.format(upd_cnt))

            if upd_cnt == 0:
                # データがないときは404応答
                db.rollback()
                return jsonify({"result": "404", "errorStatement": app_name + exec_stat, "errorDetail" : "更新するデータがありません"}), 404

            # workspace履歴追加
            exec_stat = "登録実行(履歴)"
            da_workspace.insert_history(cursor, workspace_id)
            globals.logger.debug('workspace history add complete')

            # workspace情報の再取得
            exec_stat = "登録データ確認"
            fetch_rows = da_workspace.select_workspace_id(cursor, workspace_id)
            globals.logger.debug('workspace get complete')

        # Response用のjsonに変換
        response_rows = fetch_rows

        return jsonify({"result": "200", "rows": response_rows }), 200

    except Exception as e:
        return common.serverError(e, app_name + exec_stat, exec_detail)

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

def convert_workspace_specification(json):
    """workspace.specification変換
        requestのjsonからworkspaceテーブルのspecification登録用のjsonに変換する

    Args:
        json (dict): HTTP Request

    Returns:
        dict: workspaceテーブルのspecification登録用
    """
    # 不要な項目を削除する
    result = json.copy()
    common.deleteDictKey(result, 'workspace_id')
    common.deleteDictKey(result, 'organization_id')
    common.deleteDictKey(result, 'create_at')
    common.deleteDictKey(result, 'update_at')
    common.deleteDictKey(result, 'role_update_at')
    
    return result

@app.route('/workspace/<int:workspace_id>/manifests', methods=['POST'])
def manifest_file_registration(workspace_id):
    """マニフェストテンプレートファイル登録

    Args:
        workspace_id (int): ワークスペースID

    Returns:
        response: HTTP Respose
    """
    globals.logger.debug("CALL manifest_file_registration:{}".format(workspace_id))

    try:
        # 登録内容は基本的に、引数のJsonの値を使用する(追加項目があればここで記載)
        specification = request.json
        response_rows = [] 
        with dbconnector() as db, dbcursor(db) as cursor:
            
            for spec in specification['manifests']:

                # manifest情報 insert実行
                manifest_id = da_manifest.insert_manifest(cursor, workspace_id, spec)

                globals.logger.debug('insert manifest_id:{}'.format(str(manifest_id)))

                # manifest情報の再取得
                fetch_rows = da_manifest.select_manifest_id(cursor, workspace_id, manifest_id)
                # 戻り値に内容を追加
                response_rows.append(fetch_rows[0])

        return jsonify({"result": "200", "rows": response_rows })

    except Exception as e:
        return common.serverError(e)

@app.route('/workspace/<int:workspace_id>/manifests/<int:file_id>', methods=['PUT'])
def manifest_file_update(workspace_id, file_id):
    """マニフェストテンプレートファイル更新

    Args:
        workspace_id (int): ワークスペースID
        file_id (int): ファイルID

    Returns:
        response: HTTP Respose
    """
    globals.logger.debug("CALL manifest_file_update:{}".format(file_id))

    try:
        # 登録内容は基本的に、引数のJsonの値を使用する(追加項目があればここで記載)
        specification = request.json

        with dbconnector() as db, dbcursor(db) as cursor:
            # workspace情報 update実行
            upd_cnt = da_manifest.update_manifest(cursor, workspace_id, specification, file_id)

            if upd_cnt == 0:
                # データがないときは404応答
                db.rollback()
                return jsonify({"result": "404" }), 404

            # manifest情報の再取得
            fetch_rows = da_manifest.select_manifest_id(cursor, workspace_id, file_id)

        # Response用のjsonに変換
        response_rows = fetch_rows

        return jsonify({"result": "200", "rows": response_rows })

    except Exception as e:
        return common.serverError(e)

@app.route('/workspace/<int:workspace_id>/manifests', methods=['DELETE'])
def manifest_file_delete_all(workspace_id):
    """マニフェストテンプレートファイル削除

    Args:
        workspace_id (int): ワークスペースID

    Returns:
        response: HTTP Respose
    """
    globals.logger.debug("CALL manifest_file_delete_all:workspace_id:{}".format(workspace_id))

    try:
        with dbconnector() as db, dbcursor(db) as cursor:
            # manifests情報 delete実行
            upd_cnt = da_manifest.delete_manifests(cursor, workspace_id)
    
            globals.logger.debug("delete_manifests:ret:{}".format(upd_cnt))

            if upd_cnt == 0:
                # データがないときは404応答
                db.rollback()
                return jsonify({"result": "404" }), 404

        return jsonify({"result": "200"})

    except Exception as e:
        return common.serverError(e)

@app.route('/workspace/<int:workspace_id>/manifests/<int:manifest_id>', methods=['DELETE'])
def manifest_file_delete(workspace_id, manifest_id):
    """マニフェストテンプレートファイル削除

    Args:
        workspace_id (int): ワークスペースID
        file_id (int): ファイルID

    Returns:
        response: HTTP Respose
    """
    globals.logger.debug("CALL manifest_file_delete:workspace_id:{}, manifest_id:{}".format(workspace_id, manifest_id))

    try:
        with dbconnector() as db, dbcursor(db) as cursor:
            # manifests情報 delete実行
            upd_cnt = da_manifest.delete_manifest(cursor, workspace_id, manifest_id)
    
            globals.logger.debug("delete_manifest:ret:{}".format(upd_cnt))

            if upd_cnt == 0:
                # データがないときは404応答
                db.rollback()
                return jsonify({"result": "404" }), 404

        return jsonify({"result": "200"})

    except Exception as e:
        return common.serverError(e)

@app.route('/workspace/<int:workspace_id>/manifests', methods=['GET'])
def manifest_file_get_list(workspace_id):
    """マニフェストテンプレートファイル取得(全件)

    Args:
        workspace_id (int): ワークスペースID

    Returns:
        response: HTTP Respose
    """
    globals.logger.debug("CALL manifest_file_get:{}".format(workspace_id))

    try:
        with dbconnector() as db, dbcursor(db) as cursor:

            # manifest情報の取得
            fetch_rows = da_manifest.select_manifest(cursor, workspace_id)

        # Response用のjsonに変換
        response_rows = fetch_rows

        return jsonify({"result": "200", "rows": response_rows })

    except Exception as e:
        return common.serverError(e)

@app.route('/workspace/<int:workspace_id>/manifests/<int:file_id>', methods=['GET'])
def manifest_file_get(workspace_id, file_id):
    """マニフェストテンプレートファイル取得

    Args:
        workspace_id (int): ワークスペースID
        file_id (int): ファイルID

    Returns:
        response: HTTP Respose
    """
    globals.logger.debug("CALL manifest_file_get: [ workspace_id: {}, manifest_id: {} ]".format(workspace_id, file_id))

    try:
        with dbconnector() as db, dbcursor(db) as cursor:

            # manifest情報の取得
            fetch_rows = da_manifest.select_manifest_id(cursor, workspace_id, file_id)

            if len(fetch_rows) == 0:
                # データがないときは404応答
                db.rollback()
                return jsonify({"result": "404" }), 404

        # Response用のjsonに変換
        response_rows = fetch_rows

        return jsonify({"result": "200", "rows": response_rows })

    except Exception as e:
        return common.serverError(e)

def convert_workspace_response(fetch_rows):
    """レスポンス用JSON変換
        workspace情報のselect(fetch)した結果をレスポンス用のjsonに変換する
    Args:
        fetch_rows (dict): workspaceテーブル取得結果

    Returns:
        dict: レスポンス用json
    """
    result = []
    for fetch_row in fetch_rows:
        result_row = json.loads(fetch_row['specification'])
        result_row['workspace_id'] = fetch_row['workspace_id']
        result_row['create_at'] = fetch_row['create_at']
        result_row['update_at'] = fetch_row['update_at']
        result_row['role_update_at'] = fetch_row['role_update_at']
        result.append(result_row)
    return result

@app.route('/workspace/<int:workspace_id>/manifestParameter', methods=['PUT'])
def update_manifestParameter(workspace_id):
    """ワークスペース変更

    Args:
        workspace_id (int): ワークスペースID

    Returns:
        response: HTTP Respose
    """
    globals.logger.debug("CALL update_manifestParameter:{}".format(workspace_id))

    try:
        # Requestからspecification項目を生成する
        specification = request.json

        with dbconnector() as db, dbcursor(db) as cursor:
            # workspace情報取得
            workspaceInfo = da_workspace.select_workspace_id(cursor, workspace_id)

            # workspace情報のmanifestParameter部を差し替え
            db_specification = json.loads(workspaceInfo[0]["specification"])

            # 登録する配列用のindex
            i = 0
            for db_env in db_specification["ci_config"]["environments"]:
                for in_env in specification["ci_config"]["environments"]:
                    if db_env["environment_id"] == in_env["environment_id"]:
                        db_specification["ci_config"]["environments"][i]["manifests"] = in_env["manifests"]
                        break
                i += 1

            # manifestパラメータの項目説明も更新に含める
            db_specification["parameter-info"] = specification["parameter-info"]

            # workspace情報 update実行
            upd_cnt = da_workspace.update_workspace(cursor, db_specification, workspace_id)

            if upd_cnt == 0:
                # データがないときは404応答
                db.rollback()
                return jsonify({"result": "404" }), 404

            # Response用のjsonに変換
            response_rows = workspaceInfo

        return jsonify({"result": "200", "rows": response_rows })

    except Exception as e:
        return common.serverError(e)


@app.route('/workspace/<int:workspace_id>/access', methods=['POST'])
def workspace_access_registration(workspace_id):
    """ワークスペースアクセス情報登録

    Args:
        workspace_id (int): ワークスペースID

    Returns:
        response: HTTP Respose
    """
    globals.logger.debug("CALL workspace_access_registration:{}".format(workspace_id))

    try:
        # 登録内容は基本的に、引数のJsonの値を使用する(追加項目があればここで記載)
        info = request.json
        with dbconnector() as db, dbcursor(db) as cursor:
            
            # ワークスペースアクセス情報 insert実行
            da_workspace_access.insert_workspace_access(cursor, workspace_id, info)

            globals.logger.debug('insert workspace_id:{}'.format(workspace_id))

        return jsonify({"result": "200"}), 200

    except Exception as e:
        return common.serverError(e)

@app.route('/workspace/<int:workspace_id>/access', methods=['PUT'])
def workspace_access_update(workspace_id):
    """ワークスペースアクセス情報更新

    Args:
        workspace_id (int): ワークスペースID

    Returns:
        response: HTTP Respose
    """
    globals.logger.debug("CALL workspace_access_update:{}".format(workspace_id))

    try:
        # 登録内容は基本的に、引数のJsonの値を使用する(追加項目があればここで記載)
        info = request.json
        with dbconnector() as db, dbcursor(db) as cursor:
            
            # ワークスペースアクセス情報 update実行
            upd_cnt = da_workspace_access.update_workspace_access(cursor, workspace_id, info)

            globals.logger.debug('update workspace_id:{}'.format(workspace_id))

            if upd_cnt == 0:
                # データがないときは404応答
                db.rollback()
                return jsonify({"result": "404" }), 404

        return jsonify({"result": "200"}), 200

    except Exception as e:
        return common.serverError(e)

@app.route('/workspace/<int:workspace_id>/access', methods=['GET'])
def workspace_access_get(workspace_id):
    """ワークスペースアクセス情報登録

    Args:
        workspace_id (int): ワークスペースID

    Returns:
        response: HTTP Respose
    """
    globals.logger.debug("CALL workspace_access_get:{}".format(workspace_id))

    try:
        # 登録内容は基本的に、引数のJsonの値を使用する(追加項目があればここで記載)
        with dbconnector() as db, dbcursor(db) as cursor:
            
            # ワークスペースアクセス情報 insert実行
            fetch_rows = da_workspace_access.select_workspace_access(cursor, workspace_id)

            if len(fetch_rows) == 0:
                # データがないときは404応答
                db.rollback()
                return jsonify({"result": "404" }), 404

        # Response用のjsonに変換[変換が必要な場合は関数化する]
        response_row = json.loads(fetch_rows[0]["info"])

        return jsonify(response_row), 200

    except Exception as e:
        return common.serverError(e)



@app.route('/workspace/<int:workspace_id>/access', methods=['DELETE'])
def workspace_access_delete(workspace_id, id):
    """ワークスペースアクセス情報削除

    Args:
        workspace_id (int): ワークスペースID
        id (int): ワークスペースアクセス情報ID

    Returns:
        response: HTTP Respose
    """
    globals.logger.debug("CALL workspace_access_delete:workspace_id:{}".format(workspace_id))

    try:
        with dbconnector() as db, dbcursor(db) as cursor:
            # ワークスペースアクセス情報 delete実行
            upd_cnt = da_workspace_access.delete_workspace_access(cursor, workspace_id)
    
            globals.logger.debug("workspace_access:ret:{}".format(upd_cnt))

            if upd_cnt == 0:
                # データがないときは404応答
                db.rollback()
                return jsonify({"result": "404" }), 404

        return jsonify({"result": "200"}), 200

    except Exception as e:
        return common.serverError(e)


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('API_WORKSPACE_PORT', '8000')), threaded=True)

