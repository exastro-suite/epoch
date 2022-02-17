#   Copyright 2021 NEC Corporation
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

import sys

# ロール定義 Role definition
ROLE_WS_OWNER = [ "ws-{}-owner", "EP000-0001", "オーナー", 1 ]
ROLE_WS_MANAGER = [ "ws-{}-manager", "EP000-0002", "管理者", 2 ]
ROLE_WS_MEMBER_MG = [ "ws-{}-member-mg", "EP000-0003", "メンバー管理", 3 ]
ROLE_WS_CI_SETTING = [ "ws-{}-ci-setting", "EP000-0004", "CI設定", 4 ]
ROLE_WS_CI_RESULT = [ "ws-{}-ci-result", "EP000-0005", "CI確認", 5 ]
ROLE_WS_CD_SETTING = [ "ws-{}-cd-setting", "EP000-0006", "CD設定", 6 ]
ROLE_WS_CD_EXECUTE = [ "ws-{}-cd-execute", "EP000-0007", "CD実行", 7 ]
ROLE_WS_CD_RESULT = [ "ws-{}-cd-result", "EP000-0008", "CD確認", 8 ]

# ロール権限 Role authority
ROLE_WS_ROLE_WS_REFERENCE = [ "ws-{}-role-ws-reference", "EP000-0010", "ワークスペース参照", 1 ]
ROLE_WS_ROLE_WS_NAME_UPDATE = [ "ws-{}-role-ws-name-update", "EP000-0011", "ワークスペース更新(名称)", 2 ]
ROLE_WS_ROLE_WS_CI_UPDATE = [ "ws-{}-role-ws-ci-update", "EP000-0012", "ワークスペース更新 (CI)", 3 ]
ROLE_WS_ROLE_WS_CD_UPDATE = [ "ws-{}-role-ws-cd-update", "EP000-0013", "ワークスペース更新 (CD)", 4 ]
ROLE_WS_ROLE_WS_DELETE = [ "ws-{}-role-ws-delete", "EP000-0014", "ワークスペース削除", 5 ]
ROLE_WS_ROLE_OWNER_ROLE_SETTING = [ "ws-{}-role-owner-role-setting", "EP000-0015", "オーナーロール設定", 6 ]
ROLE_WS_ROLE_MEMBER_ADD = [ "ws-{}-role-member-add", "EP000-0016", "メンバー追加", 7 ]
ROLE_WS_ROLE_MEMBER_ROLE_UPDATE = [ "ws-{}-role-member-role-update", "EP000-0017", "ロール変更", 8 ]
ROLE_WS_ROLE_CI_PIPELINE_RESULT = [ "ws-{}-role-ci-pipeline-result", "EP000-0018", "CIパイプライン結果確認", 9 ]
ROLE_WS_ROLE_MANIFEST_UPLOAD = [ "ws-{}-role-manifest-upload", "EP000-0019", "Manifestテンプレートアップロード", 10 ]
ROLE_WS_ROLE_MANIFEST_SETTING = [ "ws-{}-role-manifest-setting", "EP000-0026", "Manifestパラメータ編集", 11 ]
ROLE_WS_ROLE_CD_EXECUTE = [ "ws-{}-role-cd-execute", "EP000-0020", "CD実行", 12 ]
ROLE_WS_ROLE_CD_EXECUTE_RESULT = [ "ws-{}-role-cd-execute-result", "EP000-0021", "CD実行結果確認", 13 ]

ALL_ROLES = [
    ROLE_WS_OWNER[0],
    ROLE_WS_MANAGER[0],
    ROLE_WS_MEMBER_MG[0],
    ROLE_WS_CI_SETTING[0],
    ROLE_WS_CI_RESULT[0],
    ROLE_WS_CD_SETTING[0],
    ROLE_WS_CD_EXECUTE[0],
    ROLE_WS_CD_RESULT[0],
]

# ログの種類 Log kind
LOG_KIND_ERROR='Error'
LOG_KIND_INFO='Infomation'
LOG_KIND_UPDATE='Update'

# 状態の種類 Log kind
STATUS_INITIALIZE='initialize'
STATUS_POD='pod'
STATUS_CI_SETTING='ci_setting'
STATUS_CD_SETTING='cd_setting'

STATUS_OK="OK"
STATUS_NG="NG"

WORKSPACE_STATUS = {
    STATUS_INITIALIZE : "",
    STATUS_POD : "",
    STATUS_CI_SETTING : "",
    STATUS_CD_SETTING : "",
}

CD_STATUS_START = "Start"
CD_STATUS_ITA_RESERVE = "ITA-Reserve"
CD_STATUS_ITA_EXECUTE = "ITA-Execute"
CD_STATUS_ITA_FAILED = "ITA-Failed"
CD_STATUS_ITA_COMPLETE = "ITA-Complete"
CD_STATUS_ARGOCD_SYNC = "ArgoCD-Sync"
CD_STATUS_ARGOCD_PROCESSING = "ArgoCD-Processing"
CD_STATUS_ARGOCD_FAILED = "ArgoCD-Failed"
CD_STATUS_ARGOCD_SYNCED = "ArgoCD-Synced"
CD_STATUS_CANCEL = "Cancel"

HOUSING_INNER = "inner"
HOUSING_OUTER = "outer"