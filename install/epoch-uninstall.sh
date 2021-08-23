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
NS_NAME_PIPELINE=epoch-tekton-pipelines

BASEDIR=`dirname "$0"`

if [ ! -f "${BASEDIR}/epoch-install.yaml" ]; then
	echo "(ERROR) File Not Found: ${BASEDIR}/epoch-install.yaml"
	exit 1
fi
if [ ! -f "${BASEDIR}/epoch-pv.yaml" ]; then
	echo "(ERROR) File Not Found: ${BASEDIR}/epoch-pv.yaml"
	exit 1
fi

POD_NAME_CICD=`kubectl get pod -n ${NS_NAME_EPOCH} | sed -n -e '/^[e]poch-cicd-api-/s/ .*$//p'`

if [ ! -z "${POD_NAME_CICD}" ]; then
	# delete tekton resource
	echo "-- DELETE TEKTON PIPELINE --"
	kubectl exec -it ${POD_NAME_CICD} -n ${NS_NAME_EPOCH} -- kubectl delete -f /app/epoch/epochCiCdApi/resource/conv/tekton-pipeline --ignore-not-found

	echo "-- DELETE TEKTON TRIGGER --"
	kubectl exec -it ${POD_NAME_CICD} -n ${NS_NAME_EPOCH} -- kubectl delete -f /app/epoch/epochCiCdApi/resource/conv/tekton-trigger --ignore-not-found

	echo "-- DELETE TEKTON COMMON --"
	kubectl exec -it ${POD_NAME_CICD} -n ${NS_NAME_EPOCH} -- kubectl delete -f /app/epoch/epochCiCdApi/resource/conv/tekton-common --ignore-not-found
fi

if [ ! -z "${POD_NAME_CICD}" ]; then
	echo "-- DELETE TEKTON pipelinerun --"
	kubectl exec -it ${POD_NAME_CICD} -n ${NS_NAME_EPOCH} -- tkn pipelinerun delete --all -f -n ${NS_NAME_PIPELINE}
	echo "-- DELETE TEKTON taskrun --"
	kubectl exec -it ${POD_NAME_CICD} -n ${NS_NAME_EPOCH} -- tkn taskrun delete --all -f -n ${NS_NAME_PIPELINE}
	echo "-- DELETE TEKTON eventlistener --"
	kubectl exec -it ${POD_NAME_CICD} -n ${NS_NAME_EPOCH} -- tkn eventlistener delete --all -f -n ${NS_NAME_PIPELINE}
	echo "-- DELETE TEKTON triggerbinding --"
	kubectl exec -it ${POD_NAME_CICD} -n ${NS_NAME_EPOCH} -- tkn triggerbinding delete --all -f -n ${NS_NAME_PIPELINE}
	echo "-- DELETE TEKTON triggertemplate --"
	kubectl exec -it ${POD_NAME_CICD} -n ${NS_NAME_EPOCH} -- tkn triggertemplate delete --all -f -n ${NS_NAME_PIPELINE}
	echo "-- DELETE TEKTON pipeline --"
	kubectl exec -it ${POD_NAME_CICD} -n ${NS_NAME_EPOCH} -- tkn pipeline delete --all -f -n ${NS_NAME_PIPELINE}
	echo "-- DELETE TEKTON task --"
	kubectl exec -it ${POD_NAME_CICD} -n ${NS_NAME_EPOCH} -- tkn task delete --all -f -n ${NS_NAME_PIPELINE}
fi

if [ ! -z "${POD_NAME_CICD}" ]; then
	echo "-- DELETE WORKSPACE PODS --"
	kubectl exec -it ${POD_NAME_CICD} -n ${NS_NAME_EPOCH} -- kubectl delete -f /app/epoch/epochCiCdApi/resource/ita_install.yaml -n epoch-workspace --ignore-not-found
	kubectl exec -it ${POD_NAME_CICD} -n ${NS_NAME_EPOCH} -- kubectl delete -f /app/epoch/epochCiCdApi/resource --ignore-not-found
fi

echo "-- DELETE NAMESPACE epoch-tekton-pipelines --"
kubectl delete namespace epoch-tekton-pipelines

echo "-- DELETE NAMESPACE epoch-workspace --"
kubectl delete namespace epoch-workspace

echo "-- DELETE EPOCH POD --"
kubectl delete -f "${BASEDIR}/epoch-install.yaml" --ignore-not-found

echo "-- DELETE EPOCH PV --"
kubectl delete -f "${BASEDIR}/epoch-pv.yaml" --ignore-not-found
