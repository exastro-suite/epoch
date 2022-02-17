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
import urllib.parse
import requests
import schedule

import globals
import common
import const

# エラー時のリトライ回数(0は止めない) Number of retries on error (0 does not stop)
ARGOCD_ERROR_RETRY_COUNT = 0
global_argocd_error_count = 0
ITA_ERROR_RETRY_COUNT = 0
global_ita_error_count = 0

# 設定ファイル読み込み・globals初期化
app = Flask(__name__)
app.config.from_envvar('CONFIG_API_MONITORING_CD_PATH')
globals.init(app)

def monitoring_argo_cd():
    """Argo CD 監視

    Returns:
        None
    """

    global global_argocd_error_count
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

        error_exists = False
        # 明細数分処理する Process for the number of items
        for result_row in result_rows:
            # 繰り返し中のUserExceptionは、データを全件処理するため無視する
            # UserException during repetition is ignored because all data is processed.
            try:
                globals.logger.debug("cd-result workspace_id:[{}] cd_result_id:[{}] cd_status:[{}]".format(result_row["workspace_id"], result_row["cd_result_id"], result_row["cd_status"]))

                # ITAの同期が完了したら、ArgoCDのSyncを呼び出す
                # Call ArgoCD Sync when ITA sync is complete
                if result_row["cd_status"] == const.CD_STATUS_ITA_COMPLETE:
                    # 状態をArgoCD同期中に変更
                    contents = json.loads(result_row["contents"])

                    # ArgoCD Sync call 
                    api_url = "{}://{}:{}/workspace/{}/argocd/app/{}/sync".format(os.environ['EPOCH_CONTROL_ARGOCD_PROTOCOL'],
                                                            os.environ['EPOCH_CONTROL_ARGOCD_HOST'],
                                                            os.environ['EPOCH_CONTROL_ARGOCD_PORT'],
                                                            result_row["workspace_id"],
                                                            contents["environment_name"])
                    response = requests.post(api_url, headers=post_headers)

                    if response.status_code != 200:
                        raise common.UserException("argocd sync post error:[{}]".format(response.status_code))

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
                        raise common.UserException("cd result put error:[{}]".format(response.status_code))

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
                        raise common.UserException("argocd app get error:[{}]".format(response.status_code))

                    # 戻り値を取得 Get the return value
                    ret_argocd_app = json.loads(response.text)
                    # globals.logger.debug("argocd result [{}]".format(ret_argocd_app))

                    # 対象のオブジェクトがあるかどうかチェックする
                    # Check if there is an object of interest
                    if "sync" not in ret_argocd_app["result"]["status"]:
                        continue
                    if "revision" not in ret_argocd_app["result"]["status"]["sync"]:
                        continue

                    # manifestのrivisionを元に該当のトレースIDの履歴かチェックする 
                    # Check if the history of the corresponding trace ID is based on the revision of the manifest
                    revision = ret_argocd_app["result"]["status"]["sync"]["revision"]
                    manifest_url = ret_argocd_app["result"]["status"]["sync"]["comparedTo"]["source"]["repoURL"]
                    git_token = contents["workspace_info"]["cd_config"]["environments_common"]["git_repositry"]["token"]

                    # ヘッダ情報 header info.
                    post_headers_in_token = {
                        'private-token': git_token,
                        'Content-Type': 'application/json',
                    }

                    if contents["workspace_info"]["cd_config"]["environments_common"]["git_repositry"]["housing"] == const.HOUSING_INNER:
                        # EPOCH内レジストリ Registry in EPOCH
                        api_url = "{}://{}:{}/commits/{}?git_url={}".format(os.environ['EPOCH_CONTROL_INSIDE_GITLAB_PROTOCOL'],
                                                                os.environ['EPOCH_CONTROL_INSIDE_GITLAB_HOST'],
                                                                os.environ['EPOCH_CONTROL_INSIDE_GITLAB_PORT'],
                                                                revision,
                                                                urllib.parse.quote(manifest_url))
                        response = requests.get(api_url, headers=post_headers_in_token)

                        if response.status_code != 200:
                            raise common.UserException("git commit get error:[{}]".format(response.status_code))

                        ret_git_commit = json.loads(response.text)

                        commit_message =  ret_git_commit["rows"]["message"]
                    else:
                        # GitHub commit get
                        api_url = "{}://{}:{}/commits/{}?git_url={}".format(os.environ['EPOCH_CONTROL_GITHUB_PROTOCOL'],
                                                                os.environ['EPOCH_CONTROL_GITHUB_HOST'],
                                                                os.environ['EPOCH_CONTROL_GITHUB_PORT'],
                                                                revision,
                                                                urllib.parse.quote(manifest_url))
                        response = requests.get(api_url, headers=post_headers_in_token)

                        if response.status_code != 200:
                            raise common.UserException("git commit get error:[{}]".format(response.status_code))

                        ret_git_commit = json.loads(response.text)
                        # globals.logger.debug("rows:[{}]".format(ret_git_commit["rows"]))

                        commit_message =  ret_git_commit["rows"]["commit"]["message"]

                    globals.logger.debug("trace_id:[{}] vs commit_message10[{}]".format(contents["trace_id"], commit_message[:10]))
                    # 上10桁が一致している場合のみステータスのチェックを行う
                    if contents["trace_id"] != commit_message[:10]:
                        continue 

                    # ArgoCDの戻り値が正常化どうかチェックして該当のステータスを設定
                    # Check if the return value of ArgoCD is normal and set the corresponding status
                    if ret_argocd_app["result"]["status"]["health"]["status"] == const.ARGOCD_HEALTH_STATUS_HEALTHY:
                        cd_status = const.CD_STATUS_ARGOCD_SYNCED
                    elif ret_argocd_app["result"]["status"]["health"]["status"] == const.ARGOCD_HEALTH_STATUS_DEGRADED:
                        cd_status = const.CD_STATUS_ARGOCD_FAILED
                    elif ret_argocd_app["result"]["status"]["health"]["status"] == const.ARGOCD_HEALTH_STATUS_PROGRESSING:
                        cd_status = const.CD_STATUS_ARGOCD_PROCESSING
                    elif ret_argocd_app["result"]["status"]["health"]["status"] == const.ARGOCD_HEALTH_STATUS_SUSPENDED:
                        cd_status = const.CD_STATUS_ARGOCD_FAILED
                    elif ret_argocd_app["result"]["status"]["health"]["status"] == const.ARGOCD_HEALTH_STATUS_MISSING:
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
                        raise common.UserException("cd result put error:[{}]".format(response.status_code))

            except common.UserException as e:
                error_exists = True
                global_argocd_error_count += 1
                globals.logger.debug("UserException error count [{}]".format(global_argocd_error_count))
                globals.logger.debug("UserException Exception error args [{}]".format(e.args))

        if not error_exists:
            # 正常時はエラーをリセット Reset error when normal
            global_argocd_error_count = 0

    except Exception as e:
        global_argocd_error_count += 1
        globals.logger.debug("argocd Exception error count [{}]".format(global_argocd_error_count))
        globals.logger.debug("argocd Exception error args [{}]".format(e.args))
        return common.serverError(e)



