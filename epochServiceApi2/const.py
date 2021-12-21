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
ROLE_WS_OWNER = [ "ws-{}-owner", "EP000-0001", "オーナー" ]
ROLE_WS_MANAGER = [ "ws-{}-manager", "EP000-0002", "管理者" ]
ROLE_WS_MEMBER_MG = [ "ws-{}-member-mg", "EP000-0003", "メンバー管理" ]
ROLE_WS_CI_SETTING = [ "ws-{}-ci-setting", "EP000-0004", "CI設定" ]
ROLE_WS_CI_RESULT = [ "ws-{}-ci-result", "EP000-0005", "CI確認" ]
ROLE_WS_CD_SETTING = [ "ws-{}-cd-setting", "EP000-0006", "CD設定" ]
ROLE_WS_CD_EXECUTE = [ "ws-{}-cd-execute", "EP000-0007", "CD実行" ]
ROLE_WS_CD_RESULT = [ "ws-{}-cd-result", "EP000-0008", "CD確認" ]

# ロール権限 Role authority
ROLE_WS_ROLE_WS_REFERENCE = [ "ws-{}-role-ws-reference", "EP000-0010", "ワークスペース参照" ]
ROLE_WS_ROLE_WS_NAME_UPDATE = [ "ws-{}-role-ws-name-update", "EP000-0011", "ワークスペース更新(名称)" ]
ROLE_WS_ROLE_WS_CI_UPDATE = [ "ws-{}-role-ws-ci-update", "EP000-0012", "ワークスペース更新 (CI)" ]
ROLE_WS_ROLE_WS_CD_UPDATE = [ "ws-{}-role-ws-cd-update", "EP000-0013", "ワークスペース更新 (CD)" ]
ROLE_WS_ROLE_WS_DELETE = [ "ws-{}-role-ws-delete", "EP000-0014", "ワークスペース削除" ]
ROLE_WS_ROLE_OWNER_ROLE_SETTING = [ "ws-{}-role-owner-role-setting", "EP000-0015", "オーナーロール設定" ]
ROLE_WS_ROLE_MEMBER_ADD = [ "ws-{}-role-member-add", "EP000-0016", "メンバー追加" ]
ROLE_WS_ROLE_MEMBER_ROLE_UPDATE = [ "ws-{}-role-member-role-update", "EP000-0017", "ロール変更" ]
ROLE_WS_ROLE_CI_PIPELINE_RESULT = [ "ws-{}-role-ci-pipeline-result", "EP000-0018", "CIパイプライン結果確認" ]
ROLE_WS_ROLE_MANIFEST_SETTING = [ "ws-{}-role-manifest-setting", "EP000-0019", "Manifestテンプレート・パラメータ編集" ]
ROLE_WS_ROLE_CD_EXECUTE = [ "ws-{}-role-cd-execute", "EP000-0020", "CD実行" ]
ROLE_WS_ROLE_CD_EXECUTE_RESULT = [ "ws-{}-role-cd-execute-result", "EP000-0021", "CD実行結果確認" ]
