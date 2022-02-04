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

LOGFILE="/var/log/epoch/epoch-setting-tools.log.`TZ=JST-9 date '+%Y%m%d'`"
_LOGNAME=$1

function logger() {
    LOG_LEVEL=$1
    LOG_MESSAGE=$2
    LOG_TEXT="[`TZ=JST-9 date '+%Y/%m/%d %H:%M:%S'`][${_LOGNAME}][${LOG_LEVEL}] ${LOG_MESSAGE}"
    if [ "${LOG_LEVEL}" != "DEBUG" ]; then
        echo "[${LOG_LEVEL}] ${LOG_MESSAGE}"
    fi
    echo "${LOG_TEXT}" > /proc/1/fd/1
    echo "${LOG_TEXT}" >> "${LOGFILE}"
}

