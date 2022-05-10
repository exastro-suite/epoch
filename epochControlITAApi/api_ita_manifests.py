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
import api_access_info
import multi_lang

# 設定ファイル読み込み・globals初期化 flask setting file read and globals initialize
app = Flask(__name__)
app.config.from_envvar('CONFIG_API_ITA_PATH')
globals.init(app)

EPOCH_ITA_HOST = "it-automation"
EPOCH_ITA_PORT = "8084"

#
# メニューID
#
# 基本コンソール - 投入オペレーション一覧
ite_menu_operation = '2100000304'
# マニフェスト変数管理 - マニフェスト環境パラメータ
ita_menu_manifest_param = '0000000004'
# マニフェスト変数管理 - マニフェスト登録先Git環境パラメータ
ita_menu_gitenv_param = '0000000005'
# マニフェスト変数管理 - BlueGreen支援パラメータ
ita_menu_bluegreen_param = '0000000008'
# Ansible共通 - テンプレート管理
ita_menu_manifest_template = '2100040704'

# 共通項目
column_indexes_common = {
    "method": 0,    # 実行処理種別
    "delete": 1,    # 廃止
    "record_no": 2, # No
}
# 項目名リスト
column_names_opelist = {
    'operation_id': 'オペレーションID',
    'operation_name': 'オペレーション名',
    'operation_date': '実施予定日時',
    'remarks': '備考',
}
column_names_gitlist = {
    'host' : 'ホスト名',
    'operation_id' : 'オペレーション/ID',
    'operation' : 'オペレーション/オペレーション',
    'git_url' : 'パラメータ/Git URL',
    'git_user' : 'パラメータ/Git User',
    'git_password' : 'パラメータ/Git Password',
    'lastupdate' : '更新用の最終更新日時',
}
# 項目名リスト
column_names_manifest_param = {
    'host' : 'ホスト名',
    'operation_id' : 'オペレーション/ID',
    'operation' : 'オペレーション/オペレーション',
    'indexes' : '代入順序',
    'image' : 'パラメータ/固定パラメータ/image',
    'image_tag' : 'パラメータ/固定パラメータ/image_tag',
    'param01' : 'パラメータ/汎用パラメータ/param01',
    'param02' : 'パラメータ/汎用パラメータ/param02',
    'param03' : 'パラメータ/汎用パラメータ/param03',
    'param04' : 'パラメータ/汎用パラメータ/param04',
    'param05' : 'パラメータ/汎用パラメータ/param05',
    'param06' : 'パラメータ/汎用パラメータ/param06',
    'param07' : 'パラメータ/汎用パラメータ/param07',
    'param08' : 'パラメータ/汎用パラメータ/param08',
    'param09' : 'パラメータ/汎用パラメータ/param09',
    'param10' : 'パラメータ/汎用パラメータ/param10',
    'param11' : 'パラメータ/汎用パラメータ/param11',
    'param12' : 'パラメータ/汎用パラメータ/param12',
    'param13' : 'パラメータ/汎用パラメータ/param13',
    'param14' : 'パラメータ/汎用パラメータ/param14',
    'param15' : 'パラメータ/汎用パラメータ/param15',
    'param16' : 'パラメータ/汎用パラメータ/param16',
    'param17' : 'パラメータ/汎用パラメータ/param17',
    'param18' : 'パラメータ/汎用パラメータ/param18',
    'param19' : 'パラメータ/汎用パラメータ/param19',
    'param20' : 'パラメータ/汎用パラメータ/param20',
    'template_name' : 'パラメータ/固定パラメータ/template_name',
    'lastupdate' : '更新用の最終更新日時',
}

# 項目名リスト Item name list
column_names_bluegreen_param = {
    'host' : 'ホスト名',
    'operation_id' : 'オペレーション/ID',
    'operation' : 'オペレーション/オペレーション',
    'indexes' : '代入順序',
    'bluegreen_sdd_sec' : 'パラメータ/bluegreen_sdd_sec',
    'lastupdate' : '更新用の最終更新日時',
}

param_value_host="ita-worker"
param_value_method_entry='登録'
param_value_method_update='更新'
param_value_method_delete='廃止'
param_value_operation_date='2999/12/31 23:59'
param_value_operation_name_prefix='CD実行:'


