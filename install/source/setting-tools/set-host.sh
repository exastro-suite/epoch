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


echo "[INFO] START : set-host.sh"

#
# Initialize variables
#
BASENAME=$(basename "$0")
STEP=0
ALLSTEPS=5

#
# check parameter
#
if [ $# -ne 1 ]; then
    echo "Usage : ${BASENAME} [hostname or IPaddress]"
    echo "ERROR : Check the parameters and try again"
    exit 1
fi

PRM_MY_HOST="$1"

#
# Initialize Setting Parameter
#
STEP=$(expr ${STEP} + 1)
echo "**** STEP : ${STEP} / ${ALLSTEPS} : Initialize Setting Parameter ..."

OIDC_PASSPHRASE=$(< /dev/urandom tr -dc 'a-zA-Z0-9' | fold -w 20 | head -n 1 | sort | uniq)
if [ $? -ne 0 -o -z "${OIDC_PASSPHRASE}" ]; then
    echo "ERROR : Generate OIDC_PASSPHRASE"
    exit 2
fi

OIDC_PASSPHRASE_B64=$(echo -n "${OIDC_PASSPHRASE}" | base64)
if [ $? -ne 0 -o -z "${OIDC_PASSPHRASE_B64}" ]; then
    echo "ERROR : Generate OIDC_PASSPHRASE_B64"
    exit 2
fi

KEYCLOAK_ADMIN_PASSW=$(< /dev/urandom tr -dc 'a-zA-Z0-9' | fold -w 20 | head -n 1 | sort | uniq)
if [ $? -ne 0 -o -z "${KEYCLOAK_ADMIN_PASSW}" ]; then
    echo "ERROR : Generate KEYCLOAK_ADMIN_PASSW"
    exit 2
fi

KEYCLOAK_ADMIN_PASSW_B64=$(echo -n "${KEYCLOAK_ADMIN_PASSW}" | base64)
if [ $? -ne 0 -o -z "${KEYCLOAK_ADMIN_PASSW_B64}" ]; then
    echo "ERROR : Generate OIDC_PASSPHRASE_B64"
    exit 2
fi

EPOCH_ADMIN_PASSWD=$(< /dev/urandom tr -dc 'a-zA-Z0-9' | fold -w 20 | head -n 1 | sort | uniq)
if [ $? -ne 0 -o -z "${KEYCLOAK_ADMIN_PASSW}" ]; then
    echo "ERROR : Generate EPOCH_ADMIN_PASSWD"
    exit 2
fi

EPOCH_ADMIN_PASSWD_B64=$(echo -n "${EPOCH_ADMIN_PASSWD}" | base64)
if [ $? -ne 0 -o -z "${EPOCH_ADMIN_PASSWD_B64}" ]; then
    echo "ERROR : Generate EPOCH_ADMIN_PASSWD_B64"
    exit 2
fi

#
# Set parameter to configmap
#
STEP=$(expr ${STEP} + 1)
echo "**** STEP : ${STEP} / ${ALLSTEPS} : Set Parameter To Configmap"

kubectl patch configmap -n epoch-system host-setting-config -p "\
{\
    \"data\" : {\
        \"EPOCH_HOSTNAME\" : \"${PRM_MY_HOST}\"\
    }\
}"
if [ $? -ne 0 ]; then
    echo "ERROR : patch configmap host-setting-config"
    exit 2
fi

kubectl patch configmap -n exastro-platform-authentication-infra exastro-platform-authentication-infra-env -p "\
{\
    \"data\" : {\
        \"EXASTRO_KEYCLOAK_HOST\" : \"${PRM_MY_HOST}\"\
    }\
}"
if [ $? -ne 0 ]; then
    echo "ERROR : patch configmap exastro-platform-authentication-infra-env"
    exit 2
fi


kubectl patch configmap -n epoch-system epoch-service-api-config -p "\
{\
    \"data\" : {\
        \"EPOCH_EPAI_HOST\" : \"${PRM_MY_HOST}\"\
    }\
}"
if [ $? -ne 0 ]; then
    echo "ERROR : patch configmap epoch-service-api-config"
    exit 2
fi


kubectl patch secret -n exastro-platform-authentication-infra exastro-platform-authentication-infra-secret -p "\
{\
    \"data\" : {\
        \"GATEWAY_CRYPTO_PASSPHRASE\" : \"${OIDC_PASSPHRASE_B64}\",\
        \"KEYCLOAK_PASSWORD\" : \"${KEYCLOAK_ADMIN_PASSW_B64}\",\
        \"EPOCH_PASSWORD\" : \"${EPOCH_ADMIN_PASSWD_B64}\"\
    }\
}"
if [ $? -ne 0 ]; then
    echo "ERROR : patch secret exastro-platform-authentication-infra-secret"
    exit 2
fi

#
# restart to reflect the settings
#
STEP=$(expr ${STEP} + 1)
echo "**** STEP : ${STEP} / ${ALLSTEPS} : restart to reflect the settings ..."

# kubectl rollout restart deploy -n epoch-system epoch-service-api
# if [ $? -ne 0 ]; then
#     echo "ERROR : rollout restart epoch-service-api"
#     exit 2
# fi

kubectl rollout restart deploy -n epoch-system epoch-service-api2
if [ $? -ne 0 ]; then
    echo "ERROR : rollout restart epoch-service-api2"
    exit 2
fi

kubectl rollout restart deploy -n epoch-system epoch-control-ita-api
if [ $? -ne 0 ]; then
    echo "ERROR : rollout restart epoch-control-ita-api"
    exit 2
fi

while true; do
    sleep 5;
    RESTART_BERFORE_API_POD=$(kubectl get pod --selector "name=authentication-infra-api" -n exastro-platform-authentication-infra -o jsonpath="{range .items[*]}{@.metadata.name}{\"\n\"}{end}" 2> /dev/null)
    if [ $? -eq 0 ]; then
        break;
    fi
done
kubectl rollout restart deploy -n exastro-platform-authentication-infra authentication-infra-api
if [ $? -ne 0 ]; then
    echo "ERROR : rollout restart authentication-infra-api"
    exit 2
fi

while true; do
    sleep 5;
    RESTART_BERFORE_KEYCLOAK_POD=$(kubectl get pod --selector "app=keycloak" -n exastro-platform-authentication-infra -o jsonpath="{range .items[*]}{@.metadata.name}{\"\n\"}{end}" 2> /dev/null)
    if [ $? -eq 0 ]; then
        break;
    fi
done
kubectl rollout restart deploy -n exastro-platform-authentication-infra keycloak
if [ $? -ne 0 ]; then
    echo "ERROR : rollout restart keycloak"
    exit 2
fi

#
# wait for restart
#
STEP=$(expr ${STEP} + 1)
echo "**** STEP : ${STEP} / ${ALLSTEPS} : wait for restart ..."

echo -n "waiting ..."
while true; do
    sleep 5;
    echo -n ".";
    NOT_READY_COUNT=$(kubectl get pod -n exastro-platform-authentication-infra -o json 2> /dev/null | \
                        jq -r ".items[].status.containerStatuses[].ready" 2> /dev/null | sed -e "/true/d" | wc -l)
    if [ $? -ne 0 ]; then
        continue
    fi
    if [ ${NOT_READY_COUNT} -ne 0 ]; then
        continue;
    fi

    RESTART_AFTER_API_POD=$(kubectl get pod --selector "name=authentication-infra-api" -n exastro-platform-authentication-infra -o jsonpath="{range .items[*]}{@.metadata.name}{\"\n\"}{end}" 2> /dev/null)
    if [ $? -ne 0 ]; then
        continue
    fi
    if [ "${RESTART_BERFORE_API_POD}" == "${RESTART_AFTER_API_POD}" ]; then
        continue;
    fi

    RESTART_AFTER_KEYCLOAK_POD=$(kubectl get pod --selector "app=keycloak" -n exastro-platform-authentication-infra -o jsonpath="{range .items[*]}{@.metadata.name}{\"\n\"}{end}" 2> /dev/null)
    if [ $? -ne 0 ]; then
        continue
    fi
    if [ "${RESTART_BERFORE_KEYCLOAK_POD}" == "${RESTART_AFTER_KEYCLOAK_POD}" ]; then
        continue;
    fi

    echo "";
    break;
done;

#
# Setting api call
#
STEP=$(expr ${STEP} + 1)
echo "**** STEP : ${STEP} / ${ALLSTEPS} : Setting api call ..."

API_RESPONSE="/tmp/${BASENAME}-infra-setting.$$"

curl \
    -X POST \
    -H  'content-type: application/json'    \
    -d  @- \
    -Ss \
    -o "${API_RESPONSE}" \
    http://authentication-infra-api.exastro-platform-authentication-infra.svc:8000/settings \
    << EOF
    {
        "realm_name": "exastroplatform",
        "realm_option": {
            "displayName": "Exastro Platform",
            "enabled": "True",
            "registrationAllowed": "True"
        },
        "realm_roles": [
            "epoch-user",
            "epoch-system"
        ],
        "groups": [
            {
                "parent_group": "",
                "group_name": "epoch-user"
            }
        ],
        "group_mappings": [
            {
                "role_name": "epoch-user",
                "group_name": "epoch-user"
            }
        ],
        "default_group_name": "epoch-user",
        "users": [
        ],
        "admin_users": [
            {
                "user_name": "epoch-admin",
                "user_password": "${EPOCH_ADMIN_PASSWD}",
                "user_groups": [],
                "user_realm_roles": [],
                "user_option": {
                    "enabled": "True"
                }
            }
        ],
        "clients": [
            {
                "id": "epoch-system",
                "protocol": "openid-connect",
                "publicClient": "false",
                "redirectUris": [
                    "https://${PRM_MY_HOST}:30443/oidc-redirect/",
                    "https://${PRM_MY_HOST}:30443/"
                ],
                "baseUrl": "https://${PRM_MY_HOST}:30443/oidc-redirect/",
                "webOrigins": [],
                "protocolMappers": [
                    {
                        "name": "epoch-system-client-map-role",
                        "protocol": "openid-connect",
                        "protocolMapper": "oidc-usermodel-client-role-mapper",
                        "config": {
                            "id.token.claim": "true",
                            "access.token.claim": "true",
                            "claim.name": "epoch-role",
                            "multivalued": "true",
                            "userinfo.token.claim": "true",
                            "usermodel.clientRoleMapping.clientId": "epoch-system"
                        }
                    },
                    {
                        "name": "epoch-system-map-role",
                        "protocol": "openid-connect",
                        "protocolMapper": "oidc-usermodel-realm-role-mapper",
                        "config": {
                            "id.token.claim": "true",
                            "access.token.claim": "true",
                            "claim.name": "epoch-role",
                            "multivalued": "true",
                            "userinfo.token.claim": "true"
                        }
                    }
                ]
            }
        ],
        "conf_template": "epoch-system-template.conf",
        "token_user": "admin",
        "token_password": "${KEYCLOAK_ADMIN_PASSW}",
        "token_realm_name": "master"
    }
EOF
if [ $? -ne 0 ]; then
    echo "ERROR : Setting api call"
    exit 2
fi

API_RESULT=$(cat "${API_RESPONSE}" | jq -r ".result")
if [ $? -ne 0 ]; then
    echo "---- API Error Response ----"
    cat "${API_RESPONSE}"
    echo "ERROR : Setting api call"
    exit 2
fi
if [ "${API_RESULT}" != "200" ]; then
    echo "---- API Error Response ----"
    cat "${API_RESPONSE}"
    echo "ERROR : Setting api call"
    exit 2
fi

echo "**** ${BASENAME} completed successfully ****"
exit 0
