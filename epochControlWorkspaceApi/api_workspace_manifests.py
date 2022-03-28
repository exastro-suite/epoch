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
import hashlib

import globals
import common

# 設定ファイル読み込み・globals初期化 flask setting file read and globals initialize
app = Flask(__name__)
app.config.from_envvar('CONFIG_API_WORKSPACE_PATH')
globals.init(app)


def settings_manifest_templates(workspace_id):
    """manifest templates setting

    Args:
        workspace_id (int): workspace ID

    Returns:
        Response: HTTP Respose
    """

    try:
        globals.logger.debug('#' * 50)
        globals.logger.debug('CALL {}'.format(inspect.currentframe().f_code.co_name))
        globals.logger.debug('#' * 50)

        # パラメータ情報(JSON形式) prameter 
        payload = request.json.copy()

        # BlueGreen manifest template変換
        # BlueGreen manifest template conversion
        ret_text = conv_yaml(payload["file_text"], payload["deploy_params"])

        # 正常終了 normal termination
        ret_status = 200

        # 戻り値をそのまま返却
        # Return the return value as it is
        return jsonify({"result": ret_status, "file_text": ret_text}), ret_status

    except common.UserException as e:
        return common.server_error_to_message(e, app_name + exec_stat, error_detail)
    except Exception as e:
        return common.server_error_to_message(e, app_name + exec_stat, error_detail)

