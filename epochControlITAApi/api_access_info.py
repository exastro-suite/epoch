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
from datetime import datetime
import inspect
import os
import json
import tempfile
import subprocess
import time
import re
from urllib.parse import urlparse
import base64
import requests
from requests.auth import HTTPBasicAuth
import traceback
from datetime import timedelta, timezone

import globals
import common

# 設定ファイル読み込み・globals初期化 flask setting file read and globals initialize
app = Flask(__name__)
app.config.from_envvar('CONFIG_API_ITA_PATH')
globals.init(app)

def get_access_info(workspace_id):
    """ワークスペースアクセス情報取得

    Args:
        workspace_id (int): ワークスペースID

    Returns:
        json: アクセス情報
    """
    try:
        globals.logger.info('Get workspace access information. workspace_id={}'.format(workspace_id))

        # url設定
        api_info = "{}://{}:{}".format(os.environ['EPOCH_RS_WORKSPACE_PROTOCOL'], os.environ['EPOCH_RS_WORKSPACE_HOST'], os.environ['EPOCH_RS_WORKSPACE_PORT'])

        # アクセス情報取得
        # Select送信（workspace_access取得）
        globals.logger.info('Send a request. workspace_id={}, URL={}/workspace/{}/access'.format(workspace_id, api_info, workspace_id))
        request_response = requests.get( "{}/workspace/{}/access".format(api_info, workspace_id))

        # 情報が存在する場合は、更新、存在しない場合は、登録
        if request_response.status_code == 200:
            ret = json.loads(request_response.text)
        else:
            raise Exception("workspace_access get error status:{}, responce:{}".format(request_response.status_code, request_response.text))

        return ret

    except Exception as e:
        globals.logger.debug ("get_access_info Exception:{}".format(e.args))
        raise # 再スロー
