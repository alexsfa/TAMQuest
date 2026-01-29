#!/bin/sh
envsubst '$DOMAIN_NAME $SSL_FULLCHAIN_LOCATION $SSL_PRIVKEY_LOCATION' \
  < /etc/nginx/conf.d/default.conf.template \
  > /etc/nginx/conf.d/default.conf

exec nginx -g 'daemon off;'