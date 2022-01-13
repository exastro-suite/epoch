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
FROM	nginx

RUN	apt-get	update	\
&&	apt-get -y install	git

WORKDIR /app

COPY ./ /app/

RUN     chmod +x /app/nginx-start.sh \
&&      cp /app/epochui.conf /etc/nginx/conf.d/.

CMD ["/bin/sh","/app/nginx-start.sh"]
