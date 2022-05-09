#!/bin/bash

echo "[INFO] START: $(basename $0)"

SCRIPT_PATH=$(dirname $0)

kubectl get pod -n "${PRM_NAMESPACE}" "${HOSTNAME}" &> /dev/null
if [ $? -ne 0 ]; then
    echo "[ERROR] Not Found Pod : namespace=${PRM_NAMESPACE} jobname=${PRM_JOBNAME} hostname=${HOSTNAME}"
    exit 1
fi

WORKER_NODE_NAME=$(kubectl get pod -n "${PRM_NAMESPACE}" "${HOSTNAME}" -o jsonpath="{.spec.nodeName}")
echo "WORKER_NODE_NAME:${WORKER_NODE_NAME}"

if [ -z "${WORKER_NODE_NAME}" ]; then
    echo "[ERROR] Could not get the node name : namespace=${PRM_NAMESPACE} jobname=${PRM_JOBNAME}"
    exit 1
fi

IFS=, PRM_PV_BEFORE_DELETE_ARR=(${PRM_PV_BEFORE_DELETE})
for PV in "${PRM_PV_BEFORE_DELETE_ARR[@]}"; do
    STATUS=""
    STATUS=$(kubectl get pv "${PV}" -o jsonpath='{.status.phase}')
    if [ $? -ne 0 ]; then
        continue
    fi
    if [ "${STATUS}" = "Released" ]; then
        kubectl delete pv "${PV}"
    fi
done

sed -e "s/#WORKER-NODE-NAME#/${WORKER_NODE_NAME}/g" "${SCRIPT_PATH}/${PRM_PV_TEMPLATE}" | \
kubectl apply -f -
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to create Persistent Volume : namespace=${PRM_NAMESPACE} jobname=${PRM_JOBNAME}"
    exit 1
fi

kubectl delete job -n "${PRM_NAMESPACE}" "${PRM_JOBNAME}"
