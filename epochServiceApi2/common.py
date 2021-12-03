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

from flask import jsonify
import random, string
import json

import globals

class UserException(Exception):
    pass

def delete_dict_key(dictobj, key):
    """Dictionary Key削除

    Args:
        dictobj (dict): Dictionary
        key (any): key
    """
    if key in dictobj:
        del dictobj[key]

def random_string(n):
    """ランダム文字列生成

    Args:
        n (int): 文字数

    Returns:
        str: ランダム文字列
    """
    return ''.join(random.choices(string.ascii_letters + string.digits, k=n))


def server_error(e):
    """サーバーエラーレスポンス

    Args:
        e (Exception): 例外

    Returns:
        response: HTTP Response (HTTP-500)
    """
    import traceback

    globals.logger.error(''.join(list(traceback.TracebackException.from_exception(e).format())))

    return jsonify(
        {
            'result':       '500',
            'exception':    ''.join(list(traceback.TracebackException.from_exception(e).format())),
        }
    ), 500

def server_error_to_message(e, error_statement, error_detail):
    """サーバーエラーレスポンス(メッセージ付き)

    Args:
        e (Exception): 例外
        error_statement (str): エラー情報（処理内容）
        error_detail (str): エラー情報詳細

    Returns:
        response: HTTP Response (HTTP-500)
    """
    import traceback

    globals.logger.error(''.join(list(traceback.TracebackException.from_exception(e).format())))

    return jsonify(
        {
            'result':       '500',
            'errorStatement': error_statement,
            'errorDetail':  error_detail,
            'exception':    ''.join(list(traceback.TracebackException.from_exception(e).format())),
        }
    ), 500


def is_json_format(str):
    """json値判断

    Args:
        str (str): json文字列

    Returns:
        bool: True:json, False:not json
    """
    try:
        # Exceptionで引っかかるときはすべてJson意外と判断
        json.loads(str)
    except json.JSONDecodeError:
        return False
    except ValueError:
        return False
    except Exception:
        return False
    return True


def get_namespace_name(workspace_id):
    """workspace_idに対するnamespace名取得

    Args:
        workspace_id (int): workspace ID

    Returns:
        str: namespace name
    """
    return  'epoch-ws-{}'.format(workspace_id)


def get_pipeline_name(workspace_id):
    """workspace_idに対するpipeline namespace名取得

    Args:
        workspace_id (int): workspace ID

    Returns:
        str: pipeline namespace name
    """
    return  'epoch-tekton-pipeline-{}'.format(workspace_id)


def get_file_id(dict, fileName):
    """辞書からfile_nameの値が一致するものがあるかチェックする

    Args:
        dict (json): 検索する対象Json
        fileName (String): 検索対象ファイル名（完全一致）

    Returns:
        String: ファイルID
    """

    try:
        # 戻り値の初期化
        file_id = ""

        for dictP in dict:
            # 該当する文字列が一致した場合は、処理を抜ける
            if dictP["file_name"] == fileName:
                file_id = dictP["id"]
                break

        return file_id

    except Exception:
        raise
