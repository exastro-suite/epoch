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

SCRIPT_PATH="/tekton-installer-script"

echo "---- install tekton-pipeline-release.yaml"
kubectl apply -f ${SCRIPT_PATH}/tekton-pipeline-release.yaml

echo "---- install tekton-trigger-release.yaml"
kubectl apply -f ${SCRIPT_PATH}/tekton-trigger-release.yaml

echo "---- waiting tekton installed"

while true; do
    sleep 5;
    echo "  Check running tekton ...";
    kubectl get deploy tekton-triggers-webhook -n tekton-pipelines > /dev/null
    if [ $? -ne 0 ]; then
        continue;
    fi
    kubectl get deploy tekton-pipelines-webhook -n tekton-pipelines > /dev/null
    if [ $? -ne 0 ]; then
        continue;
    fi
    available=$(kubectl get deploy tekton-triggers-webhook -n tekton-pipelines -o json | jq -r ".status.availableReplicas")
    if [ "${available}" == "null" -o "${available}" == "0" ]; then
        continue;
    fi
    available=$(kubectl get deploy tekton-pipelines-webhook -n tekton-pipelines -o json | jq -r ".status.availableReplicas")
    if [ "${available}" == "null" -o "${available}" == "0" ]; then
        continue;
    fi

    if [ $(kubectl get pod -n tekton-pipelines -o json | jq -r ".items[].status.containerStatuses[].ready" | sed -e "/true/d" | wc -l) -ne 0 ]; then
        continue;
    fi
    break;
done;

echo "---- install tekton-trigger-interceptors.yaml"
kubectl apply -f ${SCRIPT_PATH}/tekton-trigger-interceptors.yaml
