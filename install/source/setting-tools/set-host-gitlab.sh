#!/bin/bash
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
BASENAME=$(basename "$0")
CMD_RESULT="/tmp/result.$$"
LF='
'
source "`dirname $0`/common-import-logger.sh" "${BASENAME}"

logger "INFO" "START : set-host-gitlab.sh"

GITLAB_NAMESPACE="gitlab"
GITLAB_INSTALL_CHECK_TIMES=360
GIT_API_BASE="http://gitlab-webservice-default.${GITLAB_NAMESPACE}.svc:8181"

#
# check parameter
#
if [ $# -ne 1 ]; then
    logger "ERROR" "Usage : ${BASENAME} [hostname or IPaddress]"
    logger "ERROR" "Check the parameters and try again"
    exit 1
fi

PRM_MY_HOST="$1"
logger "INFO" "PARAM PRM_MY_HOST : ${PRM_MY_HOST}"

GITLAB_CLONE_URL="https://${PRM_MY_HOST}:31183/"

logger "INFO" "START : Wait Gitlab Installer finished"

INSTALLER_STATUS=""
for ((i=1; i<=${GITLAB_INSTALL_CHECK_TIMES}; i++)); do
    sleep 10;
    INSTALLER_STATUS=$(kubectl get job/gitlab-installer -n ${GITLAB_NAMESPACE} -o "jsonpath={.status.conditions[0].type}")
    if [ $? -ne 0 ]; then
        continue;
    fi
    if [ "${INSTALLER_STATUS}" = "Complete" ]; then
        break;
    fi
    if [ "${INSTALLER_STATUS}" = "Error" ]; then
        logger "ERROR" "CANCELED : because the installation failed"
        exit 1
    fi
done
if [ "${INSTALLER_STATUS}" != "Complete" ]; then
    logger "ERROR" "CANCELED : because the installation wait timeout"
    exit 1
fi

logger "INFO" "START : Get TOKEN"
TOKEN=$(kubectl get secret gitlab-root-token -n ${GITLAB_NAMESPACE} -o jsonpath='{.data.TOKEN}' | base64 --decode)
if [ $? -ne 0 ]; then
    logger "ERROR" "CANCELED : Failed to get token"
    exit 1
fi

logger "INFO" "START : Encode CLONE URL"
GITLAB_CLONE_URL_ENC=$(echo "${GITLAB_CLONE_URL}" | perl -nle 's/([^\w ])/"%".unpack("H2",$1)/eg; s/ /\+/g; print')
if [ $? -ne 0 ]; then
    logger "ERROR" "encode clone url"
    exit 1
fi

logger "INFO" "START : Setting custom_http_clone_url_root"
SUCCEED_SETTING=0

STATUS_CODE=$(
    curl -X PUT \
    -H 'Content-Type: application/json' \
    -H "PRIVATE-TOKEN: ${TOKEN}" \
    -w '%{http_code}\n' -o /dev/null \
    "${GIT_API_BASE}/api/v4/application/settings?custom_http_clone_url_root=${GITLAB_CLONE_URL_ENC}" \
)
logger "INFO" "Setting custom_http_clone_url_root STATUS_CODE:${STATUS_CODE}"

if [ $? -ne 0 -o "${STATUS_CODE}" != "200" ]; then
    logger "ERROR" "configuration was failed"
    exit 1
fi

logger "INFO" "configuration was successful"
exit 0
