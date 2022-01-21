#   Copyright 2021 NEC Corporation
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

def insert_tekton_pipeline_task(cursor, info):
    """tekton_pipeline_task情報登録

    Args:
        cursor (mysql.connector.cursor): カーソル
        info (Dict)): tekton_pipeline_task情報のJson形式

    Returns:
        int: task_id
        
    """
    # insert実行
    cursor.execute('''
                INSERT INTO tekton_pipeline_task
                    (
                        workspace_id,
                        pipeline_id,
                        pipeline_run_name,
                        pipeline_run_uid,
                        status,
                        git_repository_url,
                        git_branch,
                        git_sender_user,
                        container_registry_image,
                        container_registry_image_tag,
                        git_webhook_header,
                        git_webhook_body
                    )
                    values
                    (
                        %(workspace_id)s,
                        %(pipeline_id)s,
                        %(pipeline_run_name)s,
                        %(pipeline_run_uid)s,
                        %(status)s,
                        %(git_repository_url)s,
                        %(git_branch)s,
                        %(git_sender_user)s,
                        %(container_registry_image)s,
                        %(container_registry_image_tag)s,
                        %(git_webhook_header)s,
                        %(git_webhook_body)s
                    )''',
                {
                    'workspace_id' :                info['workspace_id'],
                    'pipeline_id' :                 info['pipeline_id'],
                    'pipeline_run_name' :           info['pipeline_run_name'],
                    'pipeline_run_uid' :            info['pipeline_run_uid'],
                    'status' :                      info['status'],
                    'git_repository_url' :          info['git_repository_url'],
                    'git_branch' :                  info['git_branch'],
                    'git_sender_user' :             info['git_sender_user'],
                    'container_registry_image' :    info['container_registry_image'],
                    'container_registry_image_tag' :info['container_registry_image_tag'],
                    'git_webhook_header' :          info['git_webhook_header'],
                    'git_webhook_body' :            info['git_webhook_body'],
                })

    # 追加したtask_idをreturn
    return cursor.lastrowid

def update_tekton_pipeline_task(cursor, info, task_id):
    """tekton_pipeline_task情報更新

    Args:
        cursor (mysql.connector.cursor): カーソル
        info (Dict)):   ワークスペース情報のJson形式
        task_id (int):  task_id

    Returns:
        int: アップデート件数
        
    """
    # SQL生成
    sqlstmt = ( 'UPDATE tekton_pipeline_task SET '
                + ','.join(map(lambda x: '{} = %({})s'.format(x,x), info.keys()))
                + ' WHERE task_id = %(task_id)s' )

    # 更新パラメータ
    update_param = info.copy()
    update_param['task_id'] = task_id

    # workspace情報 update実行
    upd_cnt = cursor.execute( sqlstmt, update_param )

    # 更新した件数をreturn
    return upd_cnt
