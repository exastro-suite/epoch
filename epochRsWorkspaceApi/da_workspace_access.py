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

import globals
from dbconnector import dbcursor

def insert_workspace_access(cursor, workspace_id, info):
    """ワークスペースアクセス情報登録

    Args:
        cursor (mysql.connector.cursor): カーソル
        workspace_id (int): ワークスペースID
        info (Dict)): アクセス情報のJson形式

    Returns:
        int: ワークスペースアクセス情報id
        
    """
    # ワークスペースアクセス情報 insert実行
    cursor.execute('INSERT INTO workspace_access ( workspace_id, info )' \
                    ' VALUES ( %(workspace_id)s, %(info)s )',
        {
            'workspace_id' : workspace_id,
            'info' : json.dumps(info),
        }
    )
    # 追加したワークスペースIDをreturn
    return cursor.lastrowid

def update_workspace_access(cursor, workspace_id, spec, id):
    """ワークスペースアクセス情報更新

    Args:
        cursor (mysql.connector.cursor): カーソル
        workspace_id (int): ワークスペースID
        info (Dict)): ワークスペースアクセス情報のJson形式
        id (int): ワークスペースアクセス情報ID

    Returns:
        int: アップデート件数
        
    """
    # ワークスペースアクセス情報 update実行
    cursor.execute('UPDATE workspace_access' \
                    ' SET info = %(info)s' \
                    ' WHERE workspace_id = %(workspace_id)s' \
                    ' AND id = %(id)s',
        {
            'workspace_id' : workspace_id,
            'id' : id,
            'info': json.dumps(info),
        }
    )
    # 更新した件数をreturn
    return cursor.rowcount

def delete_workspace_access(cursor, workspace_id, id):
    """ワークスペースアクセス情報削除

    Args:
        cursor (mysql.connector.cursor): カーソル
        workspace_id (Int)): ワークスペースID
        id (Int)): ワークスペースアクセス情報ID

    Returns:
        int: 削除件数
        
    """
    # ワークスペースアクセス情報 delete実行
    cursor.execute('DELETE FROM workspace_access' \
                    ' WHERE workspace_id = %(workspace_id)s'\
                        ' AND id = %(id)s',
        {
            'workspace_id' : workspace_id,
            'id' : id
        }
    )
    # 削除した件数をreturn
    return cursor.rowcount

def select_workspace_access(cursor, workspace_id):
    """ワークスペースアクセス情報取得

    Args:
        cursor (mysql.connector.cursor): カーソル
        workspace_id (int): ワークスペースID

    Returns:
        dict: select結果
    """
    # select実行
    cursor.execute('SELECT * FROM workspace_access WHERE workspace_id = %(workspace_id)s ORDER BY id',
        {
            'workspace_id' : workspace_id,
        }
    )
    rows = cursor.fetchall()
    return rows

def select_workspace_access_id(cursor, workspace_id, id):
    """ワークスペースアクセス情報取得(id指定)

    Args:
        cursor (mysql.connector.cursor): カーソル
        workspace_id (int): ワークスペースID
        id (int): ワークスペースアクセス情報ID

    Returns:
        dict: select結果
    """
    # select実行
    cursor.execute('SELECT * FROM workspace_access WHERE workspace_id = %(workspace_id)s and id = %(id)s ORDER BY id',
        {
            'workspace_id' : workspace_id,
            'id' : id
        }
    )
    rows = cursor.fetchall()
    return rows
