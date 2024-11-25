#!/bin/bash

docker-compose down

git checkout .
git pull

NGINX_CONF="./nginx.conf"

if [[ ! -f "$NGINX_CONF" ]]; then
    echo "error: nginx.conf not found"
    exit 1
fi

sed -i 's/\$scheme/https/g' "$NGINX_CONF"

docker-compose up --build -d
