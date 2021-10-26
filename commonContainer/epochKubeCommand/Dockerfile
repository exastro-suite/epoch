FROM    ubuntu

RUN apt-get -y update \
&&  apt-get -y install \
    curl \
    wget \
    jq \
    cl-base64 \
&&  curl -LO -k "https://storage.googleapis.com/kubernetes-release/release/$(curl -s -k https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/linux/amd64/kubectl" \
&&  chmod +x ./kubectl \
&&  mv ./kubectl /usr/local/bin/kubectl