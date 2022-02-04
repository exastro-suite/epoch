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

from flask import jsonify
import random, string
import json

import globals

def delete_dictKey(dictobj, key):
    """Dictionary Key削除 Dictionary Key deleted

    Args:
        dictobj (dict): Dictionary
        key (any): key
    """
    if key in dictobj:
        del dictobj[key]

def random_string(n):
    """ランダム文字列生成 Random string generation

    Args:
        n (int): 文字数

    Returns:
        str: ランダム文字列
    """
    return ''.join(random.choices(string.ascii_letters + string.digits, k=n))


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


def json_value(str_json):
    """json値の値変換 Value conversion of json value

    Args:
        str_json (json): json strings

    Returns:
        str: strings value
    """
    # json値の場合は、json_dumpsで変換する
    # For json value, convert with json_dumps
    if type(str_json) is dict:
        return json.dumps(str_json)
    else:
        return str_json

def server_error(e, message=''):
    """サーバーエラーレスポンス

    Args:
        e (Exception): 例外

    Returns:
        response: HTTP Response (HTTP-500)
    """
    import traceback
    
    globals.logger.error('message : {}'.format(message))
    globals.logger.error(''.join(list(traceback.TracebackException.from_exception(e).format())))

    return jsonify(
        {
            'result':       '500',
            'message':      message,
            'exception':    ''.join(list(traceback.TracebackException.from_exception(e).format())),
        }
    ), 500

