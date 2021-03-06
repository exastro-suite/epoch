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

import encrypt_workspace

def insert_workspace_access(cursor, workspace_id, info):
    """ワークスペースアクセス情報登録

    Args:
        cursor (mysql.connector.cursor): カーソル
        workspace_id (int): ワークスペースID
        info (Dict)): アクセス情報のJson形式

    Returns:
        int: ワークスペースアクセス情報id
        
    """
    # encrypt
    enc = encrypt_workspace.encrypt_workspace_access()
    enc_info = enc.encrypt(info)

    # ワークスペースアクセス情報 insert実行
    cursor.execute('INSERT INTO workspace_access ( workspace_id, info )' \
                    ' VALUES ( %(workspace_id)s, %(info)s )',
        {
            'workspace_id' : workspace_id,
            'info' : json.dumps(enc_info),
        }
    )
    # 追加したワークスペースIDをreturn
    return cursor.lastrowid

def update_workspace_access(cursor, workspace_id, info):
    """ワークスペースアクセス情報更新

    Args:
        cursor (mysql.connector.cursor): カーソル
        workspace_id (int): ワークスペースID
        info (Dict)): ワークスペースアクセス情報のJson形式

    Returns:
        int: アップデート件数
        
    """
    # encrypt
    enc = encrypt_workspace.encrypt_workspace_access()
    enc_info = enc.encrypt(info)

    # ワークスペースアクセス情報 update実行
    upd_cnt = cursor.execute('UPDATE workspace_access' \
                    ' SET info = %(info)s' \
                    ' WHERE workspace_id = %(workspace_id)s',
        {
            'workspace_id' : workspace_id,
            'info': json.dumps(enc_info),
        }
    )
    upd_cnt = 1
    # 更新した件数をreturn
    return upd_cnt

def delete_workspace_access(cursor, workspace_id):
    """ワークスペースアクセス情報削除

    Args:
        cursor (mysql.connector.cursor): カーソル
        workspace_id (Int)): ワークスペースID

    Returns:
        int: 削除件数
        
    """
    # ワークスペースアクセス情報 delete実行
    cursor.execute('DELETE FROM workspace_access' \
                    ' WHERE workspace_id = %(workspace_id)s',
        {
            'workspace_id' : workspace_id,
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
    cursor.execute('SELECT * FROM workspace_access WHERE workspace_id = %(workspace_id)s',
        {
            'workspace_id' : workspace_id,
        }
    )
    rows = cursor.fetchall()

    enc = encrypt_workspace.encrypt_workspace_access()
    for row in rows:
        row['info'] = json.dumps(enc.decrypt(json.loads(row['info'])))
    return rows
