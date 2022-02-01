FROM    ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Tokyo

RUN apt-get -y update   \
&&  apt-get -y upgrade  \
&&  apt-get -y install \
    locales \
    curl \
    git \
    vim \
    wget \
    unzip \
    openssh-server \
    sudo \
    python3 \
&&  useradd -m epoch \
&&  echo "epoch:epoch" | chpasswd \
&&  echo "epoch ALL=NOPASSWD: ALL" >> /etc/sudoers \
&&  mkdir /run/sshd

RUN git config --global http.sslVerify false

CMD ["/usr/sbin/sshd", "-De"]



