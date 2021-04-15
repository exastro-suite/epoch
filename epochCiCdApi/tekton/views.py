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
import cgi # CGIモジュールのインポート
import cgitb
import sys
import requests
import json
import subprocess
import traceback
import os

from django.shortcuts import render
from django.http import HttpResponse
from django.http.response import JsonResponse

from django.views.decorators.csrf import csrf_exempt

from kubernetes import client, config
import yaml
from pprint import pprint


@csrf_exempt
def index(request):
    if request.method == 'POST':
        return post(request)
    else:
        return ""

@csrf_exempt    
def post(request):
    try:

        resource_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/resource"

        stdout_pl = subprocess.check_output(["kubectl","apply","-f",(resource_dir + "/pipeline-release.yaml")],stderr=subprocess.STDOUT)
        stdout_tg = subprocess.check_output(["kubectl","apply","-f",(resource_dir + "/trigger-release.yaml")],stderr=subprocess.STDOUT)
        stdout_db = subprocess.check_output(["kubectl","apply","-f",(resource_dir + "/dashbord-release.yaml")],stderr=subprocess.STDOUT)

        response = {
            "result":"OK",
            "output" : [
                stdout_pl.decode('utf-8'),
                stdout_tg.decode('utf-8'),
                stdout_db.decode('utf-8'),
            ],
        }
        return JsonResponse(response)

    except subprocess.CalledProcessError as e:
        response = {
            "result":"ERROR",
            "returncode": e.returncode,
            "command": e.cmd,
            "output": e.output.decode('utf-8'),
            "traceback": traceback.format_exc(),
        }
        return JsonResponse(response)


@csrf_exempt
def createComRegistrySecret(request):
    if request.method == 'POST':
        return createComRegistrySecretPost(request)
    else:
        return ""

@csrf_exempt    
def createComRegistrySecretPost(request):
    configuration = config.load_incluster_config()
    with client.ApiClient(configuration) as api_client:
        v1 = client.CoreV1Api(api_client)

    try:
        # 引数で指定されたCD環境を取得
        # print (request.body)
        # request_json = json.loads(request.body)
        # print (request_json)
        # request_kind = request_json["RegistrySecret"]

        # 引数
        api_version = 'v1'
        kind = 'Secret'
        name = 'registry-secret'
        namespace = 'epoch-tekton-pipelines'
        anotation = {"tekton.dev/docker-0": "https://index.docker.io/v2/"}
        secret_type = 'kubernetes.io/basic-auth'
        # string_data = format(request_kind['stringData'])
        string_data = {"username":os.environ['EPOCH_REGISTRY_USER'], "password":os.environ['EPOCH_REGISTRY_PASSWORD']}

        # Secretのbody設定
        metadata = client.V1ObjectMeta(name=name, annotations=anotation)
        body = client.V1Secret(api_version=api_version, kind=kind, metadata=metadata, string_data=string_data, type=secret_type)

        # Secret作成API
        ret = v1.create_namespaced_secret(namespace, body=body)

        response = {
            "result":"OK",
            "output": str(ret),
        }
        return JsonResponse(response)

    except subprocess.CalledProcessError as e:
        response = {
            "result":"ERROR",
            "returncode": e.returncode,
            "command": e.cmd,
            "output": e.output.decode('utf-8'),
            "traceback": traceback.format_exc(),
        }
        return JsonResponse(response)

@csrf_exempt
def createComServiceAccount(request):
    if request.method == 'POST':
        return createComServiceAccountPost(request)
    else:
        return ""

@csrf_exempt    
def createComServiceAccountPost(request):
    configuration = config.load_incluster_config()
    with client.ApiClient(configuration) as api_client:
        v1 = client.CoreV1Api(api_client)

    try:    
        # 引数
        api_version = 'v1'
        kind = 'ServiceAccount'
        name = 'pipeline-account'
        namespace = 'epoch-tekton-pipelines'
        secret_name = 'registry-secret'

        # ServiceAccountのbody設定
        metadata = client.V1ObjectMeta(name=name)
        secret1 = client.V1ObjectReference(name=secret_name, namespace=namespace)
        secrets = [secret1]
        body = client.V1ServiceAccount(api_version=api_version, kind=kind, metadata=metadata, secrets=secrets)

        # ServiceAccount作成API
        ret = v1.create_namespaced_service_account(namespace, body=body)

        response = {
            "result":"OK",
            "output": str(ret),
        }
        return JsonResponse(response)

    except subprocess.CalledProcessError as e:
        response = {
            "result":"ERROR",
            "returncode": e.returncode,
            "command": e.cmd,
            "output": e.output.decode('utf-8'),
            "traceback": traceback.format_exc(),
        }
        return JsonResponse(response)

