FROM    ubuntu:18.04

RUN echo "RUN START"  \
&&  apt-get -y update   \
&&  apt-get -y upgrade  \
&&  apt-get -y install \
    locales \
    curl \
    python3-distutils \
    git \
    vim \
#    sudo \
    wget \
    unzip \
&&  curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py \
&&  python3 get-pip.py \
&&  pip install -U pip \
&&  pip install django \
&&  pip install requests \
&&  pip install kubernetes \
&&  python3 -m pip install markdown \
&&  python3 -m pip install django-filter \
&&  pip install djangorestframework \
&&  pip install django-cors-headers \
&&  pip install bcrypt \
&&  python3 -m pip install pytz \
&&  curl -LO -k "https://storage.googleapis.com/kubernetes-release/release/$(curl -s -k https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/linux/amd64/kubectl" \
&&  chmod +x ./kubectl \
&&  mv ./kubectl /usr/local/bin/kubectl \
&&  VERSION=$(curl --silent "https://api.github.com/repos/argoproj/argo-cd/releases/latest" | grep '"tag_name"' | sed -E 's/.*"([^"]+)".*/\1/') \
&&  curl -sSL -k -o /usr/local/bin/argocd https://github.com/argoproj/argo-cd/releases/download/$VERSION/argocd-linux-amd64 \
&&  chmod +x /usr/local/bin/argocd \
&&  curl -sSL -k -o /usr/local/bin/kubectl-argo-rollouts https://github.com/argoproj/argo-rollouts/releases/latest/download/kubectl-argo-rollouts-darwin-amd64 \
&&  chmod +x /usr/local/bin/kubectl-argo-rollouts \
&&  rm -rf /var/lib/apt/lists/* \
&&  echo "RUN FINISH"

WORKDIR /app

COPY ./ /app/

RUN echo "RUN START"  

CMD ["python3", "-u", "/app/manage.py", "runserver", "0.0.0.0:8000"]

