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

import os
import json
import datetime

import globals
from dbconnector import dbcursor

def insert_workspace(cursor, specification):
    """workspace情報登録

    Args:
        cursor (mysql.connector.cursor): カーソル
        specification (Dict)): ワークスペース情報のJson形式

    Returns:
        int: ワークスペースID
        
    """
    # insert実行
    cursor.execute('INSERT INTO workspace ( organization_id, specification ) VALUES ( 1, %(specification)s )',
        {
            'specification' : json.dumps(specification)
        }
    )
    # 追加したワークスペースIDをreturn
    return cursor.lastrowid

def update_workspace(cursor, specification, workspace_id, update_at):
    """workspace情報更新

    Args:
        cursor (mysql.connector.cursor): カーソル
        specification (Dict)): ワークスペース情報のJson形式

    Returns:
        int: アップデート件数
        
    """

    sql = "UPDATE workspace" \
            " SET specification = %(specification)s"\
            " WHERE workspace_id = %(workspace_id)s"\
            " AND update_at = %(update_at)s"

    # workspace情報 update実行
    upd_cnt = cursor.execute(sql,
        {
            'workspace_id' : workspace_id,
            'specification': json.dumps(specification),
            'update_at' : update_at
        }
    )
    # 更新した件数をreturn
    return upd_cnt

def patch_workspace(cursor, workspace_id, update_items):
    """workspace情報更新パッチ

    Args:
        cursor (mysql.connector.cursor): カーソル
        workspace_id (str): workspace_id
        update_items (dict)): update items

    Returns:
        int: アップデート件数
        
    """
    set_update = []
    data = []
    for item in update_items:
        key = str(item)
        # keyの種類によって、システム日付を設定する Set the system date according to the key type
        if item == "role_update_at":
            value = datetime.datetime.now()
        else:
            value = item.values()

        set_update.append(f" AND {key} = %s")

        # JSON整形 JSON formatting
        data.append(value)

    # 設定値のはじめをSETに置き換え Replaced the beginning of the set value with SET
    if len(set_update) > 0:
        set_update[0] = " SET" + set_update[0][4:]

    # 更新キー The update key
    set_update.append(" WHERE workspace_id = %s")
    data.append(workspace_id)

    # UPDATE文の生成 Generation of UPDATE statement
    str_sql = "UPDATE workspace" + "".join(set_update)
    globals.logger.debug('sql:{}'.format(str_sql))
    globals.logger.debug('data:{}'.format(data))
    
    # workspace update
    upd_cnt = cursor.execute(str_sql, data)
    
    # 更新した件数をreturn Return the number of updates
    return upd_cnt
    

def select_workspace_id(cursor, workspace_id):
    """workspace情報取得(id指定)

    Args:
        cursor (mysql.connector.cursor): カーソル
        workspace_id (int): ワークスペースID

    Returns:
        dict: select結果
    """
    # select実行
    cursor.execute('SELECT * FROM workspace WHERE workspace_id = %(workspace_id)s ORDER BY workspace_id',
        {
            'workspace_id' : workspace_id
        }
    )
    rows = cursor.fetchall()
    return rows

def select_workspace(cursor):
    """workspace情報取得(全取得)

    Args:
        cursor (mysql.connector.cursor): カーソル

    Returns:
        dict: select結果
    """
    # select実行
    cursor.execute('SELECT * FROM workspace ORDER BY workspace_id')
    rows = cursor.fetchall()
    return rows

def insert_history(cursor, workspace_id):
    """workspace履歴情報追加

    Args:
        cursor (mysql.connector.cursor): カーソル
        workspace_id (int): ワークスペースID
    """
    cursor.execute(
        '''INSERT INTO workspace_history (workspace_id, organization_id, update_at, role_update_at, specification)
            SELECT workspace_id, organization_id, update_at, role_update_at, specification FROM workspace WHERE workspace_id = %(workspace_id)s''',
        {
            'workspace_id' : workspace_id
        }
    )