def settings_git_environment(workspace_id):
    """git environment setting

    Args:
        workspace_id (int): workspace ID

    Returns:
        Response: HTTP Respose
    """

    globals.logger.info('Set git environment. workspace_id={}'.format(workspace_id))

    app_name = "ワークスペース情報:"
    exec_stat = "IT-Automation git情報設定"
    error_detail = ""

    try:

        # パラメータ情報(JSON形式) prameter save
        payload = request.json.copy()

        # ワークスペースアクセス情報取得
        access_info = api_access_info.get_access_info(workspace_id)

        # namespaceの取得
        namespace = common.get_namespace_name(workspace_id)

        ita_restapi_endpoint = "http://{}.{}.svc:{}/default/menu/07_rest_api_ver1.php".format(EPOCH_ITA_HOST, namespace, EPOCH_ITA_PORT)
        ita_user = access_info['ITA_USER']
        ita_pass = access_info['ITA_PASSWORD']

        # HTTPヘッダの生成
        filter_headers = {
            'host': EPOCH_ITA_HOST + ':' + EPOCH_ITA_PORT,
            'Content-Type': 'application/json',
            'Authorization': base64.b64encode((ita_user + ':' + ita_pass).encode()),
            'X-Command': 'FILTER',
        }

        edit_headers = {
            'host': EPOCH_ITA_HOST + ':' + EPOCH_ITA_PORT,
            'Content-Type': 'application/json',
            'Authorization': base64.b64encode((ita_user + ':' + ita_pass).encode()),
            'X-Command': 'EDIT',
        }

        #
        # オペレーションの取得
        #
        opelist_resp = requests.post(ita_restapi_endpoint + '?no=' + ite_menu_operation, headers=filter_headers)
        opelist_json = json.loads(opelist_resp.text)
        globals.logger.debug('---- Operation ----')
        #logger.debug(opelist_resp.text.encode().decode('unicode-escape'))
        # globals.logger.debug(opelist_resp.text)

        # 項目位置の取得
        column_indexes_opelist = column_indexes(column_names_opelist, opelist_json['resultdata']['CONTENTS']['BODY'][0])
        globals.logger.debug('---- Operation Index ----')
        # globals.logger.debug(column_indexes_opelist)

        #
        # オペレーションの追加処理
        #
        opelist_edit = []
        for idx_req, row_req in enumerate(payload['cd_config']['environments']):
            if search_opration(opelist_json['resultdata']['CONTENTS']['BODY'], column_indexes_opelist, row_req['git_repositry']['url']) == -1:
                # オペレーションになければ、追加データを設定
                opelist_edit.append(
                    {
                        str(column_indexes_common['method']) : param_value_method_entry,
                        str(column_indexes_opelist['operation_name']) : param_value_operation_name_prefix + row_req['git_repositry']['url'],
                        str(column_indexes_opelist['operation_date']) : param_value_operation_date,
                        str(column_indexes_opelist['remarks']) : row_req['git_repositry']['url'],
                    }
                )

        if len(opelist_edit) > 0:
            #
            # オペレーションの追加がある場合
            #
            ope_add_resp = requests.post(ita_restapi_endpoint + '?no=' + ite_menu_operation, headers=edit_headers, data=json.dumps(opelist_edit))

            globals.logger.debug('---- ope_add_resp ----')
            #logger.debug(ope_add_resp.text.encode().decode('unicode-escape'))
            globals.logger.debug(ope_add_resp.text)

            # 追加後再取得(オペレーションIDが決定する)
            opelist_resp = requests.post(ita_restapi_endpoint + '?no=' + ite_menu_operation, headers=filter_headers)        
            opelist_json = json.loads(opelist_resp.text)
            globals.logger.debug('---- Operation ----')
            #logger.debug(opelist_resp.text.encode().decode('unicode-escape'))

        #
        # Git環境情報の取得
        #
        gitlist_resp = requests.post(ita_restapi_endpoint + '?no=' + ita_menu_gitenv_param, headers=filter_headers)
        gitlist_json = json.loads(gitlist_resp.text)
        globals.logger.debug('---- Git Environments ----')
        #logger.debug(gitlist_resp.text.encode().decode('unicode-escape'))
        #logger.debug(gitlist_resp.text)

        # 項目位置の取得
        column_indexes_gitlist = column_indexes(column_names_gitlist, gitlist_json['resultdata']['CONTENTS']['BODY'][0])
        globals.logger.debug('---- Git Environments Index ----')
        # logger.debug(column_indexes_gitlist)

        # Responseデータの初期化
        response = {"items":[]}
        # Git環境情報の追加・更新
        gitlist_edit = []
        for idx_req, row_req in enumerate(payload['cd_config']['environments']):
            idx_git = search_gitlist(gitlist_json['resultdata']['CONTENTS']['BODY'], column_indexes_gitlist, row_req['git_repositry']['url'])
            if idx_git == -1:
                # リストになければ、追加データを設定
                # 追加対象のURLのオペレーション
                idx_ope = search_opration(opelist_json['resultdata']['CONTENTS']['BODY'], column_indexes_opelist, row_req['git_repositry']['url'])

                # 追加処理データの設定
                gitlist_edit.append(
                    {
                        str(column_indexes_common['method']) : param_value_method_entry,
                        str(column_indexes_gitlist['host']) : param_value_host,
                        str(column_indexes_gitlist['operation_id']) : opelist_json['resultdata']['CONTENTS']['BODY'][idx_ope][column_indexes_opelist['operation_id']],
                        str(column_indexes_gitlist['operation']) : format_opration_info(opelist_json['resultdata']['CONTENTS']['BODY'][idx_ope], column_indexes_opelist),
                        str(column_indexes_gitlist['git_url']) : row_req['git_repositry']['url'],
                        str(column_indexes_gitlist['git_user']) : payload['cd_config']['environments_common']['git_repositry']['user'],
                        str(column_indexes_gitlist['git_password']) : payload['cd_config']['environments_common']['git_repositry']['token'],
                    }
                )

                # レスポンスデータの設定
                response["items"].append(
                    {
                        'operation_id' : opelist_json['resultdata']['CONTENTS']['BODY'][idx_ope][column_indexes_opelist['operation_id']],
                        'git_url' : row_req['git_repositry']['url'],
                        'git_user' : payload['cd_config']['environments_common']['git_repositry']['user'],
                        'git_password' : payload['cd_config']['environments_common']['git_repositry']['token'],
                    }
                )

            else:
                # リストにあれば、更新データを設定
                gitlist_edit.append(
                    {
                        str(column_indexes_common['method']) : param_value_method_update,
                        str(column_indexes_common['record_no']) : gitlist_json['resultdata']['CONTENTS']['BODY'][idx_git][column_indexes_common['record_no']],
                        str(column_indexes_gitlist['host']) : gitlist_json['resultdata']['CONTENTS']['BODY'][idx_git][column_indexes_gitlist['host']],
                        str(column_indexes_gitlist['operation']) : gitlist_json['resultdata']['CONTENTS']['BODY'][idx_git][column_indexes_gitlist['operation']],
                        str(column_indexes_gitlist['git_url']) : row_req['git_repositry']['url'],
                        str(column_indexes_gitlist['git_user']) : payload['cd_config']['environments_common']['git_repositry']['user'],
                        str(column_indexes_gitlist['git_password']) : payload['cd_config']['environments_common']['git_repositry']['token'],
                        str(column_indexes_gitlist['lastupdate']) : gitlist_json['resultdata']['CONTENTS']['BODY'][idx_git][column_indexes_gitlist['lastupdate']],
                    }
                )

                # レスポンスデータの設定
                response["items"].append(
                    {
                        'operation_id' : gitlist_json['resultdata']['CONTENTS']['BODY'][idx_git][column_indexes_gitlist['operation_id']],
                        'git_url' : row_req['git_repositry']['url'],
                        'git_user' : payload['cd_config']['environments_common']['git_repositry']['user'],
                        'git_password' : payload['cd_config']['environments_common']['git_repositry']['token'],
                    }
                )

        globals.logger.debug('---- Git Environments Post ----')
        #logger.debug(json.dumps(gitlist_edit).encode().decode('unicode-escape'))
        # logger.debug(json.dumps(gitlist_edit))

        gitlist_edit_resp = requests.post(ita_restapi_endpoint + '?no=' + ita_menu_gitenv_param, headers=edit_headers, data=json.dumps(gitlist_edit))

        globals.logger.debug('---- Git Environments Post Response ----')
        #logger.debug(gitlist_edit_resp.text.encode().decode('unicode-escape'))
        # globals.logger.debug(gitlist_edit_resp.text)

        # 正常終了
        ret_status = 200

        globals.logger.info('SUCCESS: Set git environment. workspace_id={}, ret_status={}, git_environment_count={}'.format(workspace_id, ret_status, len(response["items"])))

        # 戻り値をそのまま返却        
        return jsonify({"result": ret_status, "rows": response["items"]}), ret_status

    except common.UserException as e:
        return common.server_error_to_message(e, app_name + exec_stat, error_detail)
    except Exception as e:
        return common.server_error_to_message(e, app_name + exec_stat, error_detail)


