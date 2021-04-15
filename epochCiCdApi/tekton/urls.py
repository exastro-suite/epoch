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
from django.urls import path, include
from . import views
from . import viewsPipeline
#from . import createTriggerYaml

urlpatterns = [
    path('', views.index),
    path('common/registry/Secret', views.createComRegistrySecret),
    path('common/ServiceAccount', views.createComServiceAccount),
    path('common/Secret', views.createComSecret),
    path('common/Pv', views.createComPv),
    path('common/Pvc', views.createComPvc),
    path('common/StorageClass', views.createComStorageClass),
    path('common/Role', views.createComRole),
    path('common/RoleBinding', views.createComRoleBinding),

    # パイプライン設定
    path('pipeline', viewsPipeline.index),
#    path('trigger', createTriggerYaml.index),
    path('trigger/ClusterRole', views.createTriggerClusterRole),
    path('trigger/ClusterRoleBinding', views.createTriggerClusterRoleBinding),
    path('trigger/Role', views.createTiggerRole),
    path('trigger/RoleBinding', views.createTiggerRoleBinding),
    path('trigger/ServiceAccount', views.createTiggerServiceAccount),
    path('trigger/Secret', views.createTiggerSecret),
]
