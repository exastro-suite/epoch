#!/bin/bash

echo "[INFO] START: $(basename $0)"

kubectl get secret epoch-key -n epoch-system &> /dev/null
if [ $? -ne 0 ]; then
    echo "[INFO] GENERATE epoch-key"
    ENCRYPT_KEY=$(cat /dev/urandom | base64 | fold -w 16 | head -n 1)
    cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Secret
metadata:
  name: epoch-key
  namespace: epoch-system
stringData:
  ENCRYPT_KEY: "${ENCRYPT_KEY}"
EOF
    if [ $? -ne 0 ]; then
        echo "[ERROR] Failed to GENERATE epoch-key"
        exit 1
    fi
fi

exit 0