def column_indexes(column_names, row_header):
    """項目位置の取得 Get item position

    Args:
        column_names (str[]): column names 
        row_header (str): row header

    Returns:
        int: column index
    """
    column_indexes = {}
    for idx in column_names:
        column_indexes[idx] = row_header.index(column_names[idx])
    return column_indexes

def search_opration(opelist, column_indexes, git_url):
    """オペレーションの検索 search operation

    Args:
        opelist (dict): operation info. 
        column_indexes (dict): column indexes
        git_url (str): git url

    Returns:
        int: -1:error , other: index 
    """
    for idx, row in enumerate(opelist):
        if idx == 0:
            # 1行目はヘッダなので読み飛ばし
            continue

        if row[column_indexes_common["delete"]] != "":
            # 削除は無視
            continue

        if row[column_indexes['remarks']] is None:
            # 備考設定なしは無視
            continue

        globals.logger.debug('git_url:'+git_url)
        globals.logger.debug('row[column_indexes[remarks]]:'+row[column_indexes['remarks']])
        if git_url == row[column_indexes['remarks']]:
            # 備考にgit_urlが含まれているとき
            globals.logger.debug('find:' + str(idx))
            return idx

    # 存在しないとき
    return -1

#
# オペレーション選択文字列の生成
#
def format_opration_info(operow, column_indexes):
    return operow[column_indexes['operation_date']] + '_' + operow[column_indexes['operation_id']] + ':' + operow[column_indexes['operation_name']]

#
# git情報の検索
#
def search_gitlist(gitlist, column_indexes, git_url):
    for idx, row in enumerate(gitlist):
        if idx == 0:
            # 1行目はヘッダなので読み飛ばし
            continue

        if row[column_indexes_common["delete"]] != "":
            # 削除は無視
            continue

        if git_url == row[column_indexes['git_url']]:
            # git_urlが存在したとき
            return idx

    # 存在しないとき
    return -1


