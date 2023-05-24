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

from lib2to3.pgen2 import token
from flask import Flask, request, abort, jsonify, render_template
from datetime import datetime
import inspect
import os
import json
import re
import urllib.parse
import base64
import requests
from requests.auth import HTTPBasicAuth
import traceback
from datetime import timedelta, timezone

import globals
import common

# 設定ファイル読み込み・globals初期化
app = Flask(__name__)
app.config.from_envvar('CONFIG_API_DOCKERHUB_PATH')
globals.init(app)

dockerhub_conf = {
    "api_base_url": "https://registry.hub.docker.com/v2",
    "api_path": {
        "get_token": "/users/login",
        "get_tags": "/repositories/{}/tags",
    },
    "link_url": "https://hub.docker.com/r/{}",
}
acr_conf = {
    "api_base_url": "https://{}",
    "api_path": {
        "get_tags": "{}/acr/v1/{}/_tags",
    },
}

@app.route('/alive', methods=["GET"])
def alive():
    """死活監視

    Returns:
        Response: HTTP Respose
    """
    return jsonify({"result": "200", "time": str(datetime.now(globals.TZ))}), 200


@app.route('/registry/<path:registry>', methods=["POST"])
def get_repositories(registry):
    app_name = "ワークスペース情報:"
    exec_stat = "container images取得"
    error_detail = ""
    try:
        globals.logger.debug('#' * 50)
        globals.logger.debug('CALL {} registry:{}'.format(inspect.currentframe().f_code.co_name, registry))
        globals.logger.debug('#' * 50)

        if request.headers["interface"] == "dockerhub":
            return get_repositories_dockerhub(registry)

        elif request.headers["interface"] == "ACR":
            return get_repositories_acr(registry)

        else:
            raise common.UserException("Unsupported interface")

    except Exception as e:
        return common.server_error_to_message(e, app_name + exec_stat, error_detail)


def get_repositories_dockerhub(registry):
    """get dockerhub image list

    Args:
        registry (string): image

    Returns:
        Response: HTTP Response
    """
    app_name = "ワークスペース情報:"
    exec_stat = "DockerHub container images取得"
    error_detail = ""

    try:
        globals.logger.debug('#' * 50)
        globals.logger.debug('CALL {} registry:{}'.format(inspect.currentframe().f_code.co_name, registry))
        globals.logger.debug('#' * 50)

        # Get Dockerhub TOKEN
        token = get_token(request.headers["username"], request.headers["password"])
        if token is None:
            return jsonify({"result": "401"}), 401

        # Dockerhub Request parameters
        api_headers = {
            'Authorization': 'Bearer {}'.format(token),
        }
        api_url = dockerhub_conf["api_base_url"] + dockerhub_conf["api_path"]["get_tags"].format(registry)

        rows = []
        while True:
            globals.logger.debug('CALL {}'.format(api_url))
            api_response = requests.get( api_url, headers=api_headers)
            if api_response.status_code != 200:
                return jsonify({"result": api_response.status_code}), api_response.status_code

            api_response_json = json.loads(api_response.text)
            for result in api_response_json["results"]:
                row = {
                    "name": registry,
                    "url":  dockerhub_conf["link_url"].format(registry),
                    "tag":  result["name"],
                    "tag_last_pushed":  result["tag_last_pushed"],
                    "full_size":    result["full_size"]
                }
                rows.append(row)

            if api_response_json["next"] is None:
                break
            else:
                api_url = api_response_json["next"]

        return jsonify({"result": 200, "rows": rows}), 200

    except common.UserException as e:
        return common.server_error_to_message(e, app_name + exec_stat, error_detail)
    except Exception as e:
        return common.server_error_to_message(e, app_name + exec_stat, error_detail)


def get_repositories_acr(registry):
    """get azure container registry image list

    Args:
        registry (string): image

    Returns:
        Response: HTTP Response
    """
    app_name = "ワークスペース情報:"
    exec_stat = "Azure Container Registry images取得"
    error_detail = ""

    try:
        globals.logger.debug('#' * 50)
        globals.logger.debug('CALL {} registry:{}'.format(inspect.currentframe().f_code.co_name, registry))
        globals.logger.debug('#' * 50)

        api_url_origin = acr_conf["api_base_url"].format(registry.split("/",1)[0])
        api_url = acr_conf["api_path"]["get_tags"].format(api_url_origin, registry.split("/",1)[1])
        api_auth = HTTPBasicAuth(request.headers["username"], request.headers["password"])

        rows = []
        while True:
            globals.logger.debug('CALL {}'.format(api_url))
            api_response = requests.get( api_url, auth=api_auth )
            if api_response.status_code != 200:
                return jsonify({"result": api_response.status_code}), api_response.status_code

            api_response_json = json.loads(api_response.text)
            for result in api_response_json["tags"]:
                row = {
                    "name": registry,
                    "url":  None,
                    "tag":  result["name"],
                    "tag_last_pushed":  result["lastUpdateTime"],
                    "full_size":    None
                }
                rows.append(row)

            if "Link" in api_response.headers:
                api_url = api_url_origin + re.sub(r'^<', "", re.sub(r'>$', "", api_response.headers["Link"].split(';',1)[0]))
            else:
                break

        return jsonify({"result": 200, "rows": rows}), 200

    except common.UserException as e:
        return common.server_error_to_message(e, app_name + exec_stat, error_detail)
    except Exception as e:
        return common.server_error_to_message(e, app_name + exec_stat, error_detail)


def get_token(username, password):
    """Get toekn - token取得

    Args:
        username (str): dockerhub username
        password (str): dockerhub password

    Returns:
        str: token
    """
    globals.logger.debug('#' * 50)
    globals.logger.debug('CALL {}'.format(inspect.currentframe().f_code.co_name))
    globals.logger.debug('#' * 50)

    api_headers = {
        'Content-Type': 'application/json',
    }
    api_data = json.dumps({
        "username" :    username,
        "password" :    password
    })

    globals.logger.debug('CALL {}'.format(dockerhub_conf["api_base_url"] + dockerhub_conf["api_path"]["get_token"]))
    api_response = requests.post( dockerhub_conf["api_base_url"] + dockerhub_conf["api_path"]["get_token"], headers=api_headers, data=api_data)
    if api_response.status_code != 200:
        return None
    
    api_response_json = json.loads(api_response.text)

    return api_response_json["token"]


if __name__ == "__main__":
    app.run(debug=eval(os.environ.get('API_DEBUG', "False")), host='0.0.0.0', port=int(os.environ.get('API_DOCKERHUB_PORT', '8000')), threaded=True)
