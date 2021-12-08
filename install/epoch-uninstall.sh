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
# TEKTON resource delete
#
echo "---- delete TEKTON : pipelinerun"
for namespace in \
	$( kubectl exec -i deploy/epoch-control-tekton-api -n epoch-system -- bash -c 'kubectl tkn pipelinerun list -A -o jsonpath="{range .items[*]}{@.metadata.namespace}{\"\n\"}{end}" | uniq' );
do
	echo "namespace : ${namespace}";
	kubectl exec -i deploy/epoch-control-tekton-api -n epoch-system -- bash -c "tkn pipelinerun delete --all -f -n ${namespace}";
done

echo "---- delete TEKTON : taskrun"
for namespace in \
	$( kubectl exec -i deploy/epoch-control-tekton-api -n epoch-system -- bash -c 'kubectl tkn taskrun list -A -o jsonpath="{range .items[*]}{@.metadata.namespace}{\"\n\"}{end}" | uniq' );
do
	echo "namespace : ${namespace}";
	kubectl exec -i deploy/epoch-control-tekton-api -n epoch-system -- bash -c "tkn taskrun delete --all -f -n ${namespace}";
done

echo "---- delete TEKTON : eventlistener"
for namespace in \
	$( kubectl exec -i deploy/epoch-control-tekton-api -n epoch-system -- bash -c 'kubectl tkn eventlistener list -A -o jsonpath="{range .items[*]}{@.metadata.namespace}{\"\n\"}{end}" | uniq' );
do
	echo "namespace : ${namespace}";
	kubectl exec -i deploy/epoch-control-tekton-api -n epoch-system -- bash -c "tkn eventlistener delete --all -f -n ${namespace}";
done

echo "---- delete TEKTON : triggerbinding"
for namespace in \
	$( kubectl exec -i deploy/epoch-control-tekton-api -n epoch-system -- bash -c 'kubectl tkn triggerbinding list -A -o jsonpath="{range .items[*]}{@.metadata.namespace}{\"\n\"}{end}" | uniq' );
do
	echo "namespace : ${namespace}";
	kubectl exec -i deploy/epoch-control-tekton-api -n epoch-system -- bash -c "tkn triggerbinding delete --all -f -n ${namespace}";
done

echo "---- delete TEKTON : triggertemplate"
for namespace in \
	$( kubectl exec -i deploy/epoch-control-tekton-api -n epoch-system -- bash -c 'kubectl tkn triggertemplate list -A -o jsonpath="{range .items[*]}{@.metadata.namespace}{\"\n\"}{end}" | uniq' );
do
	echo "namespace : ${namespace}";
	kubectl exec -i deploy/epoch-control-tekton-api -n epoch-system -- bash -c "tkn triggertemplate delete --all -f -n ${namespace}";
done

echo "---- delete TEKTON : pipeline"
for namespace in \
	$( kubectl exec -i deploy/epoch-control-tekton-api -n epoch-system -- bash -c 'kubectl tkn pipeline list -A -o jsonpath="{range .items[*]}{@.metadata.namespace}{\"\n\"}{end}" | uniq' );
do
	echo "namespace : ${namespace}";
	kubectl exec -i deploy/epoch-control-tekton-api -n epoch-system -- bash -c "tkn pipeline delete --all -f -n ${namespace}";
done

echo "---- delete TEKTON : task"
for namespace in \
	$( kubectl exec -i deploy/epoch-control-tekton-api -n epoch-system -- bash -c 'kubectl tkn task list -A -o jsonpath="{range .items[*]}{@.metadata.namespace}{\"\n\"}{end}" | uniq' );
do
	echo "namespace : ${namespace}";
	kubectl exec -i deploy/epoch-control-tekton-api -n epoch-system -- bash -c "tkn task delete --all -f -n ${namespace}";
done

echo "---- delete EPOCH workspace : namespace"
for namespace in \
	$( kubectl get ns -o jsonpath="{range .items[*]}{@.metadata.name}{\"\n\"}{end}" | grep '^epoch-ws-' )
do
	echo "namespace : ${namespace}";
	kubectl delete ns ${namespace};
done

echo "---- delete EPOCH workspace : namespace"
for namespace in \
	$( kubectl get ns -o jsonpath="{range .items[*]}{@.metadata.name}{\"\n\"}{end}" | grep '^epoch-tekton-pipeline-' )
do
	echo "namespace : ${namespace}";
	kubectl delete ns ${namespace};
done

# ～0.2.0 Version Workspace
kubectl delete ns epoch-workspace --ignore-not-found;

echo "---- delete EPOCH pipeline PV"
for pvname in \
	$( kubectl get pv -o jsonpath="{range .items[*]}{@.metadata.name}{\"\n\"}{end}" | grep '^epoch-tekton-pipeline-.*-pv' )
do
	echo "pipeline PV : ${pvname}";
	kubectl delete pv ${pvname};
done

echo "---- delete ClusterRoleBinding"
for crbname in \
	$( kubectl get ClusterRoleBinding -o jsonpath="{range .items[*]}{@.metadata.name}{\"\n\"}{end}" | grep '^trigger-sa-cluster-rolebinding-' )
do
	echo "ClusterRoleBinding : ${crbname}";
	kubectl delete ClusterRoleBinding ${crbname};
done

echo "---- delete ClusterRoleBinding"
for crbname in \
	$( kubectl get ClusterRoleBinding -o jsonpath="{range .items[*]}{@.metadata.name}{\"\n\"}{end}" | grep '^trigger-sa-cluster-rolebinding-' )
do
	echo "ClusterRoleBinding : ${crbname}";
	kubectl delete ClusterRoleBinding ${crbname};
done
for crbname in \
	$( kubectl get ClusterRoleBinding -o jsonpath="{range .items[*]}{@.metadata.name}{\"\n\"}{end}" | grep '^argocd-application-controller-' )
do
	echo "ClusterRoleBinding : ${crbname}";
	kubectl delete ClusterRoleBinding ${crbname};
done
for crbname in \
	$( kubectl get ClusterRoleBinding -o jsonpath="{range .items[*]}{@.metadata.name}{\"\n\"}{end}" | grep '^argocd-server-' )
do
	echo "ClusterRoleBinding : ${crbname}";
	kubectl delete ClusterRoleBinding ${crbname};
done

echo "---- delete ClusterRole"
for crname in \
	$( kubectl get ClusterRole -o jsonpath="{range .items[*]}{@.metadata.name}{\"\n\"}{end}" | grep '^trigger-sa-cluster-role-' )
do
	echo "ClusterRole : ${crname}";
	kubectl delete ClusterRole ${crname};
done

echo "-- DELETE TEKTON"
kubectl delete -f "${BASEDIR}/source/tekton/tekton-trigger-interceptors.yaml" --ignore-not-found
kubectl delete -f "${BASEDIR}/source/tekton/tekton-trigger-release.yaml" --ignore-not-found
kubectl delete -f "${BASEDIR}/source/tekton/tekton-pipeline-release.yaml" --ignore-not-found

echo "-- DELETE EPOCH POD --"
kubectl delete -f "${BASEDIR}/epoch-install.yaml" --ignore-not-found

echo "-- DELETE EPOCH PV --"
kubectl delete -f "${BASEDIR}/epoch-pv.yaml" --ignore-not-found