def settings_manifest_parameter(workspace_id):
    """manifest parameter setting

    Returns:
        Response: HTTP Respose
    """

    globals.logger.info('Set it-automation manifest parameter. workspace_id={}'.format(workspace_id))

    app_name = "ワークスペース情報:"
    exec_stat = "実行環境取得"
    error_detail = ""

    try:
        # パラメータ情報(JSON形式) prameter save
        payload = request.json.copy()

        # ワークスペースアクセス情報取得
        access_info = api_access_info.get_access_info(workspace_id)

        # namespaceの取得
        namespace = common.get_namespace_name(workspace_id)

        ita_restapi_endpoint = "http://{}.{}.svc:{}/default/menu/07_rest_api_ver1.php".format(EPOCH_ITA_HOST, namespace, EPOCH_ITA_PORT)
        ita_user = access_info['ITA_USER']
        ita_pass = access_info['ITA_PASSWORD']

        # HTTPヘッダの生成
        filter_headers = {
            'host': EPOCH_ITA_HOST + ':' + EPOCH_ITA_PORT,
            'Content-Type': 'application/json',
            'Authorization': base64.b64encode((ita_user + ':' + ita_pass).encode()),
            'X-Command': 'FILTER',
        }

        edit_headers = {
            'host': EPOCH_ITA_HOST + ':' + EPOCH_ITA_PORT,
            'Content-Type': 'application/json',
            'Authorization': base64.b64encode((ita_user + ':' + ita_pass).encode()),
            'X-Command': 'EDIT',
        }

        # globals.logger.debug(payload)

        #
        # オペレーションの取得
        #
        opelist_resp = requests.post(ita_restapi_endpoint + '?no=' + ite_menu_operation, headers=filter_headers)
        opelist_json = json.loads(opelist_resp.text)
        globals.logger.debug('---- Operation ----')
        # logger.debug(opelist_resp.text)
        # logger.debug(opelist_json)

        # 項目位置の取得
        column_indexes_opelist = column_indexes(column_names_opelist, opelist_json['resultdata']['CONTENTS']['BODY'][0])
        globals.logger.debug('---- Operation Index ----')
        # logger.debug(column_indexes_opelist)

        #
        # マニフェスト環境パラメータの取得
        #
        content = {
            "1": {
                "NORMAL": "0"
            }
        }
        response = requests.post(ita_restapi_endpoint + '?no=' + ita_menu_manifest_param, headers=filter_headers, data=json.dumps(content))
        if response.status_code != 200:
            globals.logger.error("call ita_menu_call error:{} menu_no:{}".format(response.status_code, ita_menu_manifest_param))
            raise common.UserException(multi_lang.get_text("EP034-0009", "IT-Automation manifestパラメータ取得失敗"))

        maniparam_json = json.loads(response.text)
        globals.logger.debug('---- Current Manifest Parameters ----')
        # logger.debug(response.text)
        globals.logger.debug(maniparam_json)

        # 項目位置の取得 Get item position
        column_indexes_maniparam = column_indexes(column_names_manifest_param, maniparam_json['resultdata']['CONTENTS']['BODY'][0])
        globals.logger.debug('---- Manifest Parameters Index ----')
        # logger.debug(column_indexes_maniparam)

        response = requests.post(ita_restapi_endpoint + '?no=' + ita_menu_bluegreen_param, headers=filter_headers, data=json.dumps(content))
        if response.status_code != 200:
            globals.logger.error("call ita_menu_call error:{} menu_no:{}".format(response.status_code, ita_menu_bluegreen_param))
            raise common.UserException(multi_lang.get_text("EP034-0010", "IT-Automation BlueGreen支援パラメータ取得失敗"))

        bluegreen_param_json = json.loads(response.text)
        globals.logger.debug('---- Current Bluegreen Parameters ----')
        # logger.debug(response.text)
        globals.logger.debug(bluegreen_param_json)

        # BlueGreen支援項目位置の取得 Get item position
        column_indexes_bluegreen_param = column_indexes(column_names_bluegreen_param, bluegreen_param_json['resultdata']['CONTENTS']['BODY'][0])
        globals.logger.debug('---- Manifest Parameters Index ----')
        globals.logger.debug(f"column_indexes_bluegreen_param:{column_indexes_bluegreen_param}")

        # # Responseデータの初期化
        # response = {"result":"200",}

        globals.logger.debug("opelist:{}".format(opelist_json['resultdata']['CONTENTS']['BODY']))
        # マニフェスト環境パラメータのデータ成型
        maniparam_edit = []
        bluegreen_edit = []
        for environment in payload['ci_config']['environments']:
            
            idx_ope = -1
            # cd_configの同一環境情報からgit_urlを取得する Get git_url from the same environment information in cd_config
            for cd_environment in payload['cd_config']['environments']:
                if environment['environment_id'] == cd_environment['environment_id']:
                    globals.logger.debug("git_url:{}".format(cd_environment['git_repositry']['url']))
                    idx_ope = search_opration(opelist_json['resultdata']['CONTENTS']['BODY'], column_indexes_opelist, cd_environment['git_repositry']['url'])

            # ITAからオペレーション(=環境)が取得できなければ異常
            if idx_ope == -1:
                error_detail = "CD環境が設定されていません。"
                raise common.UserException(error_detail)

            req_maniparam_operation_id = opelist_json['resultdata']['CONTENTS']['BODY'][idx_ope][column_indexes_common['record_no']]

            for idx_manifile, row_manifile in enumerate(environment['manifests']):

                image = None
                image_tag = None
                param01 = None
                param02 = None
                param03 = None
                param04 = None
                param05 = None
                param06 = None
                param07 = None
                param08 = None
                param09 = None
                param10 = None
                param11 = None
                param12 = None
                param13 = None
                param14 = None
                param15 = None
                param16 = None
                param17 = None
                param18 = None
                param19 = None
                param20 = None
                bluegreen_sdd_sec = None
                # parameters成型
                for key, value in row_manifile['parameters'].items():
                    if key == 'image':
                        image = value
                    elif key == 'image_tag':
                        image_tag = value
                    elif key == 'param01':
                        param01 = value
                    elif key == 'param02':
                        param02 = value
                    elif key == 'param03':
                        param03 = value
                    elif key == 'param04':
                        param04 = value
                    elif key == 'param05':
                        param05 = value
                    elif key == 'param06':
                        param06 = value
                    elif key == 'param07':
                        param07 = value
                    elif key == 'param08':
                        param08 = value
                    elif key == 'param09':
                        param09 = value
                    elif key == 'param10':
                        param10 = value
                    elif key == 'param11':
                        param11 = value
                    elif key == 'param12':
                        param12 = value
                    elif key == 'param13':
                        param13 = value
                    elif key == 'param14':
                        param14 = value
                    elif key == 'param15':
                        param15 = value
                    elif key == 'param16':
                        param16 = value
                    elif key == 'param17':
                        param17 = value
                    elif key == 'param18':
                        param18 = value
                    elif key == 'param19':
                        param19 = value
                    elif key == 'param20':
                        param20 = value
                    elif key == 'bluegreen_sdd_sec':
                        bluegreen_sdd_sec = value

                # 既存データ確認
                maniparam_id = -1
                for idx_maniparam, row_maniparam in enumerate(maniparam_json['resultdata']['CONTENTS']['BODY']):
                    current_maniparam_operation_id = row_maniparam[column_indexes_maniparam['operation_id']]
                    current_maniparam_include_index = row_maniparam[column_indexes_maniparam['indexes']]
                    if current_maniparam_operation_id == req_maniparam_operation_id and \
                            current_maniparam_include_index == str(idx_manifile + 1):
                        maniparam_id = row_maniparam[column_indexes_common['record_no']]
                        break

                if maniparam_id == -1:
                    # 追加処理データの設定
                    maniparam_edit.append(
                        {
                            str(column_indexes_common['method']) : param_value_method_entry,
                            str(column_indexes_maniparam['host']) : param_value_host,
                            str(column_indexes_maniparam['operation']) : format_opration_info(opelist_json['resultdata']['CONTENTS']['BODY'][idx_ope], column_indexes_opelist),
                            str(column_indexes_maniparam['indexes']) : idx_manifile + 1,
                            str(column_indexes_maniparam['image']) : image,
                            str(column_indexes_maniparam['image_tag']) : image_tag,
                            str(column_indexes_maniparam['param01']) : param01,
                            str(column_indexes_maniparam['param02']) : param02,
                            str(column_indexes_maniparam['param03']) : param03,
                            str(column_indexes_maniparam['param04']) : param04,
                            str(column_indexes_maniparam['param05']) : param05,
                            str(column_indexes_maniparam['param06']) : param06,
                            str(column_indexes_maniparam['param07']) : param07,
                            str(column_indexes_maniparam['param08']) : param08,
                            str(column_indexes_maniparam['param09']) : param09,
                            str(column_indexes_maniparam['param10']) : param10,
                            str(column_indexes_maniparam['param11']) : param11,
                            str(column_indexes_maniparam['param12']) : param12,
                            str(column_indexes_maniparam['param13']) : param13,
                            str(column_indexes_maniparam['param14']) : param14,
                            str(column_indexes_maniparam['param15']) : param15,
                            str(column_indexes_maniparam['param16']) : param16,
                            str(column_indexes_maniparam['param17']) : param17,
                            str(column_indexes_maniparam['param18']) : param18,
                            str(column_indexes_maniparam['param19']) : param19,
                            str(column_indexes_maniparam['param20']) : param20,
                            str(column_indexes_maniparam['template_name']) : '"{{ TPF_epoch_template_yaml' + str(idx_manifile + 1) + ' }}"',
                        }
                    )
                    globals.logger.debug('---- Manifest Parameters Item(Add) ----')
                    globals.logger.debug(maniparam_edit[len(maniparam_edit) -1])

                else:
                    # 更新処理
                    maniparam_edit.append(
                        {
                            str(column_indexes_common['method']) : param_value_method_update,
                            str(column_indexes_common['record_no']) : maniparam_id,
                            str(column_indexes_maniparam['host']) : maniparam_json['resultdata']['CONTENTS']['BODY'][idx_maniparam][column_indexes_maniparam['host']],
                            str(column_indexes_maniparam['operation']) : maniparam_json['resultdata']['CONTENTS']['BODY'][idx_maniparam][column_indexes_maniparam['operation']],
                            str(column_indexes_maniparam['indexes']) : maniparam_json['resultdata']['CONTENTS']['BODY'][idx_maniparam][column_indexes_maniparam['indexes']],
                            str(column_indexes_maniparam['image']) : image,
                            str(column_indexes_maniparam['image_tag']) : image_tag,
                            str(column_indexes_maniparam['param01']) : param01,
                            str(column_indexes_maniparam['param02']) : param02,
                            str(column_indexes_maniparam['param03']) : param03,
                            str(column_indexes_maniparam['param04']) : param04,
                            str(column_indexes_maniparam['param05']) : param05,
                            str(column_indexes_maniparam['param06']) : param06,
                            str(column_indexes_maniparam['param07']) : param07,
                            str(column_indexes_maniparam['param08']) : param08,
                            str(column_indexes_maniparam['param09']) : param09,
                            str(column_indexes_maniparam['param10']) : param10,
                            str(column_indexes_maniparam['param11']) : param11,
                            str(column_indexes_maniparam['param12']) : param12,
                            str(column_indexes_maniparam['param13']) : param13,
                            str(column_indexes_maniparam['param14']) : param14,
                            str(column_indexes_maniparam['param15']) : param15,
                            str(column_indexes_maniparam['param16']) : param16,
                            str(column_indexes_maniparam['param17']) : param17,
                            str(column_indexes_maniparam['param18']) : param18,
                            str(column_indexes_maniparam['param19']) : param19,
                            str(column_indexes_maniparam['param20']) : param20,
                            str(column_indexes_maniparam['template_name']) : maniparam_json['resultdata']['CONTENTS']['BODY'][idx_maniparam][column_indexes_maniparam['template_name']],
                            str(column_indexes_maniparam['lastupdate']) : maniparam_json['resultdata']['CONTENTS']['BODY'][idx_maniparam][column_indexes_maniparam['lastupdate']],
                        }
                    )
                    globals.logger.debug('---- Manifest Parameters Item(Update) ----')
                    globals.logger.debug(maniparam_edit[len(maniparam_edit) -1])

                # 既存データ確認
                bluegreen_param_id = -1
                for idx, row in enumerate(bluegreen_param_json['resultdata']['CONTENTS']['BODY']):
                    current_operation_id = row[column_indexes_bluegreen_param['operation_id']]
                    current_include_index = row[column_indexes_bluegreen_param['indexes']]
                    if current_operation_id == req_maniparam_operation_id and \
                        current_include_index == str(idx_manifile + 1):
                        bluegreen_param_id = row[column_indexes_common['record_no']]
                        break

                if bluegreen_param_id == -1:

                    # BlueGreen用のパラメータも基本はparamと同様
                    # The parameters for BlueGreen are basically the same as param.
                    bluegreen_edit.append(
                        {
                            str(column_indexes_common['method']) : param_value_method_entry,
                            str(column_indexes_bluegreen_param['host']) : param_value_host,
                            str(column_indexes_bluegreen_param['operation']) : format_opration_info(opelist_json['resultdata']['CONTENTS']['BODY'][idx_ope], column_indexes_opelist),
                            str(column_indexes_bluegreen_param['indexes']) : idx_manifile + 1,
                            str(column_indexes_bluegreen_param['bluegreen_sdd_sec']) : bluegreen_sdd_sec,
                        }
                    )
                else:
                    globals.logger.debug("host idx:[{}]".format(column_indexes_bluegreen_param['host']))
                    globals.logger.debug("bluegreen_param_id:[{}]".format(bluegreen_param_id))
                    globals.logger.debug("host value:[{}]".format(bluegreen_param_json['resultdata']['CONTENTS']['BODY'][idx][column_indexes_bluegreen_param['host']]))
                    # BlueGreen用のパラメータも基本はparamと同様
                    # The parameters for BlueGreen are basically the same as param.
                    bluegreen_edit.append(
                        {
                            str(column_indexes_common['method']) : param_value_method_update,
                            str(column_indexes_common['record_no']) : bluegreen_param_id,
                            str(column_indexes_bluegreen_param['host']) : bluegreen_param_json['resultdata']['CONTENTS']['BODY'][idx][column_indexes_bluegreen_param['host']],
                            str(column_indexes_bluegreen_param['operation']) : bluegreen_param_json['resultdata']['CONTENTS']['BODY'][idx][column_indexes_bluegreen_param['operation']],
                            str(column_indexes_bluegreen_param['indexes']) : bluegreen_param_json['resultdata']['CONTENTS']['BODY'][idx][column_indexes_bluegreen_param['indexes']],
                            str(column_indexes_bluegreen_param['bluegreen_sdd_sec']) : bluegreen_sdd_sec,
                            str(column_indexes_bluegreen_param['lastupdate']) : bluegreen_param_json['resultdata']['CONTENTS']['BODY'][idx][column_indexes_bluegreen_param['lastupdate']],
                        }
                    )

        globals.logger.debug('---- Deleting Manifest Parameters Setting ----')
        # 既存データをすべて廃止する Abolish all existing data
        for idx_param, row_param in enumerate(maniparam_json['resultdata']['CONTENTS']['BODY']):
            # 1行目無視する
            if idx_param == 0:
                continue
            flgExists = False
            for idx_edit, row_edit in enumerate(maniparam_edit):
                # 該当するrecord_noがあれば、チェックする
                if str(column_indexes_common['record_no']) in row_edit:
                    if row_edit[str(column_indexes_common['record_no'])] == row_param[column_indexes_common['record_no']]:
                        flgExists = True
                        break
            
            # 該当するレコードがない場合は、廃止として追加する
            if not flgExists:
                # 削除用のデータ設定
                maniparam_edit.append(
                    {
                        str(column_indexes_common['method']) : param_value_method_delete,
                        str(column_indexes_common['record_no']) : row_param[column_indexes_common['record_no']],
                        str(column_indexes_maniparam['lastupdate']) : row_param[column_indexes_maniparam['lastupdate']],
                    }
                )

        globals.logger.debug('---- Deleting BlueGreen Parameters Setting ----')
        # 既存データをすべて廃止する Abolish all existing data
        for idx_param, row_param in enumerate(bluegreen_param_json['resultdata']['CONTENTS']['BODY']):
            # 1行目無視する
            if idx_param == 0:
                continue
            flgExists = False
            for idx_edit, row_edit in enumerate(bluegreen_edit):
                # 該当するrecord_noがあれば、チェックする
                if str(column_indexes_common['record_no']) in row_edit:
                    if row_edit[str(column_indexes_common['record_no'])] == row_param[column_indexes_common['record_no']]:
                        flgExists = True
                        break
            
            # 該当するレコードがない場合は、廃止として追加する
            if not flgExists:
                # 削除用のデータ設定
                bluegreen_edit.append(
                    {
                        str(column_indexes_common['method']) : param_value_method_delete,
                        str(column_indexes_common['record_no']) : row_param[column_indexes_common['record_no']],
                        str(column_indexes_bluegreen_param['lastupdate']) : row_param[column_indexes_bluegreen_param['lastupdate']],
                    }
                )

        globals.logger.debug('---- Updating Manifest Parameters ----')
        # globals.logger.debug(json.dumps(maniparam_edit))

        response = requests.post(ita_restapi_endpoint + '?no=' + ita_menu_manifest_param, headers=edit_headers, data=json.dumps(maniparam_edit))
        if response.status_code != 200:
            globals.logger.error("call ita_menu_call error:{} menu_no:{}".format(response.status_code, ita_menu_manifest_param))
            raise common.UserException(multi_lang.get_text("EP034-0011", "IT-Automation manifestパラメータ更新失敗"))

        maniparam_json = json.loads(response.text)

        globals.logger.debug('---- Manifest Parameters Post Response ----')
        # logger.debug(response.text)
        # globals.logger.debug(maniparam_json)

        if maniparam_json["status"] != "SUCCEED" or maniparam_json["resultdata"]["LIST"]["NORMAL"]["error"]["ct"] != 0:
            raise common.UserException(response.text.encode().decode('unicode-escape'))

        # BlueGreen支援パラメータの更新
        # Update of BlueGreen support parameters

        globals.logger.debug('---- Updating BlueGreen Parameters ----')
        # globals.logger.debug(json.dumps(bluegreen_edit))

        response = requests.post(ita_restapi_endpoint + '?no=' + ita_menu_bluegreen_param, headers=edit_headers, data=json.dumps(bluegreen_edit))
        if response.status_code != 200:
            globals.logger.error("call ita_menu_call error:{} menu_no:{}".format(response.status_code, ita_menu_bluegreen_param))
            raise common.UserException(multi_lang.get_text("EP034-0012", "IT-Automation BlueGreen支援パラメータ更新失敗"))

        bluegreen_param_json = json.loads(response.text)

        globals.logger.debug('---- BlueGreen Parameters Post Response ----')
        # logger.debug(response.text)
        # globals.logger.debug(bluegreen_param_json)

        if bluegreen_param_json["status"] != "SUCCEED" or bluegreen_param_json["resultdata"]["LIST"]["NORMAL"]["error"]["ct"] != 0:
            raise common.UserException(response.text.encode().decode('unicode-escape'))

        # 正常終了
        ret_status = 200

        globals.logger.info('SUCCES: Set it-automation manifest parameter. workspace_id={}, ret_status={}'.format(workspace_id, ret_status))

        # 戻り値をそのまま返却        
        return jsonify({"result": ret_status}), ret_status

    except common.UserException as e:
        return common.server_error_to_message(e, app_name + exec_stat, error_detail)
    except Exception as e:
        return common.server_error_to_message(e, app_name + exec_stat, error_detail)


