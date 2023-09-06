#!/usr/bin/env bash
set -o errexit
set -o nounset
set -o xtrace

source .env.sh
printenv

compose_name=compose.development.yml
if [[ "$DOCKER_NO_CACHE" == "true" ]]
    then
    docker-compose -f ${compose_name} rm -f
    docker-compose -f ${compose_name} build --pull --no-cache
fi

docker-compose -f ${compose_name} up --force-recreate --build --remove-orphans
