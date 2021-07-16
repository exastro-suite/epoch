FROM	nginx

RUN	apt-get	update	\
&&	apt-get -y install	git

WORKDIR /app

RUN	git clone -b main https://github.com/exastro-suite/epoch.git

RUN	echo	"server {"			>	/etc/nginx/conf.d/epochui.conf \
&&	echo	"  listen    8000;"		>>	/etc/nginx/conf.d/epochui.conf \
&&	echo	"  location  / {"		>>	/etc/nginx/conf.d/epochui.conf \
&&	echo	"    root /app/epoch/epochUi;"	>>	/etc/nginx/conf.d/epochui.conf \
&&	echo	"  }"				>>	/etc/nginx/conf.d/epochui.conf \
&&	echo	"}"				>>	/etc/nginx/conf.d/epochui.conf \
