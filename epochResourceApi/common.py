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


def serverError(e):
    """レーバーエラーレスポンス

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

