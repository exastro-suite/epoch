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
&&  curl -LO https://github.com/tektoncd/cli/releases/download/v0.18.0/tkn_0.18.0_Linux_x86_64.tar.gz \
&&  tar xvzf tkn_0.18.0_Linux_x86_64.tar.gz -C /usr/local/bin/ tkn \
&&  ln -s /usr/local/bin/tkn /usr/local/bin/kubectl-tkn \
&&  echo "INSTALL FINISH"

WORKDIR /app
COPY ./ /app/

RUN echo "RUN START"

CMD ["python3", "/app/api_tekton.py"]

