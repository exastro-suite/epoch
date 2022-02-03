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

from flask import Flask
from datetime import datetime
import inspect
import os
import json
import tempfile
import subprocess
import time
import re
import base64
import traceback
from datetime import timedelta, timezone
import sched

import globals
import common

# 設定ファイル読み込み・globals初期化
app = Flask(__name__)
app.config.from_envvar('CONFIG_API_MONITORING_CD_PATH')
globals.init(app)

def monitoring_argo_cd():
    """Argo CD 監視

    Returns:
        None
    """

    try:
        globals.logger.debug("monitoring argo cd!")

        # ヘッダ情報 header info.
        post_headers = {
            'Content-Type': 'application/json',
        }

        # ArgoCDの監視する状態は、ITA完了, ArgoCD同期中、ArgoCD処理中とする
        # The monitoring status of IT-Automation is CD execution start, ITA reservation, and ITA execution.
        cd_status_in = const.CD_STATUS_ITA_COMPLETE + "," + const.CD_STATUS_ARGOCD_SYNC + "," + const.CD_STATUS_ARGOCD_PROCESSING 

        # cd-result get
        api_url = "{}://{}:{}/cd/result?cd_status_in={}".format(os.environ['EPOCH_RS_CD_RESULT_PROTOCOL'],
                                                os.environ['EPOCH_RS_CD_RESULT_HOST'],
                                                os.environ['EPOCH_RS_CD_RESULT_PORT'],
                                                cd_status_in)
        response = requests.get(api_url)

        if response.status_code != 200:
            raise Exception("cd result get error:[{}]".format(response.status_cd))

        ret = json.loads(response.text)
        result_rows = ret["rows"]

        # 明細数分処理する Process for the number of items
        for result_row in result_rows:
            globals.logger.debug("cd-result workspace_id:[{}] cd_result_id:[{}] cd_status:[{}]".format(result_row["workspace_id"], result_row["cd_result_id"], result_row["cd_status"]))

            # ITAの同期が完了したら、ArgoCDのSyncを呼び出す
            # Call ArgoCD Sync when ITA sync is complete
            if result_row["cd_status"] == const.CD_STATUS_ITA_COMPLETE:
                # ArgoCD Sync call 

                # 状態をArgoCD同期中に変更
                post_data = result_row["contents"]
                post_data["cd_status"] = const.CD_STATUS_ARGOCD_SYNC

                # cd-result put
                api_url = "{}://{}:{}/workspace/{}/cd/result/{}".format(os.environ['EPOCH_RS_CD_RESULT_PROTOCOL'],
                                                        os.environ['EPOCH_RS_CD_RESULT_HOST'],
                                                        os.environ['EPOCH_RS_CD_RESULT_PORT'],
                                                        result_row["workspace_id"],
                                                        result_row["cd_result_id"])
                response = requests.put(api_url, headers=post_headers, data=json.dumps(post_data))

                if response.status_code != 200:
                    raise Exception("cd result put error:[{}]".format(response.status_cd))

            else:
                # ArgoCDの結果を取得して、状態を確認する
                # Get the result of ArgoCD and check the status


                # cd-result put
                api_url = "{}://{}:{}/workspace/{}/cd/result/{}".format(os.environ['EPOCH_RS_CD_RESULT_PROTOCOL'],
                                                        os.environ['EPOCH_RS_CD_RESULT_HOST'],
                                                        os.environ['EPOCH_RS_CD_RESULT_PORT'],
                                                        result_row["workspace_id"],
                                                        result_row["cd_result_id"])
                response = requests.put(api_url, headers=post_headers, data=json.dumps(post_data))

                if response.status_code != 200:
                    raise Exception("cd result put error:[{}]".format(response.status_cd))

    except Exception as e:
        return common.serverError(e)



def monitoring_it_automation():
    """IT-Automation 監視

    Returns:
        None
    """

    try:
        globals.logger.debug("monitoring it-automation!")

        # ヘッダ情報 header info.
        post_headers = {
            'Content-Type': 'application/json',
        }

        # IT-Automationの監視する状態は、CD実行開始, ITA予約、ITA実行中とする
        # The monitoring status of IT-Automation is CD execution start, ITA reservation, and ITA execution.
        cd_status_in = const.CD_STATUS_START + "," + const.CD_STATUS_ITA_RESERVE + "," + const.CD_STATUS_ITA_EXECUTE 

        # cd-result get
        api_url = "{}://{}:{}/cd/result?cd_status_in={}".format(os.environ['EPOCH_RS_CD_RESULT_PROTOCOL'],
                                                os.environ['EPOCH_RS_CD_RESULT_HOST'],
                                                os.environ['EPOCH_RS_CD_RESULT_PORT'],
                                                cd_status_in)
        response = requests.get(api_url)

        if response.status_code != 200:
            raise Exception("cd result get error:[{}]".format(response.status_cd))

        ret = json.loads(response.text)
        result_rows = ret["rows"]

        # 明細数分処理する Process for the number of items
        for result_row in result_rows:
            globals.logger.debug("cd-result workspace_id:[{}] cd_result_id:[{}] cd_status:[{}]".format(result_row["workspace_id"], result_row["cd_result_id"], result_row["cd_status"]))
            
            # ダミー処理　⇒　無条件でCD_STATUS_ITA_COMPLETEへ
            if True:
                post_data = result_row["contents"]
                post_data["cd_status"] = const.CD_STATUS_ITA_COMPLETE

                # cd-result put
                api_url = "{}://{}:{}/workspace/{}/cd/result/{}".format(os.environ['EPOCH_RS_CD_RESULT_PROTOCOL'],
                                                        os.environ['EPOCH_RS_CD_RESULT_HOST'],
                                                        os.environ['EPOCH_RS_CD_RESULT_PORT'],
                                                        result_row["workspace_id"],
                                                        result_row["cd_result_id"])
                response = requests.put(api_url, headers=post_headers, data=json.dumps(post_data))

                if response.status_code != 200:
                    raise Exception("cd result put error:[{}]".format(response.status_cd))

    except Exception as e:
        return common.serverError(e)



def main():
    """CD結果 モニタリング CD result monitoring
    """

    try:
        argocd_interval_sec = os.environ["EPOCH_MONITORING_ARGOCD_INTERVAL_SEC"]
        ita_interval_sec = os.environ["EPOCH_MONITORING_ITA_INTERVAL_SEC"]

        schedule.every(interval_sec).seconds.do(monitoring_argo_cd)
        schedule.every(interval_sec).seconds.do(ita_interval_sec)

        while True:
            schedule.run_pending()
            time.sleep(1)

    except Exception as e:
        return common.serverError(e)

if __name__ == "__main__":
    main()
