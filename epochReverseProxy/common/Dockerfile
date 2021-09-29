FROM	nginx

WORKDIR /app

COPY    nginx-start.sh /app/
COPY    epochReverseProxyBridge.conf /app/

RUN     chmod +x /app/nginx-start.sh \
&&      cp /app/epochReverseProxyBridge.conf /etc/nginx/conf.d/.

CMD ["/bin/bash","/app/nginx-start.sh"]
