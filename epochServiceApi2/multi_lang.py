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

from ja import text_list


def get_text(text_id, origin_text, *args):
    """テキスト取得

    Args:
        text_id (str): text id
        origin_text (str): 原文
        args: {0}, {1}..に埋め込むパラメータ

    Returns:
        text: 変換後のテキスト
    """
    
    try:
        text = ""
        
        # text_id存在チェック
        if(text_id in text_list.TextList.lang_array): 
            text = (text_list.TextList.lang_array[text_id])

            i=0
            
            for arg in args:
                # {0}, {1}..に埋め込む変数を第3引数以降（args）で指定した文字列に置き換える
                text = text.replace("{" + str(i) + "}", arg)
                i += 1
                
        else: 
            # text_idが存在しない場合は、原文を表示
            text = origin_text

        return text
    
    except Exception as e:
        return origin_text