# GitUrlの検索
#
def search_git_url(opelist, column_indexes, operation_id):
    for idx, row in enumerate(opelist):
        if idx == 0:
            # 1行目はヘッダなので読み飛ばし
            continue

        if row[column_indexes_common["delete"]] != "":
            # 削除は無視
            continue

        # logger.debug('operation_id:')
        # logger.debug(operation_id)
        # logger.debug('row[column_indexes[remarks]]:')
        # logger.debug(row[column_indexes['remarks']])
        if operation_id == row[column_indexes['operation_id']]:
            # 備考にgit_urlが含まれているとき
            globals.logger.debug('find:' + str(idx))
            return row[column_indexes['remarks']]

    # 存在しないとき
    return -1

#
# オペレーション選択文字列の生成
#
def format_opration_info(operow, column_indexes):
    return operow[column_indexes['operation_date']] + '_' + operow[column_indexes['operation_id']] + ':' + operow[column_indexes['operation_name']]

#
# git情報の検索
#
def search_maniparam(maniparam, column_indexes, git_url):
    for idx, row in enumerate(maniparam):
        if idx == 0:
            # 1行目はヘッダなので読み飛ばし
            continue

        if row[column_indexes_common["delete"]] != "":
            # 削除は無視
            continue

        if git_url == row[column_indexes['git_url']]:
            # git_urlが存在したとき
            return idx

    # 存在しないとき
    return -1