@csrf_exempt
def createComSecret(request):
    if request.method == 'POST':
        return createComSecretPost(request)
    else:
        return ""

@csrf_exempt    
def createComSecretPost(request):
    configuration = config.load_incluster_config()
    with client.ApiClient(configuration) as api_client:
        v1 = client.CoreV1Api(api_client)

    try:
        # 引数
        api_version = 'v1'
        kind = 'Secret'
        name = 'kube-api-secret'
        namespace = 'epoch-tekton-pipelines'
        anotation = {"kubernetes.io/service-account.name": "pipeline-account"}
        secret_type = 'kubernetes.io/service-account-token'

        # Secretのbody設定
        metadata = client.V1ObjectMeta(name=name, annotations=anotation)
        body = client.V1Secret(api_version=api_version, kind=kind, metadata=metadata, type=secret_type)

        # Secret作成API
        ret = v1.create_namespaced_secret(namespace, body=body)

        response = {
            "result":"OK",
            "output": str(ret),
        }
        return JsonResponse(response)

    except subprocess.CalledProcessError as e:
        response = {
            "result":"ERROR",
            "returncode": e.returncode,
            "command": e.cmd,
            "output": e.output.decode('utf-8'),
            "traceback": traceback.format_exc(),
        }
        return JsonResponse(response)

@csrf_exempt
def createComPv(request):
    if request.method == 'POST':
        return createComPvPost(request)
    else:
        return ""

@csrf_exempt    
def createComPvPost(request):
    configuration = config.load_incluster_config()
    with client.ApiClient(configuration) as api_client:
        v1 = client.CoreV1Api(api_client)

    try:
        # 引数
        api_version = 'v1'
        kind = 'PersistentVolume'
        name = 'epoch-pv'
        labels = {"type":"local"}
        storage_class_name = 'epoch-tekton-pipeline-storage'
        capacity = {"storage":"500Mi"}
        access_mode1 = 'ReadWriteOnce'
        hp_path = '/var/data/epoch-pv'
        hp_type = 'DirectoryOrCreate'
        ex_key = 'kubernetes.io/hostname'
        ex_operator = 'In'
        ex_values = ["epoch-worker1"]

        # PersistentVolumeClaimのbody設定
        ## metadata
        metadata = client.V1ObjectMeta(name=name, labels=labels)

        ## spec / node_affinity / required / node_selector_terms
        match_expression1 = client.V1NodeSelectorRequirement(key=ex_key, operator=ex_operator, values=ex_values)
        match_expressions = [match_expression1]
        node_selector_term1 = client.V1NodeSelectorTerm(match_expressions=match_expressions)

        ## spec / node_affinity / required
        node_selector_terms = [node_selector_term1]
        required = client.V1NodeSelector(node_selector_terms=node_selector_terms)

        ## spec / node_affinity
        node_affinity = client.V1VolumeNodeAffinity(required=required)

        ## spec
        access_modes = [access_mode1]
        host_path = client.V1HostPathVolumeSource(path=hp_path, type=hp_type)
        spec = client.V1PersistentVolumeSpec(storage_class_name=storage_class_name, capacity=capacity, access_modes=access_modes, host_path=host_path, node_affinity=node_affinity)

        ## body
        body = client.V1PersistentVolume(api_version=api_version, kind=kind, metadata=metadata, spec=spec)

        # PersistentVolume作成API
        ret = v1.create_persistent_volume(body=body)

        response = {
            "result":"OK",
            "output": str(ret),
        }
        return JsonResponse(response)

    except subprocess.CalledProcessError as e:
        response = {
            "result":"ERROR",
            "returncode": e.returncode,
            "command": e.cmd,
            "output": e.output.decode('utf-8'),
            "traceback": traceback.format_exc(),
        }
        return JsonResponse(response)

@csrf_exempt
def createComPvc(request):
    if request.method == 'POST':
        return createComPvcPost(request)
    else:
        return ""

