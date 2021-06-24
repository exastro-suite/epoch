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

NS_NAME_EPOCH=epoch-system

POD_NAME_CICD=`kubectl get pod -n ${NS_NAME_EPOCH} | sed -n -e '/^[e]poch-cicd-api-/s/ .*$//p'`

if [ ! -z "${POD_NAME_CICD}" ]; then
	kubectl exec -it ${POD_NAME_CICD} -n ${NS_NAME_EPOCH} -- ls /app/epoch/epochCiCdApi/resource
fi

if [ ! -z "${POD_NAME_CICD}" ]; then
	echo "-- DELETE TEKTON PIPELINERUN --"
	kubectl exec -it ${POD_NAME_CICD} -n ${NS_NAME_EPOCH} -- tkn pipelinerun delete --all -f -n epoch-tekton-pipelines
fi

if [ ! -z "${POD_NAME_CICD}" ]; then
	echo "-- DELETE TEKTON PIPELINE --"
	kubectl exec -it ${POD_NAME_CICD} -n ${NS_NAME_EPOCH} -- kubectl delete -f /app/epoch/epochCiCdApi/resource/conv/tekton-pipeline
fi

if [ ! -z "${POD_NAME_CICD}" ]; then
	echo "-- DELETE TEKTON TRIGGER --"
	kubectl exec -it ${POD_NAME_CICD} -n ${NS_NAME_EPOCH} -- kubectl delete -f /app/epoch/epochCiCdApi/resource/conv/tekton-trigger
fi

if [ ! -z "${POD_NAME_CICD}" ]; then
	echo "-- DELETE TEKTON COMMON --"
	kubectl exec -it ${POD_NAME_CICD} -n ${NS_NAME_EPOCH} -- kubectl delete -f /app/epoch/epochCiCdApi/resource/conv/tekton-common
fi


if [ ! -z "${POD_NAME_CICD}" ]; then
	echo "-- DELETE WORKSPACE PODS --"
	kubectl exec -it ${POD_NAME_CICD} -n ${NS_NAME_EPOCH} -- kubectl delete -f /app/epoch/epochCiCdApi/resource -n epoch-workspace
fi

echo "-- DELETE EPOCH POD --"
kubectl delete -f ./epoch-install.yaml

echo "-- DELETE EPOCH PV --"
kubectl delete -f ./epoch-pv.yaml

echo "-- DELETE NAMESPACE --"
kubectl delete namespace epoch-workspace
kubectl delete namespace epoch-tekton-pipelines