def conv_yaml(file_text, params):
    """yamlファイルの解析変換 Parsing conversion of yaml file

    Args:
        file_text (str): 変換元yamlの内容 Contents of conversion source yaml
        params (dic): BlueGreen Deploy時のパラメータ(オプション値) Parameters (option value) for BlueGreen Deploy

    Returns:
        str : 変換後の内容
    """

    try:

        block_data = []
        block_keys = {}
        block_values = {}
        idx = 0
        split_text = file_text.split("\n")
        # ファイルの読み込み Read file
        for line in split_text:
            # globals.logger.debug("line:{}".format(line))
            # ":"を区切りとして要素と値に分ける
            # Divide into elements and values ​​with ":" as a delimiter
            split_line = line.split(":")
            # 区切り文字ありの場合は、Keyと値に分けて格納する
            # If there is a delimiter, store it separately as Key and value.
            if len(split_line) < 2:
                # globals.logger.debug(f"split_line:{split_line}")
                # "---"を一区切りとしてブロックの情報とする
                # Use "---" as a block information
                if line.strip() == "---":
                    block_data.append({"block": {"block_keys": block_keys,"block_values": block_values}})
                    block_data.append({"separation": line})
                    block_keys = {}
                    block_values = {}
                    idx = 0
                else:
                    # それ以外はそのまま格納
                    # Use "---" as a block information
                    block_data.append({"other": line})
            else:
                block_keys[idx] = split_line[0].rstrip() 
                block_values[idx] = split_line[1] 
                # globals.logger.debug(f"add block:{split_line}")
                idx += 1
            
        if len(block_keys) > 0:
            block_data.append({"block": {"block_keys": block_keys,"block_values": block_values}})

        out_yaml = ""
        # globals.logger.debug(f"block_data:{block_data}")
        # 加工した情報をブロック単位で処理する
        # Process processed information in block units
        for idx, values in enumerate(block_data):
            for key in values.keys():
                if key == "other" or key == "separation":
                    # globals.logger.debug(f"line:{values[key]}")
                    out_yaml += "{}\n".format(values[key])
                else:
                    # 置き換え対象のkindを検索する
                    # Search for the kind to be replaced
                    f_Deployment = False
                    f_Service = False
                    service_idx = -1
                    service_name = ""

                    if "kind" in values[key]["block_keys"].values() and \
                        "apiVersion" in values[key]["block_keys"].values() and \
                        "metadata" in values[key]["block_keys"].values():

                        kind_idx = get_keys_from_value(values[key]["block_keys"], "kind")
                        api_ver_idx = get_keys_from_value(values[key]["block_keys"], "apiVersion")
                        metadata_idx = get_keys_from_value(values[key]["block_keys"], "metadata")

                        # globals.logger.debug(f"kind_idx:{kind_idx}")
                        # globals.logger.debug(f"api_ver_idx:{api_ver_idx}")
                        # globals.logger.debug(f"metadata_idx:{metadata_idx}")

                        # globals.logger.debug("Kind:{}".format(values[key]["block_values"][kind_idx].strip()))
                        # globals.logger.debug("apiVersion:{}".format(values[key]["block_values"][api_ver_idx].strip()))

                        if values[key]["block_values"][kind_idx].strip() == "Deployment" and \
                            values[key]["block_values"][api_ver_idx].strip() == "apps/v1":
                            # f_Deployment = True
                            # pglobals.logger.debugrint("Hit!:kind:{} , apiVersion:{}".format(values[key]["block_values"][kind_idx], values[key]["block_values"][api_ver_idx]))

                            deployment_name_key = values[key]["block_keys"][metadata_idx + 1].strip()
                            deployment_name = values[key]["block_values"][metadata_idx + 1].strip()
                            service_name = deployment_name
                            # globals.logger.debug(f"deployment_name:{deployment_name}")

                            ports_name = ""
                            ports_port = ""
                            ports_protocol = ""

                            # portsセクションを見つけて、その配下にあるname, containerPort, protocolの要素を抽出する
                            # Find the ports section and extract the name, containerPort, protocol elements under it
                            for keys_index, keys_values in values[key]["block_keys"].items():
                                if keys_values.strip() == "ports":
                                    # globals.logger.debug("ports found!!")
                                    # インデントの数をチェック
                                    # Check the number of indent
                                    leftspace = keys_values.rstrip().replace("ports", "")
                                    idx = keys_index + 1
                                    left_len = len(leftspace)
                                    while idx < len(values[key]["block_keys"]):
                                        # 子の項目判断
                                        # Child item judgment
                                        if values[key]["block_keys"][idx][left_len:left_len + 1] == "-" or \
                                            values[key]["block_keys"][idx][left_len:left_len + 1] == " ":
                                            if values[key]["block_keys"][idx][left_len + 2:].strip() == "name":
                                                ports_name = values[key]["block_values"][idx].strip()
                                            elif values[key]["block_keys"][idx][left_len + 2:].strip() == "containerPort":
                                                f_Deployment = True
                                                ports_port = values[key]["block_values"][idx].strip()
                                            elif values[key]["block_keys"][idx][left_len + 2:].strip() == "protocol":
                                                ports_protocol = values[key]["block_values"][idx].strip()
                                        else:
                                            break
                                        idx += 1
                                    # globals.logger.debug(f"ports_name:{ports_name}")
                                    # globals.logger.debug(f"ports_port:{ports_port}")
                                    # globals.logger.debug(f"ports_protocol:{ports_protocol}")

                    if f_Deployment:
                        # globals.logger.debug(f"service_name:{service_name}")
                        service_name_preview = service_name + "-preview"

                    # BlueGreen対応のyaml生成
                    # BlueGreen compatible yaml generation
                    for block_idx, block_key in values[key]["block_keys"].items():
                        # deploymentの場合は、BlueGreenのyamlに置き換える
                        # For deployment, replace with BlueGreen yaml
                        if f_Deployment:
                            if block_key == "kind":
                                value = " Rollout"
                            elif block_key == "apiVersion":
                                value = " argoproj.io/v1alpha1"
                            else:
                                value = values[key]["block_values"][block_idx]
                        else:
                            value = values[key]["block_values"][block_idx]

                        # globals.logger.debug(f"line:{block_key}:{value}")
                        out_yaml += f"{block_key}:{value}\n"

                    # Rolloutのオプション値設定
                    # Rollout option value setting
                    if f_Deployment:
                        out_yaml += "  {}:\n".format("strategy")
                        out_yaml += "    {}:\n".format("blueGreen")
                        out_yaml += "      {}: {}\n".format("activeService", service_name)
                        out_yaml += "      {}: {}\n".format("previewService", service_name_preview)
                        for key, value in params.items():
                            out_yaml += "      {}: {}\n".format(key, value)
                        # out_yaml += "      {}: {}\n".format("scaleDownDelaySeconds", 120)

                        # preview面のサービスを追加
                        # Added preview service

                        out_yaml += "---\n"
                        out_yaml += "{}: {}\n".format("apiVersion", "v1")
                        out_yaml += "{}: {}\n".format("kind", "Service")
                        out_yaml += "{}:\n".format("metadata")
                        out_yaml += "  {}: {}\n".format("name", service_name_preview)
                        out_yaml += "  {}:\n".format("labels")
                        out_yaml += "    {}: {}\n".format("name", service_name_preview)
                        out_yaml += "{}:\n".format("spec")
                        out_yaml += "  {}: {}\n".format("type", "ClusterIP")
                        out_yaml += "  {}:\n".format("ports")
                        str_sep = "- "
                        if ports_name:
                            out_yaml += "  {}{}: {}\n".format(str_sep, "name", ports_name)
                            str_sep = "  "
                        if ports_port:
                            out_yaml += "  {}{}: {}\n".format(str_sep, "port", ports_port)
                            str_sep = "  "
                            out_yaml += "  {}{}: {}\n".format(str_sep, "targetPort", ports_port)
                        if ports_protocol:
                            out_yaml += "  {}{}: {}\n".format(str_sep, "protocol", ports_protocol)
                            str_sep = "  "
                        out_yaml += "  {}:\n".format("selector")
                        out_yaml += "    {}: {}\n".format(deployment_name_key, deployment_name)

        # globals.logger.debug(f"out_yaml:{out_yaml}")

        return out_yaml
    
    except Exception as e:
        raise

def get_keys_from_value(d, val):
    """辞書情報Value値からKey値の取得
        Obtaining the Key value from the dictionary information Value value

    Args:
        d (dict): 辞書情報 Dictionary information
        val (obj): Value値 Value

    Returns:
        obj: 該当するキー値(ない場合はNone) Applicable key value (None if none)
    """
    ret = None
    for k, v in d.items():
        if v == val:
            ret = k
            break
    return ret
