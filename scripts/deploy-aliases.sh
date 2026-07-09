#!/usr/bin/env bash
# Remote deploy helpers for aws2.
# Load from ~/.bash_aliases:
#   source "$HOME/shylock/scripts/deploy-aliases.sh"

shylock-deploy() {
  ssh aws2 'cd /home/ubuntu/shylock && git pull && docker image prune -f && docker-compose up -d --build'
}

shylock-deploy-fresh() {
  ssh aws2 'cd /home/ubuntu/shylock && git pull && docker image prune -af && docker-compose build --no-cache --pull && docker-compose up -d'
}

shylock-server-clean() {
  ssh aws2 'docker system prune -af && docker volume prune -f'
}
