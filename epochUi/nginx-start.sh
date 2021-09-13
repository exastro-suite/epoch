#!/bin/bash
#   Copyright 2021 NEC Corporation
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

if [ ! -d "/etc/nginx/ssl/epoch" ]; then
    mkdir -p "/etc/nginx/ssl/epoch"
fi
if [ ! -f "/etc/nginx/ssl/epoch/ca.key" ]; then
    openssl req -new -x509 -sha256 -newkey rsa:2048 -days 3650 -nodes -out /etc/nginx/ssl/epoch/ca.pem -keyout /etc/nginx/ssl/epoch/ca.key -subj="/C=JP/ST=Tokyo/CN=epoch-ui.epoch-system.svc"
fi

nginx -g "daemon off;"