def monitoring_it_automation():
    """IT-Automation 監視

    Returns:
        None
    """

    global global_ita_error_count
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

        error_exists = False
        # 明細数分処理する Process for the number of items
        for result_row in result_rows:
            # 繰り返し中のUserExceptionは、データを全件処理するため無視する
            # UserException during repetition is ignored because all data is processed.
            try:
                globals.logger.debug("cd-result workspace_id:[{}] cd_result_id:[{}] cd_status:[{}]".format(result_row["workspace_id"], result_row["cd_result_id"], result_row["cd_status"]))

                workspace_id = result_row["workspace_id"]
                conductor_instance_id = int(result_row["cd_result_id"]) # インスタンスIDは、0埋め無しの数値 Instance ID is a number without 0 padding

                # ステータスが"Start"または"Reserve" or "Excute"の場合はITAから結果を取得する
                if result_row["cd_status"] == const.CD_STATUS_START or \
                    result_row["cd_status"] == const.CD_STATUS_ITA_RESERVE or \
                    result_row["cd_status"] == const.CD_STATUS_ITA_EXECUTE:

                    # cd-result get
                    api_url = "{}://{}:{}/workspace/{}/it-automation/cd/result/{}".format(os.environ['EPOCH_CONTROL_ITA_PROTOCOL'],
                                                                                            os.environ['EPOCH_CONTROL_ITA_HOST'],
                                                                                            os.environ['EPOCH_CONTROL_ITA_PORT'],
                                                                                            workspace_id,
                                                                                            conductor_instance_id)
                    response = requests.get(api_url)

                    if response.status_code != 200:
                        raise Exception("it-automation cd result get error:[{}]".format(response.status_code))

                    ret = json.loads(response.text)

                    globals.logger.debug("it-automation cd-result workspace_id:[{}] cd_result_id:[{}] ret[{}]".format(result_row["workspace_id"], result_row["cd_result_id"], ret))

                    ita_rows = ret["rows"]["resultdata"]

                    # ステータスIDが存在する場合のみ処理
                    # Process only if status ID exists
                    if "STATUS_ID" in ita_rows["CONDUCTOR_INSTANCE_INFO"]:
                        # 実行中になった場合は、実行中のステータスに更新
                        # If it becomes running, update to running status
                        if ita_rows["CONDUCTOR_INSTANCE_INFO"]["STATUS_ID"] == const.ITA_STATUS_ID_EXECUTING or \
                            ita_rows["CONDUCTOR_INSTANCE_INFO"]["STATUS_ID"] == const.ITA_STATUS_ID_EXEC_DELAY:
                            cd_status = const.CD_STATUS_ITA_EXECUTE
                        # 予約中になった場合は、予約中のステータスに更新
                        # If it is reserved, it will be updated to the reserved status.
                        elif ita_rows["CONDUCTOR_INSTANCE_INFO"]["STATUS_ID"] == const.ITA_STATUS_ID_RESERVED:
                            cd_status = const.CD_STATUS_ITA_RESERVE
                        # 緊急停止された場合は、緊急停止のステータスに更新
                        # In case of emergency stop, update to emergency stop status
                        elif ita_rows["CONDUCTOR_INSTANCE_INFO"]["STATUS_ID"] == const.ITA_STATUS_ID_EMERGENCY:
                            cd_status = const.CD_STATUS_ITA_EMERGENCY
                        # 正常終了した場合は、正常終了のステータスに更新
                        # If it ends normally, it will be updated to the status of normal end.
                        elif ita_rows["CONDUCTOR_INSTANCE_INFO"]["STATUS_ID"] == const.ITA_STATUS_ID_COMPLETE:
                            cd_status = const.CD_STATUS_ITA_COMPLETE
                        # 予約取消となった場合は、キャンセルのステータスに更新
                        # If the reservation is canceled, it will be updated to the cancellation status.
                        elif ita_rows["CONDUCTOR_INSTANCE_INFO"]["STATUS_ID"] == const.ITA_STATUS_ID_CANCEL:
                            cd_status = const.CD_STATUS_CANCEL
                        # 異常終了・想定外エラー・警告終了した場合は、失敗のステータスに更新
                        # Abnormal termination / unexpected error / warning If terminated, update to failure status
                        elif ita_rows["CONDUCTOR_INSTANCE_INFO"]["STATUS_ID"] == const.ITA_STATUS_ID_ABNORMAL_END or \
                            ita_rows["CONDUCTOR_INSTANCE_INFO"]["STATUS_ID"] == const.ITA_STATUS_ID_UNEXPECTED or \
                            ita_rows["CONDUCTOR_INSTANCE_INFO"]["STATUS_ID"] == const.ITA_STATUS_ID_WARNING:
                            cd_status = const.CD_STATUS_ITA_FAILED
                        # 未実行の場合は、なにもしない更新
                        # If not executed, update without doing anything
                        elif ita_rows["CONDUCTOR_INSTANCE_INFO"]["STATUS_ID"] == const.ITA_STATUS_ID_NOT_EXECUTED:
                            cd_status = result_row["cd_status"]
                        else:
                            # 上記以外はエラー
                            # Errors other than the abov
                            cd_status = const.CD_STATUS_ITA_FAILED
                    else:
                        # 取得失敗 Acquisition failure
                        cd_status = const.CD_STATUS_ITA_FAILED

                    # ステータスが更新されたら更新
                    # Update when status is updated
                    if cd_status != result_row["cd_status"]:
                        post_data = json.loads(result_row["contents"])
                        #globals.logger.debug(post_data)
                        # post_data["cd_status"] = const.CD_STATUS_ITA_COMPLETE
                        post_data = {
                            "cd_status": const.CD_STATUS_ITA_COMPLETE,
                            "ita_results": ita_rows,
                        }

                        # cd-result put
                        api_url = "{}://{}:{}/workspace/{}/cd/result/{}".format(os.environ['EPOCH_RS_CD_RESULT_PROTOCOL'],
                                                                os.environ['EPOCH_RS_CD_RESULT_HOST'],
                                                                os.environ['EPOCH_RS_CD_RESULT_PORT'],
                                                                result_row["workspace_id"],
                                                                result_row["cd_result_id"])
                        response = requests.put(api_url, headers=post_headers, data=json.dumps(post_data))

                        if response.status_code != 200:
                            raise common.UserException("cd result put error:[{}]".format(response.status_code))

            except common.UserException as e:
                error_exists = True
                global_ita_error_count += 1
                globals.logger.debug("UserException error count [{}]".format(global_ita_error_count))
                globals.logger.debug("UserException Exception error args [{}]".format(e.args))

        if not error_exists:
            # 正常時はエラーをリセット Reset error when normal
            global_ita_error_count = 0

    except Exception as e:
        global_ita_error_count += 1
        globals.logger.debug("it-automation Exception error count [{}]".format(global_ita_error_count))
        globals.logger.debug("it-automation Exception error args [{}]".format(e.args))
        return common.serverError(e)



