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

def insert_manifest(cursor, workspace_id, spec):
    """manifest情報登録

    Args:
        cursor (mysql.connector.cursor): カーソル
        workspace_id (int): ワークスペースID
        spec (Dict)): manifest情報のJson形式

    Returns:
        int: manifest_id
        
    """
    # insert実行
    cursor.execute('INSERT INTO manifest ( workspace_id, file_name, file_text  )' \
                   ' VALUES ( %(workspace_id)s, %(file_name)s, %(file_text)s )',
        {
            'workspace_id' : workspace_id,
            'file_name' : spec['file_name'],
            'file_text' : spec['file_text']
        }
    )
    # 追加したワークスペースIDをreturn
    return cursor.lastrowid

def update_manifest(cursor, workspace_id, spec):
    """manifest情報更新

    Args:
        cursor (mysql.connector.cursor): カーソル
        spec (Dict)): manifest情報のJson形式

    Returns:
        int: アップデート件数
        
    """
    # manifest情報 update実行
    upd_cnt = cursor.execute('UPDATE manifest' \
                             ' SET file_name = %(file_name)s' \
                               ' , file_text = %(file_text)s' \
                               ' WHERE workspace_id = %(workspace_id)s',
                                 ' AND id = %(manifest_id)s',
        {
            'workspace_id' : workspace_id,
            'manifest_id' : spec['manifest_id'],
            'file_name': spec['file_name'],
            'file_text': spec['file_text']
        }
    )
    # 更新した件数をreturn
    return upd_cnt

def select_manifest_id(cursor, workspace_id, manifest_id):
    """manifest情報取得(id指定)

    Args:
        cursor (mysql.connector.cursor): カーソル
        workspace_id (int): ワークスペースID
        manifest_id (int): manifest ID

    Returns:
        dict: select結果
    """
    # select実行
    cursor.execute('SELECT * FROM manifest WHERE workspace_id = %(workspace_id)s and id = %(manifest_id)s ORDER BY id',
        {
            'workspace_id' : workspace_id,
            'manifest_id' : manifest_id
        }
    )
    rows = cursor.fetchall()
    return rows

def select_manifest(cursor, workspace_id):
    """manifest情報取得(全取得)

    Args:
        cursor (mysql.connector.cursor): カーソル
        workspace_id (int): ワークスペースID

    Returns:
        dict: select結果
    """
    # select実行
    cursor.execute('SELECT * FROM workspace WHERE workspace_id = %(workspace_id)s and manifest_id ORDER BY workspace_id',
        {
            'workspace_id' : workspace_id
        }
    )

    rows = cursor.fetchall()
    return rows
