/*
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
*/
var workspace_api_conf = {
    "links" : {
        "registry"  : "https://hub.docker.com/repositories",
        // "ita"       : location_prot + "//" + location_host + ":" + (location_prot == "https:"? "31183": "31183") + "/default/menu/01_browse.php?no=2100180006",
        // "sonarqube" : location_prot + "//" + location_host + ":" + (location_prot == "https:"? "31185": "31185") + "/",
        "ita"       : "{baseurl}/default/menu/01_browse.php?no=2100180006",
        "sonarqube" : "{baseurl}",
    },
    "test": {
        "default_workspace_id": 1
    },
    "api" : {
        "resource": {
            "get" :     URL_BASE + "/api/workspace/{workspace_id}",
            "post" :    URL_BASE + "/api/workspace",
            "put" :     URL_BASE + "/api/workspace/{workspace_id}",
        },
        "client": {
            "get" :     URL_BASE + "/api/client/{client_id}",
            "client_id": {
                "ita": "epoch-ws-{workspace_id}-ita",
                "argo": "epoch-ws-{workspace_id}-argocd",
                "sonarqube": "epoch-ws-{workspace_id}-sonarqube"
            }
        },
        "workspace": {
            "post":     URL_BASE + "/api/workspace/{workspace_id}/pod",
            //"wait": 30000,
            "wait": 0,
        },
        "ci_pipeline": {
            "post":     URL_BASE + "/api/workspace/{workspace_id}/ci/pipeline",
        },
        "cd_pipeline": {
            "post":     URL_BASE + "/api/workspace/{workspace_id}/cd/pipeline",
        },
        "manifestParameter": {
            "post":     URL_BASE + "/api/workspace/{workspace_id}/manifest/parameter",
        },
        "manifestTemplate": {
            "post" :    URL_BASE + "/api/workspace/{workspace_id}/manifest/template",
            "get" :     URL_BASE + "/api/workspace/{workspace_id}/manifest/template",
            "delete" :  URL_BASE + "/api/workspace/{workspace_id}/manifest/template/{file_id}",
        },
        "cdExecDesignation": {
            "post" :    URL_BASE + "/api/workspace/{workspace_id}/cd/exec",
        },
        "ciResult": {
            "nop" : {
                "get" : URL_BASE + "/api/alive"
            },
            "pipelinerun": {
                "get" :    URL_BASE + "/api/workspace/{workspace_id}/ci/pipeline/result",
            },
            "taskrunlogs": {
                "get" :    URL_BASE + "/api/workspace/{workspace_id}/ci/pipeline/result/{taskrun_name}/logs",
            }
        }
    }
}
const ci_result_polling_span = 10000; // 10s
