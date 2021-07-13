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

def insert_organization(cursor, info):
    """organization情報登録

    Args:
        cursor (mysql.connector.cursor): カーソル
        info (Dict)): organization情報のJson形式

    Returns:
        int: organization_id
        
    """
    # insert実行
    cursor.execute('INSERT INTO organization ( organization_name, additional_information )' \
                   ' VALUES ( %(organization_name)s, %(additional_information)s )',
        {
            'organization_name' : info['organization_name'],
            'additional_information' : json.dumps(info['additional_information'])
        }
    )
    # 追加したワークスペースIDをreturn
    return cursor.lastrowid

def insert_history(cursor, organization_id):
    """organization履歴情報追加

    Args:
        cursor (mysql.connector.cursor): カーソル
        organization_id (int): Organization ID
    """
    cursor.execute(
        '''INSERT INTO organization_history ( organization_id, organization_name, additional_information, update_at )
            SELECT organization_id, organization_name, additional_information, update_at FROM organization WHERE organization_id = %(organization_id)s''',
        {
            'organization_id' : organization_id
        }
    )

def select_organization_id(cursor, organization_id):
    """organization情報取得(id指定)

    Args:
        cursor (mysql.connector.cursor): カーソル
        organization_id (int): ワークスペースID

    Returns:
        dict: select結果
    """
    # select実行
    cursor.execute('SELECT * FROM organization WHERE organization_id = %(organization_id)s ORDER BY organization_id',
        {
            'organization_id' : organization_id
        }
    )
    rows = cursor.fetchall()
    return rows

def select_organization(cursor):
    """organization情報取得(全取得)

    Args:
        cursor (mysql.connector.cursor): カーソル

    Returns:
        dict: select結果
    """
    # select実行
    cursor.execute('SELECT * FROM workspace ORDER BY workspace_id')
    rows = cursor.fetchall()
    return rows
