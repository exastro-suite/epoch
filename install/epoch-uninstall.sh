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
BASENAME=`basename "$0"`

# wait setting
SEC_TO_WAIT_PATCH_PV=3
SEC_TO_WAIT_DELETE_PV=1

#
# check file
#
if [ ! -f "${BASEDIR}/epoch-install.yaml" ]; then
	echo "[ERROR] File Not Found: ${BASEDIR}/epoch-install.yaml"
	echo "Execute the file in the cloned repository"
	exit 1
fi
if [ ! -f "${BASEDIR}/source/tekton/tekton-trigger-interceptors.yaml" ]; then
	echo "[ERROR] File Not Found: ${BASEDIR}/source/tekton/tekton-trigger-interceptors.yaml"
	echo "Execute the file in the cloned repository"
	exit 1
fi
if [ ! -f "${BASEDIR}/source/tekton/tekton-trigger-release.yaml" ]; then
	echo "[ERROR] File Not Found: ${BASEDIR}/source/tekton/tekton-trigger-release.yaml"
	echo "Execute the file in the cloned repository"
	exit 1
fi
if [ ! -f "${BASEDIR}/source/tekton/tekton-pipeline-release.yaml" ]; then
	echo "[ERROR] File Not Found: ${BASEDIR}/source/tekton/tekton-trigger-release.yaml"
	echo "Execute the file in the cloned repository"
	exit 1
fi
if [ ! -f "${BASEDIR}/source/tekton/tekton-pipeline-release.yaml" ]; then
	echo "[ERROR] File Not Found: ${BASEDIR}/source/tekton/tekton-trigger-release.yaml"
	echo "Execute the file in the cloned repository"
	exit 1
fi

#
# uninstll option
#
OPTION_HELP="OFF"
OPTION_PV="OFF"
OPTION_GITLAB="OFF"
OPTION_TEKTON="OFF"
while [ $# -gt 0 ]; do
	case "${1}" in
		"--help"|"-h"|"-H")
			OPTION_HELP="ON"
			;;
		"--persistentvolume-data"|"-D")
			OPTION_PV="ON"
			;;
		"--gitlab")
			OPTION_GITLAB="ON"
			;;
		"--tekton")
			OPTION_TEKTON="ON"
			;;
		"--all"|"-A")
			OPTION_PV="ON"
			OPTION_GITLAB="ON"
			OPTION_TEKTON="ON"
			;;
		*)
			OPTION_HELP="ON"
			;;
	esac
	shift
done

if [ "${OPTION_HELP}" = "ON" ]; then
cat <<EOF

Usage : ${BASENAME} [--persistentvolume-file] [--gitlab] [--tekton] [--all] [--help]

option description:
	--help, -h, -H
		Print this text

	--persistentvolume-data, -D
		Clear the files in the persistent volume

	--gitlab
		Uninstall gitlab as well

	--tekton
		Uninstall tekton as well

	--all, -A
		Uninstall gitlab as well and
		Clear the files in the persistent volume

EOF
exit 1
fi

echo "[INFO] DELETE EPOCH WORKSPACE NAMESPACE"
for ns in \
	$(kubectl get ns -o jsonpath="{.items[*].metadata.name}");
do
	case "${ns}" in
		epoch-ws-[0-9]* |\
		epoch-tekton-pipeline-[0-9]*)
			echo "[EXEC] kubectl delete ns ${ns}"
			kubectl delete ns "${ns}"
			;;
	esac
done

if [ "${OPTION_PV}" = "ON" ]; then
	echo "[INFO] DELETE EPOCH WORKSPACE PERSISTENT VOLUME"
	for pv in \
		$(kubectl get pv -o jsonpath="{.items[*].metadata.name}");
	do
		case "${pv}" in
			epoch-tekton-pipeline-[0-9]* |\
			epoch-ws-[0-9]*)
				echo "[EXEC] kubectl patch pv ${pv} -p "'{"spec": {"persistentVolumeReclaimPolicy":"Recycle"}}'
				kubectl patch pv "${pv}" -p '{"spec": {"persistentVolumeReclaimPolicy":"Recycle"}}'
				sleep ${SEC_TO_WAIT_PATCH_PV}

				echo "[EXEC] kubectl delete pv ${pv}"
				kubectl delete pv ${pv}
				sleep ${SEC_TO_WAIT_DELETE_PV}
				;;
		esac
	done
fi

echo "[INFO] DELETE EPOCH WORKSPACE CLUSTER ROLE BINDING"
for crb in \
	$( kubectl get ClusterRoleBinding -o jsonpath="{.items[*].metadata.name}")
do
	case "${crb}" in
		trigger-sa-cluster-rolebinding-[0-9]* |\
		argocd-application-controller-[0-9]* |\
		argocd-server-[0-9]*)
			echo "[EXEC] kubectl delete ClusterRoleBinding ${crb}"
			kubectl delete ClusterRoleBinding ${crb}
			;;
	esac
done

echo "[INFO] DELETE EPOCH WORKSPACE CLUSTER ROLE"
for cr in \
	$( kubectl get ClusterRole -o jsonpath="{.items[*].metadata.name}")
