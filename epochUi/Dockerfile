FROM	nginx

RUN	apt-get	update	\
&&	apt-get -y install	git

WORKDIR /app

RUN	git clone -b main https://github.com/exastro-suite/epoch.git

RUN     chmod +x /app/epoch/epochUi/nginx-start.sh \
&&      cp /app/epoch/epochUi/epochui.conf /etc/nginx/conf.d/.

CMD ["/bin/sh","/app/epoch/epochUi/nginx-start.sh"]
