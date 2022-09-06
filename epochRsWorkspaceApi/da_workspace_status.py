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

import os
import json

import globals
from dbconnector import dbcursor

def insert_workspace_status(cursor, workspace_id, info):
    """ワークスペース状態情報登録 Workspace status information registration

    Args:
        cursor (mysql.connector.cursor): カーソル cursor
        workspace_id (int): ワークスペースID workspace id
        info (Dict)): 状態のJson形式 status json

    Returns:
        int: workspace id

    """
    # ワークスペース状態情報 insert実行 Workspace status information insert execution
    cursor.execute('INSERT INTO workspace_status ( workspace_id, info )' \
                    ' VALUES ( %(workspace_id)s, %(info)s )',
        {
            'workspace_id' : workspace_id,
            'info' : json.dumps(info),
        }
    )
    # workspace id return
    return cursor.lastrowid

def update_workspace_status(cursor, workspace_id, info_upadate_colums):
    """ワークスペース状態情報更新 Workspace status information update

    Args:
        cursor (mysql.connector.cursor): カーソル cursor
        workspace_id (int): ワークスペースID workspace id
        info_upadate_colums (Dict)): 更新対象となる項目のjson値 Json value of the item to be updated

    Returns:
        int: アップデート件数 update count

    """
    upd_item = ""
    upd_json = {
            'workspace_id' : workspace_id,
    }
    # 更新対象となる項目数分、更新sqlを組み立て
    # Assemble update sql for the number of items to be updated
    for key, val in info_upadate_colums.items():
        upd_item = upd_item + ', "$.{}", %({})s'.format(key, key)
        upd_json[key] = val

    # 更新SQL　update SQL
    sql = 'UPDATE workspace_status' \
            ' SET info = json_replace(info, ' + upd_item[2:] + ')' \
            ' WHERE workspace_id = %(workspace_id)s'
            # ' SET info = %(info)s' \

    # cursor.affected_rows()
    # ワークスペース状態情報 update実行 update excute
    upd_cnt = cursor.execute(sql, upd_json)
    upd_cnt = 1

    # 更新した件数をreturn Return the count of updates
    return upd_cnt

def delete_workspace_status(cursor, workspace_id):
    """ワークスペース状態情報削除 Delete workspace status information

    Args:
        cursor (mysql.connector.cursor): カーソル cursor
        workspace_id (int): ワークスペースID workspace id

    Returns:
        int: 削除件数 delete count

    """
    # ワークスペース状態情報 delete実行 Workspace status information delete execution
    cursor.execute('DELETE FROM workspace_status' \
                    ' WHERE workspace_id = %(workspace_id)s',
        {
            'workspace_id' : workspace_id,
        }
    )
    # 削除した件数をreturn delete count to return
    return cursor.rowcount

def select_workspace_status(cursor, workspace_id):
    """ワークスペース状態情報取得 Get workspace status information

    Args:
        cursor (mysql.connector.cursor): カーソル cursor
        workspace_id (int): ワークスペースID workspace id

    Returns:
        dict: select結果 select results
    """
    # select実行 select execute
    cursor.execute('SELECT * FROM workspace_status WHERE workspace_id = %(workspace_id)s',
        {
            'workspace_id' : workspace_id,
        }
    )
    rows = cursor.fetchall()
    return rows