def settings_manifest_templates(workspace_id):
    """manifest templates setting

    Returns:
        Response: HTTP Respose
    """

    globals.logger.info('Set it-automation manifest template. workspace_id={}'.format(workspace_id))

    app_name = "ワークスペース情報:"
    exec_stat = "manifestテンプレートファイル登録"
    error_detail = ""

    try:
        # パラメータ情報(JSON形式) prameter save
        payload = request.json.copy()

        # ワークスペースアクセス情報取得
        access_info = api_access_info.get_access_info(workspace_id)

        # namespaceの取得
        namespace = common.get_namespace_name(workspace_id)

        ita_restapi_endpoint = "http://{}.{}.svc:{}/default/menu/07_rest_api_ver1.php".format(EPOCH_ITA_HOST, namespace, EPOCH_ITA_PORT)
        ita_user = access_info['ITA_USER']
        ita_pass = access_info['ITA_PASSWORD']

        # HTTPヘッダの生成
        filter_headers = {
            'host': EPOCH_ITA_HOST + ':' + EPOCH_ITA_PORT,
            'Content-Type': 'application/json',
            'Authorization': base64.b64encode((ita_user + ':' + ita_pass).encode()),
            'X-Command': 'FILTER',
        }

        edit_headers = {
            'host': EPOCH_ITA_HOST + ':' + EPOCH_ITA_PORT,
            'Content-Type': 'application/json',
            'Authorization': base64.b64encode((ita_user + ':' + ita_pass).encode()),
            'X-Command': 'EDIT',
        }

        #
        # マニフェストテンプレートの取得
        #
        content = {
            "1": {
                "NORMAL": "0"
            },
            "3": {
                "NORMAL": "TPF_epoch_template_yaml"
            },
        }
        manitpl_resp = requests.post(ita_restapi_endpoint + '?no=' + ita_menu_manifest_template, headers=filter_headers, data=json.dumps(content))
        manitpl_json = json.loads(manitpl_resp.text)
        globals.logger.debug('---- Current Manifest Templates ----')
        # logger.debug(manitpl_resp.text)
        # globals.logger.debug(manitpl_json)

        req_data = payload['manifests']
        mani_req_len = len(req_data)
        mani_ita_len = manitpl_json['resultdata']['CONTENTS']['RECORD_LENGTH']
        max_loop_cnt = max(mani_req_len, mani_ita_len)
        globals.logger.debug("max_loop_cnt: " + str(max_loop_cnt))

        ita_data = manitpl_json['resultdata']['CONTENTS']["BODY"]
        ita_data.pop(0)
        # globals.logger.debug(ita_data)

        edit_data = {
            "UPLOAD_FILE": []
        }
        tpl_cnt = 0
        for i in range(max_loop_cnt):

            # ITAを廃止
            if i > mani_req_len - 1:
                tmp_data = []
                for j, item in enumerate(ita_data[i]):
                    if j == 0:
                        tmp_data.append('廃止')
                    else:
                        tmp_data.append(item)

                edit_data[str(i)] = tmp_data

            # ITAに新規登録する
            elif i > mani_ita_len - 1:
                tpl_cnt += 1
                tmp_data = {}
                tmp_data['0'] = "登録"
                tmp_data['3'] = "TPF_epoch_template_yaml" + str(tpl_cnt)
                tmp_data['4'] = req_data[i]["file_name"]
                tmp_data['5'] = "VAR_image:\n"\
                                "VAR_image_tag:\n"\
                                "VAR_param01:\n"\
                                "VAR_param02:\n"\
                                "VAR_param03:\n"\
                                "VAR_param04:\n"\
                                "VAR_param05:\n"\
                                "VAR_param06:\n"\
                                "VAR_param07:\n"\
                                "VAR_param08:\n"\
                                "VAR_param09:\n"\
                                "VAR_param10:\n"\
                                "VAR_param11:\n"\
                                "VAR_param12:\n"\
                                "VAR_param13:\n"\
                                "VAR_param14:\n"\
                                "VAR_param15:\n"\
                                "VAR_param16:\n"\
                                "VAR_param17:\n"\
                                "VAR_param18:\n"\
                                "VAR_param19:\n"\
                                "VAR_param20:\n"\
                                "VAR_bluegreen_sdd_sec:"

                edit_data[str(i)] = tmp_data
                edit_data["UPLOAD_FILE"].append({"4": base64.b64encode(req_data[i]["file_text"].encode()).decode()})

            # ITAを更新する
            else:
                tpl_cnt += 1
                tmp_data = ita_data[i]
                tmp_data[0] = "更新"
                tmp_data[3] = "TPF_epoch_template_yaml" + str(tpl_cnt)
                tmp_data[4] = req_data[i]["file_name"]
                tmp_data[5] = "VAR_image:\n"\
                            "VAR_image_tag:\n"\
                            "VAR_param01:\n"\
                            "VAR_param02:\n"\
                            "VAR_param03:\n"\
                            "VAR_param04:\n"\
                            "VAR_param05:\n"\
                            "VAR_param06:\n"\
                            "VAR_param07:\n"\
                            "VAR_param08:\n"\
                            "VAR_param09:\n"\
                            "VAR_param10:\n"\
                            "VAR_param11:\n"\
                            "VAR_param12:\n"\
                            "VAR_param13:\n"\
                            "VAR_param14:\n"\
                            "VAR_param15:\n"\
                            "VAR_param16:\n"\
                            "VAR_param17:\n"\
                            "VAR_param18:\n"\
                            "VAR_param19:\n"\
                            "VAR_param20:\n"\
                            "VAR_bluegreen_sdd_sec:"

                edit_data[str(i)] = tmp_data
                edit_data["UPLOAD_FILE"].append({"4": base64.b64encode(req_data[i]["file_text"].encode()).decode()})

        # globals.logger.debug(edit_data)

        # ITAへREST実行
        manutemplate_edit_resp = requests.post(ita_restapi_endpoint + '?no=' + ita_menu_manifest_template, headers=edit_headers, data=json.dumps(edit_data))
        # manitemplate_json = json.loads(manutemplate_edit_resp.text)

        # globals.logger.debug(manitemplate_json)

        # 正常終了
        ret_status = 200

        globals.logger.info('SUCCESS: Set it-automation manifest template. workspace_id={}, ret_status={}'.format(workspace_id, ret_status))

        # 戻り値をそのまま返却        
        return jsonify({"result": ret_status}), ret_status

    except common.UserException as e:
        return common.server_error_to_message(e, app_name + exec_stat, error_detail)
    except Exception as e:
        return common.server_error_to_message(e, app_name + exec_stat, error_detail)
