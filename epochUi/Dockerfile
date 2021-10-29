FROM	nginx

RUN	apt-get	update	\
&&	apt-get -y install	git

WORKDIR /app

COPY ./ /app/

RUN     chmod +x /app/nginx-start.sh \
&&      cp /app/epochui.conf /etc/nginx/conf.d/.

CMD ["/bin/sh","/app/nginx-start.sh"]