@csrf_exempt    
def createComPvcPost(request):
    configuration = config.load_incluster_config()
    with client.ApiClient(configuration) as api_client:
        v1 = client.CoreV1Api(api_client)

    try:
        # 引数
        api_version = 'v1'
        kind = 'PersistentVolumeClaim'
        name = 'workspace-source-pvc'
        namespace = 'epoch-tekton-pipelines'
        labels = {"app":"epoch-tekton-pipeline-claim"}
        access_mode1 = 'ReadWriteOnce'
        requests = {"storage":"500Mi"}
        storage_class_name = 'epoch-tekton-pipeline-storage'

        # PersistentVolumeClaimのbody設定
        metadata = client.V1ObjectMeta(name=name, labels=labels)
        access_modes = [access_mode1]
        resources = client.V1ResourceRequirements(requests=requests)
        spec = client.V1PersistentVolumeClaimSpec(access_modes=access_modes, resources=resources, storage_class_name=storage_class_name)
        body = client.V1PersistentVolumeClaim(api_version=api_version, kind=kind, metadata=metadata, spec=spec)

        # PersistentVolumeClaim作成API
        ret = v1.create_namespaced_persistent_volume_claim(namespace, body=body)

        response = {
            "result":"OK",
            "output": str(ret),
        }
        return JsonResponse(response)

    except subprocess.CalledProcessError as e:
        response = {
            "result":"ERROR",
            "returncode": e.returncode,
            "command": e.cmd,
            "output": e.output.decode('utf-8'),
            "traceback": traceback.format_exc(),
        }
        return JsonResponse(response)

@csrf_exempt
def createComStorageClass(request):
    if request.method == 'POST':
        return createComStorageClassPost(request)
    else:
        return ""

@csrf_exempt    
def createComStorageClassPost(request):
    configuration = config.load_incluster_config()
    with client.ApiClient(configuration) as api_client:
            v1 = client.StorageV1Api(api_client)
        
    try:
        # 引数
        api_version = 'storage.k8s.io/v1'
        kind = 'StorageClass'
        name = 'epoch-tekton-pipeline-storage'
        provisioner = 'kubernetes.io/no-provisioner'
        volume_binding_mode = 'WaitForFirstConsumer'

        # StorageClassのbody設定
        metadata = client.V1ObjectMeta(name=name)
        body = client.V1StorageClass(api_version=api_version, kind=kind, metadata=metadata, provisioner=provisioner, volume_binding_mode=volume_binding_mode)

        # StorageClass作成API
        ret = v1.create_storage_class(body=body)

        response = {
            "result":"OK",
            "output": str(ret),
        }
        return JsonResponse(response)

    except subprocess.CalledProcessError as e:
        response = {
            "result":"ERROR",
            "returncode": e.returncode,
            "command": e.cmd,
            "output": e.output.decode('utf-8'),
            "traceback": traceback.format_exc(),
        }
        return JsonResponse(response)

@csrf_exempt
def createComRole(request):
    if request.method == 'POST':
        return createComRolePost(request)
    else:
        return ""

@csrf_exempt    
def createComRolePost(request):
    configuration = config.load_incluster_config()
    with client.ApiClient(configuration) as api_client:
        v1 = client.RbacAuthorizationV1Api(api_client)

    try:
        # 引数
        api_version = 'rbac.authorization.k8s.io/v1'
        kind = 'Role'
        name = 'pipeline-role'
        namespace = 'epoch-tekton-pipelines'
        r1_api_groups = [""]
        r2_api_groups = ["apps"]
        r3_api_groups = ["triggers.tekton.dev"]
        r4_api_groups = [""]
        r5_api_groups = ["tekton.dev"]
        r1_resources = ["services"]
        r2_resources = ["deployments"]
        r3_resources = ["eventlisteners", "triggerbindings", "triggertemplates", "triggers"]
        r4_resources = ["configmaps", "secrets"]
        r5_resources = ["pipelineruns", "pipelineresources", "taskruns"]
        r1_verbs = ["get", "create", "update", "patch"]
        r2_verbs = ["get", "create", "update", "patch"]
        r3_verbs = ["get"]
        r4_verbs = ["get", "list", "watch"]
        r5_verbs = ["create"]

        # Roleのbody設定
        metadata = client.V1ObjectMeta(name=name)
        rule1 = client.V1PolicyRule(api_groups=r1_api_groups, resources=r1_resources, verbs=r1_verbs)
        rule2 = client.V1PolicyRule(api_groups=r2_api_groups, resources=r2_resources, verbs=r2_verbs)
        rule3 = client.V1PolicyRule(api_groups=r3_api_groups, resources=r3_resources, verbs=r3_verbs)
        rule4 = client.V1PolicyRule(api_groups=r4_api_groups, resources=r4_resources, verbs=r4_verbs)
        rule5 = client.V1PolicyRule(api_groups=r5_api_groups, resources=r5_resources, verbs=r5_verbs)
        rules = [rule1, rule2, rule3, rule4, rule5]
        body = client.V1Role(api_version=api_version, kind=kind ,metadata=metadata, rules=rules)

        # Role作成API
        ret = v1.create_namespaced_role(namespace, body=body)

        response = {
            "result":"OK",
            "output": str(ret),
        }
        return JsonResponse(response)

    except subprocess.CalledProcessError as e:
        response = {
            "result":"ERROR",
            "returncode": e.returncode,
            "command": e.cmd,
            "output": e.output.decode('utf-8'),
            "traceback": traceback.format_exc(),
        }
        return JsonResponse(response)

