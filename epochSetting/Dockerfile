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

COPY ./command /usr/local/bin

RUN chmod +x /usr/local/bin/*

# TEST
ENTRYPOINT ["/bin/sh", "-c", "while :; do sleep 10; done"]
