#!/bin/bash
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

BASE_DIR=`dirname $0`

ALL_MANIFESTS="${BASE_DIR}/epoch-install.yaml"
UPDATE_MANIFESTS="${BASE_DIR}/epoch-update.yaml"

SOURCE_MANIFEST="${BASE_DIR}/source"
TEMPLATES_DIR="${BASE_DIR}/source/templates"
TEKTON_MANIFEST="${BASE_DIR}/source/tekton"
GITLAB_INSTALLER="${BASE_DIR}/source/gitlab"
TOOLS_SCRIPT="${BASE_DIR}/source/setting-tools"


# ---- templatesフォルダ内のtemplateファイルをもとに定義用のyaml生成 ----
cat <<EOF > ${SOURCE_MANIFEST}/gateway-conf-template.yaml
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
EOF
kubectl create cm gateway-conf-template -n exastro-platform-authentication-infra --dry-run=client -o yaml \
    --from-file=${TEMPLATES_DIR}/epoch-system-template.conf       \
    --from-file=${TEMPLATES_DIR}/epoch-system-ws-template.conf    \
    --from-file=${TEMPLATES_DIR}/epoch-ws-ita-template.conf       \
    --from-file=${TEMPLATES_DIR}/epoch-ws-sonarqube-template.conf \
    >>   ${SOURCE_MANIFEST}/gateway-conf-template.yaml

# ---- source/tektonフォルダ内のファイルをもとにinstaller scriptのyaml生成 ----
cat <<EOF > ${SOURCE_MANIFEST}/tekton-installer-script.yaml
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
EOF
kubectl create cm tekton-installer-script -n epoch-system --dry-run=client -o yaml \
    --from-file=${TEKTON_MANIFEST}/tekton-installer-script.sh \
    --from-file=${TEKTON_MANIFEST}/tekton-pipeline-release.yaml \
    --from-file=${TEKTON_MANIFEST}/tekton-trigger-release.yaml \
    --from-file=${TEKTON_MANIFEST}/tekton-trigger-interceptors.yaml \
    >>   ${SOURCE_MANIFEST}/tekton-installer-script.yaml

cat <<EOF > ${SOURCE_MANIFEST}/epoch-init-setting-script.yaml
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
EOF
kubectl create cm epoch-init-setting-script -n epoch-system --dry-run=client -o yaml \
    --from-file=${TEMPLATES_DIR}/epoch-init-setting.sh \
    >>   ${SOURCE_MANIFEST}/epoch-init-setting-script.yaml

cat <<EOF > ${SOURCE_MANIFEST}/gateway-httpd-pv-create-script.yaml
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
EOF
kubectl create cm gateway-httpd-pv-create-script -n epoch-system --dry-run=client -o yaml \
    --from-file=${TEMPLATES_DIR}/epoch-pv-creator.sh \
    --from-file=${TEMPLATES_DIR}/exastro-authentication-infra-httpd-conf-pv-template.yaml \
    >>   ${SOURCE_MANIFEST}/gateway-httpd-pv-create-script.yaml

cat <<EOF > ${SOURCE_MANIFEST}/epoch-system-pv-create-script.yaml
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
EOF
kubectl create cm epoch-system-pv-create-script -n epoch-system --dry-run=client -o yaml \
    --from-file=${TEMPLATES_DIR}/epoch-pv-creator.sh \
    --from-file=${TEMPLATES_DIR}/epoch-system-pv-template.yaml \
    >>   ${SOURCE_MANIFEST}/epoch-system-pv-create-script.yaml


# ---- source/gitlabフォルダ内のファイルをもとにinstaller scriptのyaml生成 ----
cat <<EOF > ${SOURCE_MANIFEST}/gitlab-installer-start-script.yaml
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
EOF
kubectl create cm gitlab-installer-start-script -n epoch-system --dry-run=client -o yaml \
    --from-file=${GITLAB_INSTALLER}/gitlab-installer-start.yaml \
    --from-file=${GITLAB_INSTALLER}/gitlab-installer-start.sh \
    >>   ${SOURCE_MANIFEST}/gitlab-installer-start-script.yaml

# ---- source/setting-toolsフォルダ内のファイルをもとにsetting-tools scriptのyaml生成 ----
cat <<EOF > ${SOURCE_MANIFEST}/epoch-setting-tools-script.yaml
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
EOF
kubectl create cm epoch-setting-tools-script -n epoch-system --dry-run=client -o yaml \
    --from-file=${TOOLS_SCRIPT}/common-import-logger.sh \
    --from-file=${TOOLS_SCRIPT}/set-host.sh \
    --from-file=${TOOLS_SCRIPT}/set-host-gitlab.sh \
    --from-file=${TOOLS_SCRIPT}/set-proxy.sh \
    --from-file=${TOOLS_SCRIPT}/get-gitlab-initial-root-password.sh \
    --from-file=${TOOLS_SCRIPT}/get-keycloak-initial-admin-password.sh \
    --from-file=${TOOLS_SCRIPT}/get-workspace-tools-account.sh \
    >>   ${SOURCE_MANIFEST}/epoch-setting-tools-script.yaml


