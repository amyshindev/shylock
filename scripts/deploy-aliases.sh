#!/usr/bin/env bash
# Remote deploy helpers for shylock-prod (Amazon Linux; replaced aws2).
# Load from ~/.bash_aliases:
#   source "$HOME/shylock/scripts/deploy-aliases.sh"

shylock-deploy() {
  ssh shylock-prod 'cd /home/ec2-user/shylock && git pull && docker image prune -f && docker compose up -d --build'
}

shylock-deploy-fresh() {
  ssh shylock-prod 'cd /home/ec2-user/shylock && git pull && docker image prune -af && docker compose build --no-cache --pull && docker compose up -d'
}

shylock-server-clean() {
  ssh shylock-prod 'docker system prune -af && docker volume prune -f'
}
