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

if [ $# -ne 1 ]; then
    echo "Usage : `basename $0` workspace_id"
    exit 1
fi

kubectl exec -i -n epoch-system deploy/workspace-db -- mysql -N -B -u root -ppassword workspace_db -e"select info from workspace_access where workspace_id=$1;"  2> /dev/null | jq