def main():
    """CD結果 モニタリング CD result monitoring
    """

    global global_argocd_error_count
    global global_ita_error_count
    try:
        argocd_interval_sec = int(os.environ["EPOCH_MONITORING_ARGOCD_INTERVAL_SEC"])
        ita_interval_sec = int(os.environ["EPOCH_MONITORING_ITA_INTERVAL_SEC"])

        ARGOCD_ERROR_RETRY_COUNT = int(os.environ["EPOCH_MONITORING_ARGOCD_ERROR_RETRY_COUNT"])
        ITA_ERROR_RETRY_COUNT = int(os.environ["EPOCH_MONITORING_ITA_ERROR_RETRY_COUNT"]) 
        global_argocd_error_count = 0
        global_ita_error_count = 0

        schedule.every(argocd_interval_sec).seconds.do(monitoring_argo_cd)
        schedule.every(ita_interval_sec).seconds.do(monitoring_it_automation)

        while True:
            schedule.run_pending()

            # エラーリトライ回数超えた場合は、終了する
            # If the number of error retries is exceeded, the process will end.
            if ARGOCD_ERROR_RETRY_COUNT != 0 and global_argocd_error_count > ARGOCD_ERROR_RETRY_COUNT:
                break

            if ITA_ERROR_RETRY_COUNT != 0 and global_ita_error_count > ITA_ERROR_RETRY_COUNT:
                break

            time.sleep(1)

    except Exception as e:
        return common.serverError(e)

if __name__ == "__main__":
    main()