@csrf_exempt
def createComRoleBinding(request):
    if request.method == 'POST':
        return createComRoleBindingPost(request)
    else:
        return ""

@csrf_exempt    
def createComRoleBindingPost(request):
    configuration = config.load_incluster_config()
    with client.ApiClient(configuration) as api_client:
        v1 = client.RbacAuthorizationV1Api(api_client)

    try:
        # 引数
        api_version = 'rbac.authorization.k8s.io/v1'
        kind = 'RoleBinding'
        name = 'pipeline-role-binding'
        namespace = 'epoch-tekton-pipelines'
        rr_api_group = 'rbac.authorization.k8s.io'
        rr_kind = 'Role'
        rr_name = 'pipeline-role'
        sj_kind = 'ServiceAccount'
        sj_name = 'pipeline-account'

        # RoleBindingのbody設定
        metadata = client.V1ObjectMeta(name=name)
        role_ref = client.V1RoleRef(api_group=rr_api_group, kind=rr_kind, name=rr_name)
        subject1 = client.V1Subject(kind=sj_kind, name=sj_name, namespace=namespace)
        subjects = [subject1]
        body = client.V1RoleBinding(metadata=metadata, role_ref=role_ref, subjects=subjects)

        # RoleBinding作成API
        ret = v1.create_namespaced_role_binding(namespace, body=body)

        response = {
            "result":"OK",
            "output": str(ret),
        }
        return JsonResponse(response)

    except subprocess.CalledProcessError as e:
        response = {
            "result":"ERROR",
            "returncode": e.returncode,
            "command": e.cmd,
            "output": e.output.decode('utf-8'),
            "traceback": traceback.format_exc(),
        }
        return JsonResponse(response)

@csrf_exempt
def createTriggerClusterRole(request):
    if request.method == 'POST':
        return createTriggerClusterRolePost(request)
    else:
        return ""

@csrf_exempt    
def createTriggerClusterRolePost(request):
    configuration = config.load_incluster_config()
    with client.ApiClient(configuration) as api_client:
        v1 = client.RbacAuthorizationV1Api(api_client)

    try:
        # 引数
        kind = 'ClusterRole'
        api_version = 'rbac.authorization.k8s.io/v1'
        name = 'tekton-triggers-clusterrole'
        r1_api_groups = ["triggers.tekton.dev"]
        r1_resources = ["clustertriggerbindings"]
        r1_verbs = ["get", "list", "watch"]

        # ClusterRoleのbody設定
        metadata = client.V1ObjectMeta(name=name)
        rule1 = client.V1PolicyRule(api_groups=r1_api_groups, resources=r1_resources, verbs=r1_verbs)
        rules = [rule1]
        body = client.V1ClusterRole(api_version=api_version, kind=kind ,metadata=metadata, rules=rules)

        # ClusterRole作成API
        ret = v1.create_cluster_role(body=body)

        response = {
            "result":"OK",
            "output": str(ret),
        }
        return JsonResponse(response)

    except subprocess.CalledProcessError as e:
        response = {
            "result":"ERROR",
            "returncode": e.returncode,
            "command": e.cmd,
            "output": e.output.decode('utf-8'),
            "traceback": traceback.format_exc(),
        }
        return JsonResponse(response)

@csrf_exempt
def createTriggerClusterRoleBinding(request):
    if request.method == 'POST':
        return createTriggerClusterRoleBindingPost(request)
    else:
        return ""

