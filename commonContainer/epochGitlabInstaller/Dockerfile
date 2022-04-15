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
FROM exastro/epoch-kube-command:0.1.5_20211026_1600

WORKDIR /installer/chart
COPY ./gitlab-5.6.2.tgz /installer/chart

WORKDIR /installer/script
COPY ./gitlab-config.yaml               /installer/script
COPY ./gitlab-installer.sh              /installer/script
COPY ./gitlab-pv-template.yaml          /installer/script
COPY ./gitlab-root-token-template.yaml  /installer/script

RUN chmod +x /installer/script/gitlab-installer.sh
WORKDIR /installer

ENTRYPOINT  ["/installer/script/gitlab-installer.sh"]
