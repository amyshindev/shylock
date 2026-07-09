#!/usr/bin/env bash
# Remote deploy helpers for aws2.
# Load from ~/.bash_aliases:
#   source "$HOME/shylock/scripts/deploy-aliases.sh"

_shylock_remote_build_env='export DOCKER_BUILDKIT=1 COMPOSE_DOCKER_CLI_BUILD=1'

shylock-deploy() {
  ssh aws2 "${_shylock_remote_build_env} && cd /home/ubuntu/shylock && git pull && docker-compose up -d --build"
}

shylock-deploy-fresh() {
  ssh aws2 "${_shylock_remote_build_env} && cd /home/ubuntu/shylock && git pull && docker-compose build --no-cache --pull && docker-compose up -d"
}
