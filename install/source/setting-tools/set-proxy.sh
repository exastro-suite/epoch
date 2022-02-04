#!/bin/bash
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

BASENAME=$(basename "$0")
CMD_RESULT="/tmp/result.$$"
LF='
'
source "`dirname $0`/common-import-logger.sh" "${BASENAME}"

logger "INFO" "START : ${BASENAME}"

if [ $# -ne 2 ]; then
    logger "ERROR" "Usage : ${BASENAME} [https_proxy] [http_proxy]"
    logger "ERROR" "Check the parameters and try again"
    exit 1
fi

PRM_HTTPS_PROXY=$1
PRM_HTTP_PROXY=$2

logger "INFO" "PARAM PRM_HTTPS_PROXY : ${PRM_HTTPS_PROXY}"
logger "INFO" "PARAM PRM_HTTP_PROXY  : ${PRM_HTTP_PROXY}"

#------------------------------------------------
logger "INFO" "START : Check kubernetes api server config"

API_SERVER_POD_NAME=$(\
    kubectl get pod -n kube-system -o jsonpath="{range .items[*]}{@.metadata.name}{\"\t\"}{@.metadata.labels.component}{@.value}{\"\n\"}{end}" |\
    awk '$2=="kube-apiserver" {print $1}' |\
    head -n 1)

kubectl get pod ${API_SERVER_POD_NAME} -n kube-system -o jsonpath="{range .spec.containers[*].env[*]}{@.name}{\"\t\"}{@.value}{\"\n\"}{end}" | \
awk '\
toupper($1)=="NO_PROXY" {\
    if(index("," $2 ",",",tekton-pipelines-webhook.tekton-pipelines.svc,")==0) {\
        exit 1;\
    }\
    if(index("," $2 ",",",tekton-triggers-webhook.tekton-pipelines.svc,")==0) {\
        exit 1;\
    }\
}'

if [ $? -ne 0 ]; then
    logger "ERROR" "kubernetes settings required${LF}Set the no_proxy setting on the kubernetes api server to \"tekton-pipelines-webhook.tekton-pipelines.svc\" and \"tekton-triggers-webhook.tekton-pipelines.svc\" and try again${LF}"
    exit 1
fi

#------------------------------------------------
kubectl get configmap epoch-control-api-config -n epoch-system &> /dev/null
if [ $? -eq 0 ]; then
    logger "INFO" "START : patch epoch-control-api-config"
    kubectl patch configmap epoch-control-api-config -n epoch-system -p "\
    {\
        \"data\" : {\
            \"HTTP_PROXY\" : \"${PRM_HTTP_PROXY}\",\
            \"HTTPS_PROXY\" : \"${PRM_HTTPS_PROXY}\"\
        }\
    }"
    if [ $? -ne 0 ]; then
        logger "ERROR" "patch epoch-control-api-config"
        exit 1
    fi
fi

kubectl get configmap proxy-setting-config -n epoch-system &> /dev/null
if [ $? -eq 0 ]; then
    logger "INFO" "START : patch proxy-setting-config"
    kubectl patch configmap proxy-setting-config -n epoch-system -p "\
    {\
        \"data\" : {\
            \"HTTP_PROXY\" : \"${PRM_HTTP_PROXY}\",\
            \"HTTPS_PROXY\" : \"${PRM_HTTPS_PROXY}\"\
        }\
    }"
    if [ $? -ne 0 ]; then
        logger "ERROR" "patch proxy-setting-config"
        exit 1
    fi
fi

kubectl get configmap epoch-cicd-api-config -n epoch-system &> /dev/null
if [ $? -eq 0 ]; then
    logger "INFO" "START : patch epoch-cicd-api-config"
    kubectl patch configmap epoch-cicd-api-config -n epoch-system -p "\
    {\
        \"data\" : {\
            \"HTTP_PROXY\" : \"${PRM_HTTP_PROXY}\",\
            \"HTTPS_PROXY\" : \"${PRM_HTTPS_PROXY}\"\
        }\
    }"
    if [ $? -ne 0 ]; then
        logger "ERROR" "patch epoch-cicd-api-config"
        exit 1
    fi
fi

#------------------------------------------------
kubectl get deploy -n epoch-system -o jsonpath="{range .items[*]}{@.metadata.name}{\"\n\"}{end}" |\
while read DEPLOY; do
    REFERENCE_COUNT=$(
        kubectl get deploy -n epoch-system "${DEPLOY}" -o yaml |
        sed -n -e '/epoch-control-api-config/p' -e '/proxy-setting-config/p' -e '/epoch-cicd-api-config/p' |
        wc -l
    )
    if [ ${REFERENCE_COUNT} -gt 0 ]; then
        logger "INFO" "rollout restart deploy ${DEPLOY}"
        kubectl rollout restart deploy -n epoch-system "${DEPLOY}"
        if [ $? -ne 0 ]; then
            logger "ERROR" "rollout restart deploy ${DEPLOY}"
            exit 1
        fi
    fi
done

exit 0
