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

#
# epoch version 0.1.1 uninstaller
#

NS_NAME_EPOCH=epoch-system
NS_NAME_WORKSPACE=epoch-workspace
NS_NAME_PIPELINE=epoch-tekton-pipelines
NS_NAME_PIPELINE_V011=epoch-tekton-pipeline-1

BASEDIR=`dirname "$0"`

if [ ! -f "${BASEDIR}/epoch-install.yaml" ]; then
	echo "(ERROR) File Not Found: ${BASEDIR}/epoch-install.yaml"
	exit 1
fi
if [ ! -f "${BASEDIR}/epoch-pv.yaml" ]; then
	echo "(ERROR) File Not Found: ${BASEDIR}/epoch-pv.yaml"
	exit 1
fi

#
# version 0.1.0 tekton pipeline uninstall
#
POD_NAME_CICD=`kubectl get pod -n ${NS_NAME_EPOCH} | sed -n -e '/^[e]poch-cicd-api-/s/ .*$//p'`

if [ ! -z "${POD_NAME_CICD}" ]; then
	# delete tekton resource
	echo "-- DELETE TEKTON PIPELINE --"
	kubectl exec -it ${POD_NAME_CICD} -n ${NS_NAME_EPOCH} -- kubectl delete -f /app/resource/conv/tekton-pipeline --ignore-not-found

	echo "-- DELETE TEKTON TRIGGER --"
	kubectl exec -it ${POD_NAME_CICD} -n ${NS_NAME_EPOCH} -- kubectl delete -f /app/resource/conv/tekton-trigger --ignore-not-found

	echo "-- DELETE TEKTON COMMON --"
	kubectl exec -it ${POD_NAME_CICD} -n ${NS_NAME_EPOCH} -- kubectl delete -f /app/resource/conv/tekton-common --ignore-not-found
fi

#
# version 0.1.0 tekton pipeline uninstall
#
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

#
# version 0.1.1 tekton pipeline uninstall
#
POD_NAME_TEKTON=`kubectl get pod -n ${NS_NAME_EPOCH} | sed -n -e '/^[e]poch-control-tekton-api-/s/ .*$//p'`

if [ ! -z "${POD_NAME_TEKTON}" ]; then
	echo "-- DELETE TEKTON PIPELINE --"
	kubectl exec -it ${POD_NAME_TEKTON} -n ${NS_NAME_EPOCH} -- kubectl delete -f /var/epoch/tekton --ignore-not-found
fi

#
# version 0.1.1 tekton pipeline uninstall
#
if [ ! -z "${POD_NAME_TEKTON}" ]; then
	echo "-- DELETE TEKTON pipelinerun --"
	kubectl exec -it ${POD_NAME_TEKTON} -n ${NS_NAME_EPOCH} -- tkn pipelinerun delete --all -f -n ${NS_NAME_PIPELINE_V011}
	echo "-- DELETE TEKTON taskrun --"
	kubectl exec -it ${POD_NAME_TEKTON} -n ${NS_NAME_EPOCH} -- tkn taskrun delete --all -f -n ${NS_NAME_PIPELINE_V011}
	echo "-- DELETE TEKTON eventlistener --"
	kubectl exec -it ${POD_NAME_TEKTON} -n ${NS_NAME_EPOCH} -- tkn eventlistener delete --all -f -n ${NS_NAME_PIPELINE_V011}
	echo "-- DELETE TEKTON triggerbinding --"
	kubectl exec -it ${POD_NAME_TEKTON} -n ${NS_NAME_EPOCH} -- tkn triggerbinding delete --all -f -n ${NS_NAME_PIPELINE_V011}
	echo "-- DELETE TEKTON triggertemplate --"
	kubectl exec -it ${POD_NAME_TEKTON} -n ${NS_NAME_EPOCH} -- tkn triggertemplate delete --all -f -n ${NS_NAME_PIPELINE_V011}
	echo "-- DELETE TEKTON pipeline --"
	kubectl exec -it ${POD_NAME_TEKTON} -n ${NS_NAME_EPOCH} -- tkn pipeline delete --all -f -n ${NS_NAME_PIPELINE_V011}
	echo "-- DELETE TEKTON task --"
	kubectl exec -it ${POD_NAME_TEKTON} -n ${NS_NAME_EPOCH} -- tkn task delete --all -f -n ${NS_NAME_PIPELINE_V011}
fi

if [ ! -z "${POD_NAME_CICD}" ]; then
	echo "-- DELETE WORKSPACE PODS --"
	kubectl exec -it ${POD_NAME_CICD} -n ${NS_NAME_EPOCH} -- kubectl delete -f /app/resource/ita_install.yaml -n ${NS_NAME_WORKSPACE} --ignore-not-found
	kubectl exec -it ${POD_NAME_CICD} -n ${NS_NAME_EPOCH} -- kubectl delete -f /app/resource --ignore-not-found
fi

echo "-- DELETE NAMESPACE epoch-tekton-pipelines --"
# version 0.1.0 tekton pipeline uninstall
kubectl delete namespace ${NS_NAME_PIPELINE} --ignore-not-found
# version 0.1.1 tekton pipeline uninstall
kubectl delete namespace ${NS_NAME_PIPELINE_V011} --ignore-not-found

echo "-- DELETE NAMESPACE epoch-workspace --"
kubectl delete namespace ${NS_NAME_WORKSPACE} --ignore-not-found

echo "-- DELETE EPOCH POD --"
kubectl delete -f "${BASEDIR}/epoch-install.yaml" --ignore-not-found

echo "-- DELETE EPOCH PV --"
kubectl delete -f "${BASEDIR}/epoch-pv.yaml" --ignore-not-found