@csrf_exempt    
def createTriggerClusterRoleBindingPost(request):
    configuration = config.load_incluster_config()
    with client.ApiClient(configuration) as api_client:
        v1 = client.RbacAuthorizationV1Api(api_client)

    try:
        # 引数
        namespace = 'epoch-tekton-pipelines'
        api_version = 'rbac.authorization.k8s.io/v1'
        kind = 'ClusterRoleBinding'
        name = 'tekton-triggers-clusterbinding'
        sj_kind = 'ServiceAccount'
        sj_name = 'tekton-triggers-sa'
        rr_api_group = 'rbac.authorization.k8s.io'
        rr_kind = 'ClusterRole'
        rr_name = 'tekton-triggers-clusterrole'

        # ClusterRoleBindingのbody設定
        metadata = client.V1ObjectMeta(name=name)
        role_ref = client.V1RoleRef(api_group=rr_api_group, kind=rr_kind, name=rr_name)
        subject1 = client.V1Subject(kind=sj_kind, name=sj_name, namespace=namespace)
        subjects = [subject1]
        body = client.V1ClusterRoleBinding(metadata=metadata, role_ref=role_ref, subjects=subjects)

        # ClusterRoleBinding作成API
        ret = v1.create_cluster_role_binding(body=body)

        response = {
            "result":"OK",
            "output": str(ret),
        }
        return JsonResponse(response)

    except subprocess.CalledProcessError as e:
        response = {
            "result":"ERROR",
            "returncode": e.returncode,
            "command": e.cmd,
            "output": e.output.decode('utf-8'),
            "traceback": traceback.format_exc(),
        }
        return JsonResponse(response)

@csrf_exempt
def createTiggerRole(request):
    if request.method == 'POST':
        return createTriggerRolePost(request)
    else:
        return ""

@csrf_exempt    
def createTriggerRolePost(request):
    configuration = config.load_incluster_config()
    with client.ApiClient(configuration) as api_client:
        v1 = client.RbacAuthorizationV1Api(api_client)

    try:
        # 引数
        api_version = 'rbac.authorization.k8s.io/v1'
        kind = 'Role'
        name = 'tekton-triggers-minimal'
        namespace = 'epoch-tekton-pipelines'
        r1_api_groups = ["triggers.tekton.dev"]
        r2_api_groups = [""]
        r3_api_groups = ["tekton.dev"]
        r4_api_groups = [""]
        r5_api_groups = ["policy"]
        r1_resources = ["eventlisteners", "triggerbindings", "triggertemplates", "triggers"]
        r2_resources = ["configmaps", "secrets"]
        r3_resources = ["pipelineruns", "pipelineresources", "taskruns"]
        r4_resources = ["serviceaccounts"]
        r5_resources = ["podsecuritypolicies"]
        r5_resource_names = ["tekton-triggers"]
        r1_verbs = ["get", "list", "watch"]
        r2_verbs = ["get", "list", "watch"]
        r3_verbs = ["create"]
        r4_verbs = ["impersonate"]
        r5_verbs = ["use"]

        # Roleのbody設定
        metadata = client.V1ObjectMeta(name=name)
        rule1 = client.V1PolicyRule(api_groups=r1_api_groups, resources=r1_resources, verbs=r1_verbs)
        rule2 = client.V1PolicyRule(api_groups=r2_api_groups, resources=r2_resources, verbs=r2_verbs)
        rule3 = client.V1PolicyRule(api_groups=r3_api_groups, resources=r3_resources, verbs=r3_verbs)
        rule4 = client.V1PolicyRule(api_groups=r4_api_groups, resources=r4_resources, verbs=r4_verbs)
        rule5 = client.V1PolicyRule(api_groups=r5_api_groups, resources=r5_resources, resource_names=r5_resource_names, verbs=r5_verbs)
        rules = [rule1, rule2, rule3, rule4, rule5]
        body = client.V1Role(api_version=api_version, kind=kind ,metadata=metadata, rules=rules)

        # Role作成API
        ret = v1.create_namespaced_role(namespace, body=body)

        response = {
            "result":"OK",
            "output": str(ret),
        }
        return JsonResponse(response)

    except subprocess.CalledProcessError as e:
        response = {
            "result":"ERROR",
            "returncode": e.returncode,
            "command": e.cmd,
            "output": e.output.decode('utf-8'),
            "traceback": traceback.format_exc(),
        }
        return JsonResponse(response)

