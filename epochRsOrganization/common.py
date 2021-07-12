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

import globals

def deleteDictKey(dictobj, key):
    """Dictionary Key削除

    Args:
        dictobj (dict): Dictionary
        key (any): key
    """
    if key in dictobj:
        del dictobj[key]

def randomString(n):
    """ランダム文字列生成

    Args:
        n (int): 文字数

    Returns:
        str: ランダム文字列
    """
    return ''.join(random.choices(string.ascii_letters + string.digits, k=n))


def serverError(e, message=''):
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