do
	case "${cr}" in
		trigger-sa-cluster-role-[0-9]* |\
		argocd-application-controller-[0-9]* |\
		argocd-server-[0-9]*)
			kubectl delete ClusterRole ${cr}
			;;
	esac
done

if [ "${OPTION_TEKTON}" = "ON" ]; then
	echo "[INFO] CHECK TEKTON RESOURCE NOT EXISTS"

	resource_exist="FALSE"
	for cs in \
		$( kubectl get CustomResourceDefinition -o jsonpath="{.items[*].metadata.name}" )
	do
		case "${cs}" in
			"clusterinterceptors.triggers.tekton.dev")
				;;
			*.tekton.dev)
				resource_count=$( kubectl get "${cs}" -A --no-headers 2> /dev/null | wc -l )
				if [ ${resource_count} -gt 0 ]; then
					resource_exist="TRUE"
					echo "[WARN] TEKTON resource (${cs}) remains, so TEKTON will not be deleted"
				fi
				;;
			*)
				;;
		esac
	done
	
	if [ ${resource_exist} = "FALSE" ]; then
		echo "[INFO] DELETE TEKTON"
		echo "[EXEC] kubectl delete -f ${BASEDIR}/source/tekton/tekton-trigger-interceptors.yaml --ignore-not-found"
		kubectl delete -f "${BASEDIR}/source/tekton/tekton-trigger-interceptors.yaml" --ignore-not-found

		echo "[EXEC] kubectl delete -f ${BASEDIR}/source/tekton/tekton-trigger-release.yaml --ignore-not-found"
		kubectl delete -f "${BASEDIR}/source/tekton/tekton-trigger-release.yaml" --ignore-not-found

		echo "[EXEC] kubectl delete -f ${BASEDIR}/source/tekton/tekton-pipeline-release.yaml --ignore-not-found"
		kubectl delete -f "${BASEDIR}/source/tekton/tekton-pipeline-release.yaml" --ignore-not-found
	fi
fi

echo "[INFO] DELETE EPOCH-SYSTEM"
echo "[EXEC] kubectl delete -f ${BASEDIR}/epoch-install.yaml --ignore-not-found"
sleep 1
kubectl delete -f "${BASEDIR}/epoch-install.yaml" --ignore-not-found

if [ "${OPTION_PV}" = "ON" ]; then
	echo "[INFO] DELETE EPOCH-SYSTEM PERSISTENT VOLUME"
	for pv in \
		$(kubectl get pv -o jsonpath="{.items[*].metadata.name}");
	do
		case "${pv}" in
			"epoch-rs-cd-result-db" |\
			"epoch-rs-logs-db" |\
			"epoch-tekton-pipeline-db" |\
			"epoch-tekton-pipelinerun-db" |\
			"epoch-workspace-db" |\
			"exastro-authentication-infra-httpd" |\
			"exastro-platform-authentication-infra-keycloak-db")
				echo "[EXEC] kubectl patch pv ${pv} -p "'{"spec": {"persistentVolumeReclaimPolicy":"Recycle"}}'
				kubectl patch pv "${pv}" -p '{"spec": {"persistentVolumeReclaimPolicy":"Recycle"}}'
				sleep ${SEC_TO_WAIT_PATCH_PV}

				echo "[EXEC] kubectl delete pv ${pv}"
				kubectl delete pv ${pv}
				sleep ${SEC_TO_WAIT_DELETE_PV}
				;;
		esac
	done
fi


if [ "${OPTION_GITLAB}" = "ON" ]; then
	echo "[INFO] DELETE GITLAB"

	kubectl get ns gitlab &> /dev/null
	if [ $? -eq 0 ]; then
		echo "[EXEC] kubectl run uninstall-gitlab-$$ --command bash -- -c helm uninstall gitlab -n gitlab"
		kubectl run -i uninstall-gitlab-$$ -n gitlab \
			--restart=Never \
			--image=exastro/epoch-kube-command:0.1.5_20211026_1600 \
			--pod-running-timeout=30m \
			--serviceaccount=gitlab-installer \
			--command bash \
			-- -c "helm uninstall gitlab -n gitlab --timeout 10m --wait; echo '**** If the process stops here, press CTRL + C ****'"
		sleep 1

		echo "[EXEC] kubectl delete ns gitlab --ignore-not-found"
		kubectl delete ns gitlab --ignore-not-found
	fi

	if [ "${OPTION_PV}" = "ON" ]; then
		for pv in \
			$(kubectl get pv -o jsonpath="{.items[*].metadata.name}");
		do
			case "${pv}" in
				"gitlab-gitaly" |\
				"gitlab-minio" |\
				"gitlab-postgresql" |\
				"gitlab-redis")

					echo "[EXEC] kubectl patch pv ${pv} -p "'{"spec": {"persistentVolumeReclaimPolicy":"Recycle"}}'
					kubectl patch pv "${pv}" -p '{"spec": {"persistentVolumeReclaimPolicy":"Recycle"}}'
					sleep ${SEC_TO_WAIT_PATCH_PV}
					echo "[EXEC] kubectl delete pv ${pv} --ignore-not-found"
					kubectl delete pv ${pv} --ignore-not-found
					sleep ${SEC_TO_WAIT_DELETE_PV}
			esac
		done
	fi
fi