# ---- source内のyamlファイル定義 ----
YAMLFILES=()
YAMLFILES+=("epoch-system.yaml")
YAMLFILES+=("epoch-init-setting-script.yaml")
YAMLFILES+=("epoch-init-setting.yaml")
YAMLFILES+=("exastro-platform-authentication-infra.yaml")   # namespace
YAMLFILES+=("host-setting-config.yaml")
YAMLFILES+=("proxy-setting.yaml")
YAMLFILES+=("epoch-system-pv-create-script.yaml")
YAMLFILES+=("epoch-system-pv-create.yaml")
YAMLFILES+=("epoch-control-api-config.yaml")
YAMLFILES+=("epoch-control-workspace-api.yaml")
YAMLFILES+=("epoch-control-github-api.yaml")
YAMLFILES+=("epoch-control-inside-gitlab-api.yaml")
YAMLFILES+=("epoch-control-tekton-api.yaml")
YAMLFILES+=("epoch-control-tekton-db.yaml")
YAMLFILES+=("epoch-control-argocd-api.yaml")
YAMLFILES+=("epoch-control-ita-api.yaml")
YAMLFILES+=("epoch-control-dockerhub-api.yaml")
YAMLFILES+=("epoch-rs-workspace-api.yaml")
YAMLFILES+=("epoch-rs-workspace-db.yaml")
YAMLFILES+=("epoch-rs-ci-result-api.yaml")
YAMLFILES+=("epoch-rs-ci-result-db.yaml")
YAMLFILES+=("epoch-rs-cd-result-api.yaml")
YAMLFILES+=("epoch-rs-cd-result-db.yaml")
YAMLFILES+=("epoch-rs-logs-api.yaml")
YAMLFILES+=("epoch-rs-logs-db.yaml")
YAMLFILES+=("epoch-service-api-config.yaml")
YAMLFILES+=("epoch-service-api2.yaml")
YAMLFILES+=("epoch-ui.yaml")
YAMLFILES+=("epoch-monitoring-api-config.yaml")
YAMLFILES+=("epoch-monitoring-cd-api.yaml")

# 認証基盤
YAMLFILES+=("exastro-platform-authentication-infra-role.yaml")
YAMLFILES+=("authentication-infra-env.yaml")
YAMLFILES+=("authentication-infra-secret.yaml")
YAMLFILES+=("keycloak-db.yaml")
YAMLFILES+=("keycloak.yaml")
YAMLFILES+=("gateway-conf-template.yaml")
YAMLFILES+=("nodeport-template.yaml")
YAMLFILES+=("authentication-infra-api.yaml")
YAMLFILES+=("gateway-httpd.yaml")
YAMLFILES+=("gateway-httpd-pv-create-script.yaml")
YAMLFILES+=("gateway-httpd-pv-create.yaml")

# TEKTON instasller
YAMLFILES+=("tekton-installer-script.yaml")
YAMLFILES+=("tekton-installer.yaml")

# gitlab Installer
YAMLFILES+=("gitlab-installer-start-script.yaml")
YAMLFILES+=("gitlab-installer-start.yaml")

# epoch setting-tools
YAMLFILES+=("epoch-setting-tools-script.yaml")
YAMLFILES+=("epoch-setting-tools.yaml")

# update exclude files
UPDATE_EXCLUDE_FILES=()
UPDATE_EXCLUDE_FILES+=("host-setting-config.yaml")
UPDATE_EXCLUDE_FILES+=("proxy-setting.yaml")
UPDATE_EXCLUDE_FILES+=("epoch-control-api-config.yaml")
UPDATE_EXCLUDE_FILES+=("epoch-service-api-config.yaml")
UPDATE_EXCLUDE_FILES+=("authentication-infra-env.yaml")
UPDATE_EXCLUDE_FILES+=("authentication-infra-secret.yaml")
UPDATE_EXCLUDE_FILES+=("gitlab-installer-start-script.yaml")
UPDATE_EXCLUDE_FILES+=("gitlab-installer-start.yaml")


# -----------------------------------



cat <<EOF > ${ALL_MANIFESTS}
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
EOF

cat <<EOF > ${UPDATE_MANIFESTS}
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
EOF


for YAMLFILE in ${YAMLFILES[@]}; do
    if [ ! -f "${SOURCE_MANIFEST}/${YAMLFILE}" ]; then
        echo "ERROR: not found ${YAMLFILE}"
        exit 1
    fi
    echo    ""                                      >>  ${ALL_MANIFESTS}
    echo    "#---- ${YAMLFILE}"                     >>  ${ALL_MANIFESTS}
    echo    "---"                                   >>  ${ALL_MANIFESTS}
    cat     "${SOURCE_MANIFEST}/${YAMLFILE}"        >>  ${ALL_MANIFESTS}

    if [[ $(printf '%s\n' "${UPDATE_EXCLUDE_FILES[@]}" | grep -qx "${YAMLFILE}"; echo -n $? ) -ne 0 ]]; then
        echo    ""                                      >>  ${UPDATE_MANIFESTS}
        echo    "#---- ${YAMLFILE}"                     >>  ${UPDATE_MANIFESTS}
        echo    "---"                                   >>  ${UPDATE_MANIFESTS}
        cat     "${SOURCE_MANIFEST}/${YAMLFILE}"        >>  ${UPDATE_MANIFESTS}
    fi
done

for YAMLFILEPATH in $(ls ${SOURCE_MANIFEST}/*.yaml); do
    YAMLNAME=$(basename "${YAMLFILEPATH}")

    ONLIST=$(for item in "${YAMLFILES[@]}"; do echo "${item}"; done | grep "${YAMLNAME}" | wc -l)
    if [ ${ONLIST} -eq 0 ]; then
        echo "WARNING: not listed file : ${YAMLNAME}"
    fi
done


echo "SUCCEED !!"
