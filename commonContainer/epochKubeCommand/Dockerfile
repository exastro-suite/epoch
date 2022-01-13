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
FROM    ubuntu

RUN apt-get -y update \
&&  apt-get -y install \
    curl \
    wget \
    jq \
    cl-base64 \
&&  curl -LO -k "https://storage.googleapis.com/kubernetes-release/release/$(curl -s -k https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/linux/amd64/kubectl" \
&&  chmod +x ./kubectl \
&&  mv ./kubectl /usr/local/bin/kubectl \
&&  curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 \
&&  chmod 700 get_helm.sh \
&&  ./get_helm.sh

WORKDIR /root
ENTRYPOINT ["/bin/sh", "-c", "while :; do sleep 10; done"]
