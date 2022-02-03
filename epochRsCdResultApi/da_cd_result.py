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

def insert_cd_result(cursor, workspace_id, cd_result_id, username, contents):
    """cd_result insert

    Args:
        cursor (mysql.connector.cursor): カーソル cursor
        workspace_id (int): workspace id
        cd_result_id (int): cd-result id
        username (str): username
        contents (dict): contents (include "cd_staus")

    Returns:
        int: lastrowid
        
    """
    # insert実行 insert excute
    cursor.execute('''
                INSERT INTO cd_result
                    (
                        workspace_id,
                        cd_result_id,
                        cd_status,
                        contents,
                        username
                    )
                    values
                    (
                        %(workspace_id)s,
                        %(cd_result_id)s,
                        %(cd_status)s,
                        %(contents)s,
                        %(username)s
                    )''',
                {
                    'workspace_id' :                workspace_id,
                    'cd_result_id' :                cd_result_id,
                    'cd_status' :                   contents["cd_status"],
                    'contents' :                    json.dumps(contents),
                    'username' :                    username,
                })

    # 追加したcd_result_idをreturn 
    # Return the added cd_result_id
    return cursor.lastrowid

def update_cd_result(cursor, workspace_id, cd_result_id, update_contents_items):
    """cd_result update

    Args:
        cursor (mysql.connector.cursor): カーソル cursor
        workspace_id (int): workspace id
        cd_result_id (int): cd-result id
        update_contents_items (dict)): update contents items (include "cd_staus")

    Returns:
        int: アップデート件数 update count
        
    """
    upd_item = ""
    upd_json = {
            'workspace_id' : workspace_id,
            'cd_result_id' : cd_result_id,
            'cd_status' : update_contents_items["cd_status"],
    }
    # 更新対象となる項目数分、更新sqlを組み立て
    # Assemble update sql for the number of items to be updated
    for key, val in update_contents_items.items():
        upd_item = upd_item + ', "$.{}", %(co_{})s'.format(key, key)
        upd_json["co_" + key] = val

    # 更新SQL　update SQL
    sql = 'UPDATE cd_result' \
            ' SET cd_status = %(cd_status)s' \
            ' , contents = json_replace(contents, ' + upd_item[2:] + ')' \
            ' WHERE workspace_id = %(workspace_id)s' \
            ' AND cd_result_id = %(cd_result_id)s'
    globals.logger.debug('SQL {}'.format(sql))

    # cursor.affected_rows()
    # CD結果情報 update実行 cd result update excute
    upd_cnt = cursor.execute(sql, upd_json)
    upd_cnt = 1

    # 更新した件数をreturn Return the count of updates
    return upd_cnt

def delete_cd_result(cursor, workspace_id, cd_result_id):
    """cd_result delete

    Args:
        cursor (mysql.connector.cursor): カーソル cursor
        workspace_id (int): workspace id
        cd_result_id (int): cd-result id

    Returns:
        int: 削除件数 delete count
        
    """
    # CD結果情報 delete実行 cd result delete execution
    cursor.execute('DELETE FROM cd_result' \
                    ' WHERE workspace_id = %(workspace_id)s' \
                    ' AND cd_result_id = %(cd_result_id)s',
        {
            'workspace_id' : workspace_id,
            'cd_result_id' : cd_result_id,
        }
    )
    # 削除した件数をreturn 
    # delete count to return
    return cursor.rowcount

def select_cd_result(cursor, workspace_id=None, cd_result_id=None, cd_status_in=[], username=None, latest=False):
    """CD結果情報取得 Get cd_result

    Args:
        cursor (mysql.connector.cursor): カーソル cursor
        workspace_id (int): workspace id (Required fields)
        cd_result_id (int): cd-result id 
        cd_status_in (array str): cd_status in conditions
        username (str): username
        latest (bool): latest True or False

    Returns:
        dict: select結果 select results
    """

    sql_limit = ""
    cond_where = ""
    cond_json = {}

    # 条件がある場合に設定
    # Set when there are conditions
    if workspace_id is not None:
        cond_where += " AND workspace_id = %(workspace_id)s"
        cond_json["workspace_id"] = workspace_id

    if cd_result_id is not None:
        cond_where += " AND cd_result_id = %(cd_result_id)s"
        cond_json["cd_result_id"] = cd_result_id

    if len(cd_status_in) > 0:
        cond_str = ""
        for (idx, val) in enumerate(cd_status_in):
            cond_str += f", %(cd_status_in_{idx})s"
            cond_json[f"cd_status_in_{idx}"] = val
        cond_where += " AND cd_status in ({})".format(cond_str[2:])

    if username is not None:
        cond_where += " AND username = %(username)s"
        cond_json["username"] = username

    # 最新のみの場合
    if latest:
        sql_limit = " LIMIT 1"

    # 常に取得は降順
    sql_order = " ORDER BY update_at DESC"

    # sql
    sql = "SELECT * FROM cd_result" \
            " WHERE " + cond_where[4:] + \
            sql_order + \
            sql_limit

    globals.logger.debug(f'sql:{sql}')
    # select実行 select execute
    cursor.execute(sql, cond_json)
    rows = cursor.fetchall()
    return rows
