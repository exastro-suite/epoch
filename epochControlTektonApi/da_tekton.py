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

def insert_tekton_pipeline_yaml(cursor, info):
    """tekton_pipeline_yaml情報登録

    Args:
        cursor (mysql.connector.cursor): カーソル
        info (Dict)): tekton_pipeline_yaml情報のJson形式

    Returns:
        int: yaml_id
        
    """
    # insert実行
    cursor.execute('''
                INSERT INTO tekton_pipeline_yaml
                    (
                        workspace_id,
                        kind,
                        filename,
                        yamltext
                    )
                    values
                    (
                        %(workspace_id)s,
                        %(kind)s,
                        %(filename)s,
                        %(yamltext)s
                    )''',
                {
                    'workspace_id' :    info["workspace_id"],
                    'kind':             info["kind"],
                    'filename' :        info["template"],
                    'yamltext' :        info["yamltext"],
                })
    # 追加したワークスペースIDをreturn
    return cursor.lastrowid

def select_tekton_pipeline_yaml_id(cursor, workspace_id, kind):
    """organization情報取得(id指定)

    Args:
        cursor (mysql.connector.cursor): カーソル
        workspace_id (int): ワークスペースID
        kind (str)): 区分 "namespace"/"pipeline"

    Returns:
        dict: select結果
    """
    # select実行
    cursor.execute('''
            SELECT * FROM tekton_pipeline_yaml
                WHERE   workspace_id    =   %(workspace_id)s
                and     kind            =   %(kind)s
                order by    yaml_id desc''',
            {
                'workspace_id':     workspace_id,
                'kind':             kind,
            })
            
    rows = cursor.fetchall()
    return rows

def delete_tekton_pipeline_yaml(cursor, yaml_id):
    """tekton_pipeline_yaml情報削除(id指定)

    Args:
        cursor (mysql.connector.cursor): カーソル
        yaml_id (int): yaml ID

    Returns:
        int: 削除件数
    """
    # tekton_pipeline_yaml情報 delete実行
    cursor.execute('''
                DELETE FROM tekton_pipeline_yaml
                    WHERE   yaml_id    =   %(yaml_id)s''',
                {
                    'yaml_id':     yaml_id,
                })

    # 削除した件数をreturn
    return cursor.rowcount