@csrf_exempt
def createTiggerRoleBinding(request):
    if request.method == 'POST':
        return createTriggerRoleBindingPost(request)
    else:
        return ""

@csrf_exempt    
def createTriggerRoleBindingPost(request):
    configuration = config.load_incluster_config()
    with client.ApiClient(configuration) as api_client:
        v1 = client.RbacAuthorizationV1Api(api_client)

    try:
        # 引数
        api_version = 'rbac.authorization.k8s.io/v1'
        kind = 'RoleBinding'
        name = 'tekton-triggers-binding'
        namespace = 'epoch-tekton-pipelines'
        sj_kind = 'ServiceAccount'
        sj_name = 'tekton-triggers-sa'
        rr_api_group = 'rbac.authorization.k8s.io'
        rr_kind = 'Role'
        rr_name = 'tekton-triggers-minimal'

        # RoleBindingのbody設定
        metadata = client.V1ObjectMeta(name=name)
        role_ref = client.V1RoleRef(api_group=rr_api_group, kind=rr_kind, name=rr_name)
        subject1 = client.V1Subject(kind=sj_kind, name=sj_name, namespace=namespace)
        subjects = [subject1]
        body = client.V1RoleBinding(metadata=metadata, role_ref=role_ref, subjects=subjects)

        # RoleBinding作成API
        ret = v1.create_namespaced_role_binding(namespace, body=body)

        response = {
            "result":"OK",
            "output": str(ret),
        }
        return JsonResponse(response)

    except subprocess.CalledProcessError as e:
        response = {
            "result":"ERROR",
            "returncode": e.returncode,
            "command": e.cmd,
            "output": e.output.decode('utf-8'),
            "traceback": traceback.format_exc(),
        }
        return JsonResponse(response)

@csrf_exempt
def createTiggerServiceAccount(request):
    if request.method == 'POST':
        return createTriggerServiceAccountPost(request)
    else:
        return ""

@csrf_exempt    
def createTriggerServiceAccountPost(request):
    configuration = config.load_incluster_config()
    with client.ApiClient(configuration) as api_client:
        v1 = client.CoreV1Api(api_client)

    try:
        # 引数
        api_version = 'v1'
        kind = 'ServiceAccount'
        name = 'tekton-triggers-sa'
        namespace = 'epoch-tekton-pipelines'

        # ServiceAccountのbody設定
        metadata = client.V1ObjectMeta(name=name)
        body = client.V1ServiceAccount(api_version=api_version, kind=kind, metadata=metadata)

        # ServiceAccount作成API
        ret = v1.create_namespaced_service_account(namespace, body=body)

        response = {
            "result":"OK",
            "output": str(ret),
        }
        return JsonResponse(response)

    except subprocess.CalledProcessError as e:
        response = {
            "result":"ERROR",
            "returncode": e.returncode,
            "command": e.cmd,
            "output": e.output.decode('utf-8'),
            "traceback": traceback.format_exc(),
        }
        return JsonResponse(response)

@csrf_exempt
def createTiggerSecret(request):
    if request.method == 'POST':
        return createTriggerSecretPost(request)
    else:
        return ""

@csrf_exempt    
def createTriggerSecretPost(request):
    configuration = config.load_incluster_config()
    with client.ApiClient(configuration) as api_client:
        v1 = client.CoreV1Api(api_client)

    try:
        # 引数
        api_version = 'v1'
        kind = 'Secret'
        name = 'gitlab-secret'
        namespace = 'epoch-tekton-pipelines'
        secret_type = 'Opaque'
        string_data = {"secretToken":os.environ['EPOCH_WEBHOOK_TOKEN']}

        # Secretのbody設定
        metadata = client.V1ObjectMeta(name=name)
        body = client.V1Secret(api_version=api_version, kind=kind, metadata=metadata, string_data=string_data, type=secret_type)

        # Secret作成API
        ret = v1.create_namespaced_secret(namespace, body=body)

        response = {
            "result":"OK",
            "output": str(ret),
        }
        return JsonResponse(response)

    except subprocess.CalledProcessError as e:
        response = {
            "result":"ERROR",
            "returncode": e.returncode,
            "command": e.cmd,
            "output": e.output.decode('utf-8'),
            "traceback": traceback.format_exc(),
        }
        return JsonResponse(response)
