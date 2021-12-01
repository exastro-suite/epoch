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

from flask import Flask, request, abort, jsonify, render_template
import inspect
import os
import json
from requests.auth import HTTPBasicAuth
import traceback
from kubernetes import client, config

import globals
import common

# 設定ファイル読み込み・globals初期化
app = Flask(__name__)
app.config.from_envvar('CONFIG_API_WORKSPACE_PATH')
globals.init(app)

def get_namespace(name):
    """namespace情報取得

    Args:
        name (str)): namespace名

    Returns:
        [json]: namespace情報
    """
    try:

        config.load_incluster_config()
        # 使用するAPIの宣言
        v1 = client.CoreV1Api()
        
        # 引数の設定
        pretty = '' # str | If 'true', then the output is pretty printed. (optional)
        exact = True # bool | Should the export be exact.  Exact export maintains cluster-specific fields like 'Namespace'. Deprecated. Planned for removal in 1.18. (optional)
        export = True # bool | Should this value be exported.  Export strips fields that a user can not specify. Deprecated. Planned for removal in 1.18. (optional)

        # namespaceの情報取得
        ret = v1.read_namespace(name=name)
        # globals.logger.debug("read_namespace: {}".format(ret))

        return ret 

    except client.exceptions.ApiException as e:
        globals.logger.error('e:{}'.format(str(e.reason)))
        if e.reason == "Not Found":
            return None
        else:
            globals.logger.error(''.join(list(traceback.TracebackException.from_exception(e).format())))
            raise
    except Exception as e:
        globals.logger.error(''.join(list(traceback.TracebackException.from_exception(e).format())))
        raise

def create_namespace(name):
    """namespace作成

    Args:
        name (str): namespace名

    Returns:
        [json]: namespace情報
    """
    try:

        config.load_incluster_config()
        # 使用するAPIの宣言
        v1 = client.CoreV1Api()
        
        # 引数の設定
        body = client.V1Namespace(metadata=client.V1ObjectMeta(name=name))
        # api_instance = kubernetes.client.CoreV1Api(api_client)
        # body = kubernetes.client.V1Namespace() # V1Namespace | 
        #pretty = '' # str | If 'true', then the output is pretty printed. (optional)
        #dry_run = '' # str | When present, indicates that modifications should not be persisted. An invalid or unrecognized dryRun directive will result in an error response and no further processing of the request. Valid values are: - All: all dry run stages will be processed (optional)
        #field_manager = '' # str | fieldManager is a name associated with the actor or entity that is making these changes. The value must be less than or 128 characters long, and only contain printable characters, as defined by https://golang.org/pkg/unicode/#IsPrint. (optional)

        # namespaceの作成
        #ret = v1.create_namespace(body=body, pretty=pretty, dry_run=dry_run, field_manager=field_manager)
        ret = v1.create_namespace(body=body)

        # globals.logger.debug("create_namespace: {}".format(ret))

        return ret 

    except Exception as e:
        globals.logger.error(''.join(list(traceback.TracebackException.from_exception(e).format())))
        raise
