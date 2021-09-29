#!/bin/bash

# default
APP_NAME="epoch-application"
NAMESPACE="epoch-namespace"

# rewrite APP_NAME and NAMESPACE
# mount this file using manifest
source /app/epochSettings/appCertificateSetting.sh

if [ ! -d "/etc/nginx/ssl/epoch" ]; then
  mkdir -p "/etc/nginx/ssl/epoch"
fi
if [ ! -f "/etc/nginx/ssl/epoch/ca.key" ]; then
  openssl req -new \
    -x509 -sha256 -newkey rsa:2048 \
    -days 3650 \
    -nodes \
    -out /etc/nginx/ssl/epoch/ca.pem \
    -keyout /etc/nginx/ssl/epoch/ca.key \
    -subj="/C=JP/ST=Tokyo/CN=${APP_NAME}.${NAMESPACE}.svc"
fi

nginx -g "daemon off;"
