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

GITLAB_NAMESPACE="gitlab"
GITLAB_CONFIG_SETTING_RETRY=60
GIT_API_BASE="http://gitlab-webservice-default:8181"


BASEDIR=$(dirname $0)

# version 5.6.2
CHART_FILE=/installer/chart/gitlab-5.6.2.tgz
DEPLOY_RAILS_RUNNER=gitlab-toolbox

#
# Create and Initialize PV Directory
#
echo "[INFO] START : Create and Initialize PV Directory"

rm -rf /gitlab-pv/*
mkdir -p /gitlab-pv/postgresql
mkdir -p /gitlab-pv/minio
mkdir -p /gitlab-pv/redis
mkdir -p /gitlab-pv/gitaly
chmod 777 /gitlab-pv/*
#
# Get NodeName
#
echo "[INFO] START : Get NodeName"
POD_NAME=${HOSTNAME}
echo "POD_NAME: ${POD_NAME}"

NODENAME=$(kubectl get pod -n "${GITLAB_NAMESPACE}" "${POD_NAME}" -o jsonpath='{.spec.nodeName}' )
if [ $? -ne 0 ]; then
  echo "[ERROR] get nodename"
fi
echo "[INFO] NODENAME : ${NODENAME}"

#kubectl delete job gitlab-pv-initializer -n "${GITLAB_NAMESPACE}"

#
# Create PV
#
echo "[INFO] START : create pv"
sed -e  "s/#NODENAME#/${NODENAME}/g" ${BASEDIR}/gitlab-pv-template.yaml |\
kubectl apply -f -
if [ $? -ne 0 ]; then
  echo "[ERROR] apply pv"
  exit 1
fi

#
# install gitlab
#
echo "[INFO] START : helm install"
helm install gitlab ${CHART_FILE} -n "${GITLAB_NAMESPACE}" --values ${BASEDIR}/gitlab-config.yaml
if [ $? -ne 0 ]; then
  echo "[ERROR] helm install"
  exit 1
fi

#
# Waitting Runner Up
#
echo "[INFO] START : Waitting Runner Up"
while true; do
    sleep 5;
    echo -n "."
    NOT_READY_COUNT=$(kubectl get pod -n "${GITLAB_NAMESPACE}" -o jsonpath='{range .items[*]}{@.status.phase}{"\n"}' | sed -e "/Running/d" -e "/Succeeded/d" -e "/^$/d" | wc -l)
    if [ $? -ne 0 ]; then
      continue;
    fi
    if [ ${NOT_READY_COUNT} -ne 0 ]; then
      continue;
    fi
    kubectl get deploy ${DEPLOY_RAILS_RUNNER} -n "${GITLAB_NAMESPACE}" &> /dev/null
    if [ $? -ne 0 ]; then
      continue;
    fi
    kubectl get deploy gitlab-webservice-default -n "${GITLAB_NAMESPACE}" &> /dev/null
    if [ $? -ne 0 ]; then
      continue;
    fi
    echo ""
    break;
done;

#
# Generate root token
#
echo "[INFO] START : Generate root token"
TOKEN_LENGTH=20
ROOT_TOKEN=$(cat /dev/urandom | sed -e 's/[^A-Za-z0-9]//g' | base64 | fold -w 20 | head -n 1)
if [ $? -ne 0 ]; then
  echo "[ERROR] generate ROOT_TOKEN"
fi

echo "[INFO] ROOT_TOKEN : ${ROOT_TOKEN}"
sed -e  "s|#ROOT_TOKEN#|${ROOT_TOKEN}|g" \
    -e  "s|#NAMESPACE#|${GITLAB_NAMESPACE}|g" \
    ${BASEDIR}/gitlab-root-token-template.yaml |\
kubectl apply -f -
if [ $? -ne 0 ]; then
  echo "[ERROR] generate ROOT_TOKEN secret"
  exit 1
fi


#
# Setting root token
#
echo "[INFO] START : Setting root token"
kubectl exec -i deploy/${DEPLOY_RAILS_RUNNER} -n "${GITLAB_NAMESPACE}" \
-- gitlab-rails runner \
"token = User.find_by_username('root').personal_access_tokens.create(scopes: [:api], name: 'epoch system token'); token.set_token('${ROOT_TOKEN}'); token.save!"
if [ $? -ne 0 ]; then
  echo "[ERROR] Setting root token"
  exit 1
fi

#
# configure gitlab
#
EXITCODE_PUT_enabled_git_access_protocol=-1
EXITCODE_allow_local_requests_from_web_hooks_and_services=-1
EXITCODE_allow_local_requests_from_hooks_and_services=-1

for ((i=1; i<=${GITLAB_CONFIG_SETTING_RETRY}; i++)); do
    sleep 10;

    if [ ${EXITCODE_PUT_enabled_git_access_protocol} -ne 0 ]; then
      echo -n "[INFO] Setting enabled_git_access_protocol : "
      STATUS_CODE=$( \
        curl -X PUT \
        -H 'Content-Type: application/json' \
        -H "PRIVATE-TOKEN: ${ROOT_TOKEN}" \
        -w '%{http_code}\n' -o /dev/null \
        "${GIT_API_BASE}/api/v4/application/settings?enabled_git_access_protocol=http" \
      )

      if [ $? -eq 0 -a "${STATUS_CODE}" = "200" ]; then
        EXITCODE_PUT_enabled_git_access_protocol=0
        echo "DONE"
      else
        echo "FAIL"
        continue
      fi
    fi

    if [ ${EXITCODE_allow_local_requests_from_web_hooks_and_services} -ne 0 ]; then
      echo -n "[INFO] Setting allow_local_requests_from_web_hooks_and_services : "
      STATUS_CODE=$( \
        curl -X PUT \
          -H 'Content-Type: application/json' \
          -H "PRIVATE-TOKEN: ${ROOT_TOKEN}" \
          -w '%{http_code}\n' -o /dev/null \
          "${GIT_API_BASE}/api/v4/application/settings?allow_local_requests_from_web_hooks_and_services=true" \
      )

      if [ $? -eq 0 -a "${STATUS_CODE}" = "200" ]; then
        EXITCODE_allow_local_requests_from_web_hooks_and_services=0
        echo "DONE"
      else
        echo "FAIL"
        continue
      fi
    fi

    EXITCODE_allow_local_requests_from_hooks_and_services=0
    # if [ ${EXITCODE_allow_local_requests_from_hooks_and_services} -ne 0 ]; then
    #   echo -n "[INFO] Setting allow_local_requests_from_hooks_and_services : "
    #   STATUS_CODE=$( \
    #     curl -X PUT \
    #       -H 'Content-Type: application/json' \
    #       -H "PRIVATE-TOKEN: ${ROOT_TOKEN}" \
    #       "${GIT_API_BASE}/api/v4/application/settings?allow_local_requests_from_hooks_and_services=true" \
    #   )

    #   if [ $? -eq 0 -a "${STATUS_CODE}" = "200" ]; then
    #     EXITCODE_allow_local_requests_from_hooks_and_services=0
    #     echo "DONE"
    #   else
    #     echo "FAIL"
    #     continue
    #   fi
    # fi

    break;
done

if [ ${EXITCODE_PUT_enabled_git_access_protocol} -ne 0 \
  -o ${EXITCODE_allow_local_requests_from_web_hooks_and_services} -ne 0 \
  -o ${EXITCODE_allow_local_requests_from_hooks_and_services} -ne 0 ]; then
  echo "[ERROR] timeout configure gitlab"
  exit 1
fi

echo -n "[INFO] root initial password : "
kubectl get secret gitlab-gitlab-initial-root-password -ojsonpath='{.data.password}' -n gitlab | base64 --decode ; echo

echo "[INFO] Installation and configuration was successful"
exit 0
