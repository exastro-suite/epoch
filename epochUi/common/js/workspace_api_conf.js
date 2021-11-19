var workspace_api_conf = {
    "links" : {
        "registry"  : "https://hub.docker.com/repositories",
        // "argo"      : location_prot + "//" + location_host + ":" + "31184" + "/",
        // "ita"       : location_prot + "//" + location_host + ":" + (location_prot == "https:"? "31183": "31183") + "/default/menu/01_browse.php?no=2100180006",
        // "sonarqube" : location_prot + "//" + location_host + ":" + (location_prot == "https:"? "31185": "31185") + "/",
        "argo"      : "{baseurl}",
        "ita"       : "{baseurl}/default/menu/01_browse.php?no=2100180006",
        "sonarqube" : "{baseurl}",
    },
    "test": {
        "default_workspace_id": 1
    },
    "api" : {
        "resource": {
            "get" :     URL_BASE + "/api2/workspace/{workspace_id}",
            //"get" :     URL_BASE + "/api/workspace/info/{workspace_id}/",
            "post" :    URL_BASE + "/api2/workspace",
            "put" :     URL_BASE + "/api2/workspace/{workspace_id}",
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
            "post":     URL_BASE + "/api/workspace/pod/",
            "wait": 30000,
        },
        "pipeline": {
            "post":     URL_BASE + "/api/pipeline/",
        },
        "pipelineParameter": {
            "post":     URL_BASE + "/api/pipelineParameter/",
        },
        "manifestParameter": {
            "post":     URL_BASE + "/api/workspace/{workspace_id}/manifestParameter",
        },
        "manifestTemplate": {
            "post" :    URL_BASE + "/api/workspace/{workspace_id}/manifests/",
            "get" :     URL_BASE + "/api/workspace/{workspace_id}/manifests/",
            "delete" :  URL_BASE + "/api/workspace/{workspace_id}/manifests/{file_id}",
        },
        "cdExecDesignation": {
            "post" :    URL_BASE + "/api/cdExecDesignation/",
        },
        "ciResult": {
            "pipelinerun": {
                "get" :    URL_BASE + "/api/ciResult/workspace/{workspace_id}/tekton/pipelinerun",
            },
            "taskrunlogs": {
                "get" :    URL_BASE + "/api/ciResult/workspace/{workspace_id}/tekton/taskrun/{taskrun_name}/logs",
            }
        }
    }
}
const ci_result_polling_span = 10000; // 10s
