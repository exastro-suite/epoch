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

CD_STATUS_START="Start"
CD_STATUS_ITA_RESERVE="ITA-Reserve"
CD_STATUS_ITA_EXECUTE="ITA-Execute"
CD_STATUS_ITA_FAILED="ITA-Failed"
CD_STATUS_ITA_COMPLETE="ITA-Complete"
CD_STATUS_ITA_EMERGENCY="ITA-Emergency"
CD_STATUS_ARGOCD_SYNC="ArgoCD-Sync"
CD_STATUS_ARGOCD_PROCESSING="ArgoCD-Processing"
CD_STATUS_ARGOCD_FAILED="ArgoCD-Failed"
CD_STATUS_ARGOCD_SYNCED="ArgoCD-Synced"
CD_STATUS_CANCEL="Cancel"

ARGOCD_HEALTH_STATUS_HEALTHY = "Healthy"
ARGOCD_HEALTH_STATUS_DEGRADED = "Degraded"
ARGOCD_HEALTH_STATUS_PROGRESSING = "Progressing"
ARGOCD_HEALTH_STATUS_SUSPENDED = "Suspended"
ARGOCD_HEALTH_STATUS_MISSING = "Missing"
ARGOCD_HEALTH_STATUS_UNKNOWN = "Unknown"

HOUSING_INNER = "inner"
HOUSING_OUTER = "outer"

# ITAの結果ステータス IT-Automation result status
ITA_STATUS_ID_NOT_EXECUTED  = "1"  # 未実行 Not executed
ITA_STATUS_ID_RESERVED      = "2"  # 未実行(予約) Not executed (reserved)
ITA_STATUS_ID_EXECUTING     = "3"  # 実行中 executing
ITA_STATUS_ID_EXEC_DELAY    = "4"  # 実行中(遅延) executing delay
ITA_STATUS_ID_COMPLETE      = "5"  # 正常終了 Successful completion
ITA_STATUS_ID_EMERGENCY     = "6"  # 緊急停止 Emergency stop
ITA_STATUS_ID_ABNORMAL_END  = "7"  # 異常終了 Abnormal termination
ITA_STATUS_ID_UNEXPECTED    = "8"  # 想定外エラー Unexpected error
ITA_STATUS_ID_CANCEL        = "9"  # 予約取消 Cancellation of reservation
ITA_STATUS_ID_WARNING       = "11" # 警告終了 Warning end