#!/bin/sh

set -e

envsubst '${API_PATH} ${WS_PATH}' < /usr/share/nginx/html/config.template.js > /usr/share/nginx/html/config.js

envsubst '${BACKEND_URL}' < /etc/nginx/templates/default.conf.template > /etc/nginx/conf.d/default.conf

exec "$@"