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

def insert_logs(cursor, workspace_id, username, log_kind, contents):
    """logs insert

    Args:
        cursor (mysql.connector.cursor): カーソル cursor
        workspace_id (int): workspace id
        username (str): username
        log_kind (str): log kind

    Returns:
        int: log_id
        
    """
    # insert実行
    cursor.execute('''
                INSERT INTO logs
                    (
                        workspace_id,
                        log_kind,
                        contents,
                        username
                    )
                    values
                    (
                        %(workspace_id)s,
                        %(log_kind)s,
                        %(contents)s,
                        %(username)s
                    )''',
                {
                    'workspace_id' :                workspace_id,
                    'log_kind' :                    log_kind,
                    'contents' :                    json.dumps(contents),
                    'username' :                    username,
                })

    # 追加したtask_idをreturn
    return cursor.lastrowid
