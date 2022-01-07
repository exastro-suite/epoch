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
import traceback
import re

import globals
import const

class AuthException(Exception):
    pass

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
    """ランダム文字列生成 random string generator

    Args:
        n (int): 文字数 length

    Returns:
        str: ランダム文字列 random string
    """
    return ''.join(random.choices(string.ascii_letters + string.digits, k=n))


def str_mask(str):
    """指定文字列をマスク置き換えする Replace the specified character string with a mask

    Args:
        str (str): 文字列 string

    Returns:
        str: 置き換え文字列 afeter string
    """

    # 1文字以上の入力があれば置き換えする If there is more than one character input, replace it
    if len(str) > 0:
        ret = '*' * len(str)
    else:
        ret = str

    return ret

def server_error(e):
    """サーバーエラーレスポンス server error response

    Args:
        e (Exception): 例外 exception

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

def server_error_to_message(e, error_statement, error_detail, rows = None):
    """サーバーエラーレスポンス(メッセージ付き) server error response with message

    Args:
        e (Exception): 例外 exception
        error_statement (str): エラー情報（処理内容）error info. process contents
        error_detail (str): エラー情報詳細 error detail

    Returns:
        response: HTTP Response (HTTP-500)
    """
    import traceback

    globals.logger.error(''.join(list(traceback.TracebackException.from_exception(e).format())))

    ret_json = {
            'result': '500',
            'errorStatement': error_statement,
            'errorDetail': error_detail,
            'exception': ''.join(list(traceback.TracebackException.from_exception(e).format())),
    }
    # 返す情報がある場合は情報を設定 Set information if there is information to return
    if rows is not None:
        ret_json["rows"] = rows

    return jsonify(ret_json), 500

def user_error_to_message(e, error_statement, error_detail, return_code, rows = None):
    """ユーザー型サーバーエラーレスポンス(メッセージ付き) user server error response with message

    Args:
        e (Exception): 例外 exception
        error_statement (str): エラー情報（処理内容）error info. process contents
        error_detail (str): エラー情報詳細 error detail
        return_code (int)  return code

    Returns:
        response: HTTP Response (HTTP-[return_code])
    """
    import traceback

    globals.logger.error(''.join(list(traceback.TracebackException.from_exception(e).format())))

    ret_json = {
            'result': '500',
            'errorStatement': error_statement,
            'errorDetail': error_detail,
            'exception': ''.join(list(traceback.TracebackException.from_exception(e).format())),
    }
    # 返す情報がある場合は情報を設定 Set information if there is information to return
    if rows is not None:
        ret_json["rows"] = rows

    return jsonify(ret_json), return_code


def is_json_format(str):
    """json値判断 json value judgement

    Args:
        str (str): json文字列 json string

    Returns:
        bool: True:json, False:not json
    """
    try:
        # Exceptionで引っかかるときはすべてJson意外と判断
        # When it gets caught in Exception, it is judged that Json is unexpected
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

def get_current_user(header):
    """ログインユーザID取得

    Args:
        header (dict): request header情報

    Returns:
        str: ユーザID
    """
    try:
        # 該当の要素が無い場合は、confの設定に誤り
        HEAD_REMOTE_USER = "X-REMOTE-USER"
        if not HEAD_REMOTE_USER in header:
            raise Exception("get_current_user error not found header:{}".format(HEAD_REMOTE_USER))

        remote_user = header[HEAD_REMOTE_USER]
        # globals.logger.debug('{}:{}'.format(HEAD_REMOTE_USER, remote_user))

        # 最初の@があるところまでをuser_idとする
        idx = remote_user.rfind('@')
        user_id = remote_user[:idx]
        # globals.logger.debug('user_id:{}'.format(user_id))

        return user_id

    except Exception as e:
        globals.logger.debug(e.args)
        globals.logger.debug(traceback.format_exc())
        raise


def get_role_name(kind_role):
    """正規表現で一致するロールを取得する Get a matching role in a regular expression

    Args:
        kind_role (str): ロールの種類 role kind

    Returns:
        str: role name
    """

    try:
        roles = [
            const.ROLE_WS_OWNER[0],
            const.ROLE_WS_MANAGER[0],
            const.ROLE_WS_MEMBER_MG[0],
            const.ROLE_WS_CI_SETTING[0],
            const.ROLE_WS_CI_RESULT[0],
            const.ROLE_WS_CD_SETTING[0],
            const.ROLE_WS_CD_EXECUTE[0],
            const.ROLE_WS_CD_RESULT[0],
        ]

        ret_role = None
        for role in roles:
            # 正規表現を使って、role名を判断する Use regular expressions to determine role names
            ex_role = re.match("ws-({}|\d+)-(.+)", role)
            if ex_role[2] == kind_role:
                ret_role = role
                break

        return ret_role

    except Exception:
        raise

def get_role_kind(role_name):
    """正規表現で一致するロール種類を取得する Get the matching role type in a regular expression

    Args:
        role_name (str): ロール role name

    Returns:
        str: role kind name
    """

    try:
        roles = [
            const.ROLE_WS_OWNER[0],
            const.ROLE_WS_MANAGER[0],
            const.ROLE_WS_MEMBER_MG[0],
            const.ROLE_WS_CI_SETTING[0],
            const.ROLE_WS_CI_RESULT[0],
            const.ROLE_WS_CD_SETTING[0],
            const.ROLE_WS_CD_EXECUTE[0],
            const.ROLE_WS_CD_RESULT[0],
        ]

        ret_kind = None
        for role in roles:
            # 正規表現を使って、role名を判断する Use regular expressions to determine role names
            ex_role_src = re.match("ws-({}|\d+)-(.+)", role_name)
            ex_role = re.match("ws-({}|\d+)-(.+)", role)
            if ex_role[2] == ex_role_src[2]:
                ret_kind = ex_role[2]
                break

        return ret_kind

    except Exception:
        raise


def get_role_info(role_name):
    """正規表現で一致するロール情報を取得する Get the matching role info. in a regular expression

    Args:
        role_name (str): ロール role name

    Returns:
        str: role kind name
    """

    try:
        roles = [
            const.ROLE_WS_OWNER,
            const.ROLE_WS_MANAGER,
            const.ROLE_WS_MEMBER_MG,
            const.ROLE_WS_CI_SETTING,
            const.ROLE_WS_CI_RESULT,
            const.ROLE_WS_CD_SETTING,
            const.ROLE_WS_CD_EXECUTE,
            const.ROLE_WS_CD_RESULT,
        ]

        ret_info = None
        for role in roles:
            # 正規表現を使って、role名を判断する Use regular expressions to determine role names
            ex_role_src = re.match("ws-({}|\d+)-(.+)", role_name)
            ex_role = re.match("ws-({}|\d+)-(.+)", role[0])
            if ex_role[2] == ex_role_src[2]:
                ret_info = role
                break

        return ret_info

    except Exception:
        raise
