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
import requests
import schedule

import globals
import common
import const

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
        cd_status_in = "{}.{}.{}".format(const.CD_STATUS_ITA_COMPLETE, const.CD_STATUS_ARGOCD_SYNC, const.CD_STATUS_ARGOCD_PROCESSING) 

        # cd-result get
        api_url = "{}://{}:{}/cd/result?cd_status_in={}".format(os.environ['EPOCH_RS_CD_RESULT_PROTOCOL'],
                                                os.environ['EPOCH_RS_CD_RESULT_HOST'],
                                                os.environ['EPOCH_RS_CD_RESULT_PORT'],
                                                cd_status_in)
        response = requests.get(api_url)

        if response.status_code != 200:
            raise Exception("cd result get error:[{}]".format(response.status_code))

        ret = json.loads(response.text)
        result_rows = ret["rows"]

        # 明細数分処理する Process for the number of items
        for result_row in result_rows:
            globals.logger.debug("cd-result workspace_id:[{}] cd_result_id:[{}] cd_status:[{}]".format(result_row["workspace_id"], result_row["cd_result_id"], result_row["cd_status"]))

            # ITAの同期が完了したら、ArgoCDのSyncを呼び出す
            # Call ArgoCD Sync when ITA sync is complete
            if result_row["cd_status"] == const.CD_STATUS_ITA_COMPLETE:
                # 状態をArgoCD同期中に変更
                contents = json.loads(result_row["contents"])

                # ArgoCD Sync call 
                api_url = "{}://{}:{}/workspace/{}/argocd/sync/{}".format(os.environ['EPOCH_CONTROL_ARGOCD_PROTOCOL'],
                                                        os.environ['EPOCH_CONTROL_ARGOCD_HOST'],
                                                        os.environ['EPOCH_CONTROL_ARGOCD_PORT'],
                                                        result_row["workspace_id"],
                                                        contents["environment_name"])
                response = requests.post(api_url, headers=post_headers)

                if response.status_code != 200:
                    raise Exception("argocd sync post error:[{}]".format(response.status_code))

                # 状態をArgoCD同期中に変更
                post_data = {
                    "cd_status": const.CD_STATUS_ARGOCD_SYNC,
                }

                # cd-result put
                api_url = "{}://{}:{}/workspace/{}/cd/result/{}".format(os.environ['EPOCH_RS_CD_RESULT_PROTOCOL'],
                                                        os.environ['EPOCH_RS_CD_RESULT_HOST'],
                                                        os.environ['EPOCH_RS_CD_RESULT_PORT'],
                                                        result_row["workspace_id"],
                                                        result_row["cd_result_id"])
                response = requests.put(api_url, headers=post_headers, data=json.dumps(post_data))

                if response.status_code != 200:
                    raise Exception("cd result put error:[{}]".format(response.status_code))

            else:
                # ArgoCDの結果を取得して、状態を確認する
                # Get the result of ArgoCD and check the status
                contents = json.loads(result_row["contents"])

                # ArgoCD app get call 
                api_url = "{}://{}:{}/workspace/{}/argocd/app/{}".format(os.environ['EPOCH_CONTROL_ARGOCD_PROTOCOL'],
                                                        os.environ['EPOCH_CONTROL_ARGOCD_HOST'],
                                                        os.environ['EPOCH_CONTROL_ARGOCD_PORT'],
                                                        result_row["workspace_id"],
                                                        contents["environment_name"])
                response = requests.get(api_url)

                if response.status_code != 200:
                    raise Exception("argocd app get error:[{}]".format(response.status_code))

                # 戻り値を取得 Get the return value
                ret_argocd_app = json.loads(response.text)
                globals.logger.debug("argocd result [{}]".format(ret_argocd_app))

                # ArgoCDの戻り値が正常化どうかチェックして該当のステータスを設定
                # Check if the return value of ArgoCD is normal and set the corresponding status
                if ret_argocd_app["result"]["status"]["health"]["status"] == const.ARGOCD_HEALTH_STATUS_HEALTHY:
                    cd_status = const.CD_STATUS_ARGOCD_SYNCED
                elif ret_argocd_app["result"]["status"]["health"]["status"] == ARGOCD_HEALTH_STATUS_DEGRADED:
                    cd_status = const.CD_STATUS_ARGOCD_FAILED
                elif ret_argocd_app["result"]["status"]["health"]["status"] == ARGOCD_HEALTH_STATUS_PROGRESSING:
                    cd_status = const.CD_STATUS_ARGOCD_PROCESSING
                elif ret_argocd_app["result"]["status"]["health"]["status"] == ARGOCD_HEALTH_STATUS_SUSPENDED:
                    cd_status = const.CD_STATUS_ARGOCD_FAILED
                elif ret_argocd_app["result"]["status"]["health"]["status"] == ARGOCD_HEALTH_STATUS_MISSING:
                    cd_status = const.CD_STATUS_ARGOCD_FAILED
                else:
                    cd_status = const.CD_STATUS_ARGOCD_FAILED

                # 変更したい項目のみ設定（cd_statusは必須）
                # Set only the items you want to change (cd_status is required)
                post_data = {
                    "cd_status": cd_status,
                    "argocd_results": ret_argocd_app,
                }

                # cd-result put
                api_url = "{}://{}:{}/workspace/{}/cd/result/{}".format(os.environ['EPOCH_RS_CD_RESULT_PROTOCOL'],
                                                        os.environ['EPOCH_RS_CD_RESULT_HOST'],
                                                        os.environ['EPOCH_RS_CD_RESULT_PORT'],
                                                        result_row["workspace_id"],
                                                        result_row["cd_result_id"])
                response = requests.put(api_url, headers=post_headers, data=json.dumps(post_data))

                if response.status_code != 200:
                    raise Exception("cd result put error:[{}]".format(response.status_code))

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
        cd_status_in = "{}.{}.{}".format(const.CD_STATUS_START, const.CD_STATUS_ITA_RESERVE, const.CD_STATUS_ITA_EXECUTE) 

        # cd-result get
        api_url = "{}://{}:{}/cd/result?cd_status_in={}".format(os.environ['EPOCH_RS_CD_RESULT_PROTOCOL'],
                                                os.environ['EPOCH_RS_CD_RESULT_HOST'],
                                                os.environ['EPOCH_RS_CD_RESULT_PORT'],
                                                cd_status_in)
        response = requests.get(api_url)

        if response.status_code != 200:
            raise Exception("cd result get error:[{}]".format(response.status_code))

        ret = json.loads(response.text)
        result_rows = ret["rows"]

        # 明細数分処理する Process for the number of items
        for result_row in result_rows:
            globals.logger.debug("cd-result workspace_id:[{}] cd_result_id:[{}] cd_status:[{}]".format(result_row["workspace_id"], result_row["cd_result_id"], result_row["cd_status"]))
            
            # ダミー処理　⇒　無条件でCD_STATUS_ITA_COMPLETEへ
            if True:
                post_data = json.loads(result_row["contents"])
                #globals.logger.debug(post_data)
                # post_data["cd_status"] = const.CD_STATUS_ITA_COMPLETE
                post_data = {
                    "cd_status": const.CD_STATUS_ITA_COMPLETE
                }

                # cd-result put
                api_url = "{}://{}:{}/workspace/{}/cd/result/{}".format(os.environ['EPOCH_RS_CD_RESULT_PROTOCOL'],
                                                        os.environ['EPOCH_RS_CD_RESULT_HOST'],
                                                        os.environ['EPOCH_RS_CD_RESULT_PORT'],
                                                        result_row["workspace_id"],
                                                        result_row["cd_result_id"])
                response = requests.put(api_url, headers=post_headers, data=json.dumps(post_data))

                if response.status_code != 200:
                    raise Exception("cd result put error:[{}]".format(response.status_code))

    except Exception as e:
        return common.serverError(e)



def main():
    """CD結果 モニタリング CD result monitoring
    """

    try:
        argocd_interval_sec = int(os.environ["EPOCH_MONITORING_ARGOCD_INTERVAL_SEC"])
        ita_interval_sec = int(os.environ["EPOCH_MONITORING_ITA_INTERVAL_SEC"])

        schedule.every(argocd_interval_sec).seconds.do(monitoring_argo_cd)
        schedule.every(ita_interval_sec).seconds.do(monitoring_it_automation)

        while True:
            schedule.run_pending()
            time.sleep(1)

    except Exception as e:
        return common.serverError(e)

if __name__ == "__main__":
    main()
