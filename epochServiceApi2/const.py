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
ROLE_WS_OWNER = "ws-{}-owner"
ROLE_WS_MANAGER = "ws-{}-manager"
ROLE_WS_MEMBER_MG = "ws-{}-member-mg"
ROLE_WS_CI_SETTING = "ws-{}-ci-setting"
ROLE_WS_CI_RESULT = "ws-{}-ci-result"
ROLE_WS_CD_SETTING = "ws-{}-cd-setting"
ROLE_WS_CD_EXECUTE = "ws-{}-cd-execute"
ROLE_WS_CD_RESULT = "ws-{}-cd-result"

# ロール権限 Role authority
ROLE_WS_ROLE_WS_REFERENCE = "ws-{}-role-ws-reference"
ROLE_WS_ROLE_WS_NAME_UPDATE = "ws-{}-role-ws-name-update"
ROLE_WS_ROLE_WS_CI_UPDATE = "ws-{}-role-ws-ci-update"
ROLE_WS_ROLE_WS_CD_UPDATE = "ws-{}-role-ws-cd-update"
ROLE_WS_ROLE_WS_DELETE = "ws-{}-role-ws-delete"
ROLE_WS_ROLE_OWNER_ROLE_SETTING = "ws-{}-role-owner-role-setting"
ROLE_WS_ROLE_MEMBER_ADD = "ws-{}-role-member-add"
ROLE_WS_ROLE_MEMBER_ROLE_UPDATE = "ws-{}-role-member-role-update"
ROLE_WS_ROLE_CI_PIPELINE_RESULT = "ws-{}-role-ci-pipeline-result"
ROLE_WS_ROLE_MANIFEST_SETTING = "ws-{}-role-manifest-setting"
ROLE_WS_ROLE_CD_EXECUTE = "ws-{}-role-cd-execute"
ROLE_WS_ROLE_CD_EXECUTE_RESULT = "ws-{}-role-cd-execute-result"
