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
import yaml

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

    globals.logger.info('Set it-automation manifest template. workspace_id={}'.format(workspace_id))

    try:
        # パラメータ情報(JSON形式) prameter 
        payload = request.json.copy()

        # BlueGreen manifest template変換
        # BlueGreen manifest template conversion
        ret_text = conv_yaml(payload["file_text"], payload["deploy_params"])

        # 正常終了 normal termination
        ret_status = 200

        globals.logger.info('SUCCESS: Set it-automation manifest template. ret_status={}, workspace_id={}, ret_text_length ={}'.format(ret_status, workspace_id, len(ret_text)))

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
                block_values[idx] = line[len(split_line[0]) + 1:]
                # globals.logger.debug(f"add block:{split_line}")
                idx += 1
            
        if len(block_keys) > 0:
            block_data.append({"block": {"block_keys": block_keys,"block_values": block_values}})

        # ファイルの内容のテンプレートをいったん正規化してJson形式で変換する
        # Once normalize the template of the contents of the file and convert it in Json format
        json_yaml = [obj for obj in yaml.safe_load_all(re.sub("{{\s.*?\s}}", "x", file_text))]
        # globals.logger.debug(f"json_yaml:{json_yaml}")

        out_yaml = ""
        block_idx = 0
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
                    service_name = ""
                    ports_info = []

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

                            # port配下のインデント解決用 ただし、ports内に変数指定された場合の対処が必要なので、インデント固定化を有効化する
                            # For indent resolution under port However, since it is necessary to deal with the case where a variable is specified in ports, enable indent fixation.
                            # # containersまでの情報がそろっているかチェックする
                            # # Check if the information up to containers is complete
                            # if "spec" in json_yaml[block_idx] and \
                            #     "template" in json_yaml[block_idx]["spec"] and \
                            #     "spec" in json_yaml[block_idx]["spec"]["template"] and \
                            #     "containers" in json_yaml[block_idx]["spec"]["template"]["spec"]:

                            #     globals.logger.debug("containers:{}".format(json_yaml[block_idx]["spec"]["template"]["spec"]["containers"]))
                            #     # Portsがあるかチェックする
                            #     # Check for Ports
                            #     for container in json_yaml[block_idx]["spec"]["template"]["spec"]["containers"]:
                            #         if "ports" in container:
                            #             for container_port in container["ports"]:
                            #                 # containerPortが必須条件
                            #                 # containerPort is a prerequisite
                            #                 if "containerPort" in container_port:
                            #                     # 一つでもPort指定がないとBlueGreenは作成対象外
                            #                     # BlueGreen is not subject to creation unless even one Port is specified.
                            #                     f_Deployment = True
                            #                     # Portsの情報を格納
                            #                     # Store Ports information
                            #                     ports_info.append(
                            #                         {
                            #                             "ports_name": container_port.get("name",""),
                            #                             "ports_port": container_port.get("containerPort",""),
                            #                             "ports_protocol": container_port.get("protocol",""),
                            #                         }
                            #                     )
                            #                     # globals.logger.debug("add ports:{}.{}.{}".format(container_port.get("name", ""), container_port.get("containerPort", ""), container_port.get("protocol", "")))

                            ports_name = ""
                            ports_port = ""
                            ports_protocol = ""
                            ports_first = True  # 1回目のPortかどうか判断用のフラグ Flag for determining whether it is the first port

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

                                            if values[key]["block_keys"][idx][left_len:left_len + 1] == "-":
                                                if ports_first:
                                                    # 初回は格納しない
                                                    # Do not store the first time
                                                    ports_first = False
                                                else:
                                                    # Port番号の指定がある場合のみ
                                                    # Only when the port number is specified
                                                    if ports_port:
                                                        # nameがない場合は、自動付与('name-'+Port番号)
                                                        # If there is no name, it is automatically assigned ('name-' + Port number)
                                                        if not ports_name:
                                                            ports_name = f"name-{ports_port}"

                                                        # "-"を一区切りとしてPortsの情報を格納
                                                        # Store Ports information with "-" as a delimiter
                                                        ports_info.append(
                                                            {
                                                                "ports_name": ports_name,
                                                                "ports_port": ports_port,
                                                                "ports_protocol": ports_protocol,
                                                            }
                                                        )
                                                    ports_name = ""
                                                    ports_port = ""
                                                    ports_protocol = ""

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

                                # 情報があれば格納する Store information if available
                                if not ports_first:
                                    # Port番号の指定がある場合のみ
                                    # Only when the port number is specified
                                    if ports_port:
                                        # nameがない場合は、自動付与('name-'+Port番号)
                                        # If there is no name, it is automatically assigned ('name-' + Port number)
                                        if not ports_name:
                                            ports_name = f"name-{ports_port}"

                                        ports_info.append(
                                            {
                                                "ports_name": ports_name,
                                                "ports_port": ports_port,
                                                "ports_protocol": ports_protocol,
                                            }
                                        )
                                    ports_name = ""
                                    ports_port = ""
                                    ports_protocol = ""
                                    ports_first = True
                    
                    block_idx += 1

                    globals.logger.debug(f"ports_info:{ports_info}")

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
                        for port_info in ports_info:
                            str_sep = "- "
                            if port_info["ports_name"]:
                                out_yaml += "  {}{}: {}\n".format(str_sep, "name", port_info["ports_name"])
                                str_sep = "  "
                            if port_info["ports_port"]:
                                out_yaml += "  {}{}: {}\n".format(str_sep, "port", port_info["ports_port"])
                                str_sep = "  "
                                out_yaml += "  {}{}: {}\n".format(str_sep, "targetPort", port_info["ports_port"])
                            if port_info["ports_protocol"]:
                                out_yaml += "  {}{}: {}\n".format(str_sep, "protocol", port_info["ports_protocol"])
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
