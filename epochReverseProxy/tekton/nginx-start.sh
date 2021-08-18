#!/bin/bash

if [ ! -d "/etc/nginx/ssl/epoch" ]; then
    mkdir -p "/etc/nginx/ssl/epoch"
fi
if [ ! -f "/etc/nginx/ssl/epoch/ca.key" ]; then
    openssl req -new -x509 -sha256 -newkey rsa:2048 -days 3650 -nodes -out /etc/nginx/ssl/epoch/ca.pem -keyout /etc/nginx/ssl/epoch/ca.key -subj="/C=JP/ST=Tokyo/CN=epoch-reverse-proxy-tekton.epoch-tekton-pipelines.svc"
fi

nginx -g "daemon off;"
