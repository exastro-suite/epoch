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
FROM    exastro/epoch-api-base:0.1

RUN echo "INSTALL START"  \
&&  pip install bcrypt \
&&  VERSION=$(curl --silent "https://api.github.com/repos/argoproj/argo-cd/releases/latest" | grep '"tag_name"' | sed -E 's/.*"([^"]+)".*/\1/') \
&&  curl -sSL -k -o /usr/local/bin/argocd https://github.com/argoproj/argo-cd/releases/download/$VERSION/argocd-linux-amd64 \
&&  chmod +x /usr/local/bin/argocd \
&&  curl -sSL -k -o /usr/local/bin/kubectl-argo-rollouts https://github.com/argoproj/argo-rollouts/releases/latest/download/kubectl-argo-rollouts-darwin-amd64 \
&&  chmod +x /usr/local/bin/kubectl-argo-rollouts \
&&  echo "INSTALL FINISH"

WORKDIR /app
COPY ./ /app/

RUN echo "RUN START"

CMD ["python3", "/app/api_argocd.py"]

