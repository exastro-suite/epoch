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
&&  curl -LO -k "https://storage.googleapis.com/kubernetes-release/release/$(curl -s -k https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/linux/amd64/kubectl" \
&&  chmod +x ./kubectl \
&&  mv ./kubectl /usr/local/bin/kubectl \
&&  echo "RUN FINISH"

WORKDIR /app

RUN echo "RUN START"  \
&&  git clone -b main "https://github.com/exastro-suite/epoch.git"

CMD ["python3", "/app/epoch/epochServiceApi/manage.py", "runserver", "0.0.0.0:8000"]

