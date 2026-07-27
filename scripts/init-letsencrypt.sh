#!/usr/bin/env bash
# One-time bootstrap for Let's Encrypt certs (nginx + certbot, docker-compose.yaml).
# Nginx won't start with the real ssl_certificate paths until they exist, so this
# spins up dummy self-signed certs first, starts nginx, swaps in real certs via
# certbot's webroot challenge, then reloads nginx.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

DC="docker compose"
command -v docker-compose >/dev/null 2>&1 && ! docker compose version >/dev/null 2>&1 && DC="docker-compose"

EMAIL="amysoo02@gmail.com"
RSA_KEY_SIZE=4096
DATA_PATH="./certbot"
STAGING=0 # set to 1 first to avoid Let's Encrypt's rate limits while testing

# domain groups: first domain in each group names the cert (matches default.conf)
DOMAIN_GROUPS=(
  "api.shylock-trial.xyz"
  "auth.shylock-trial.xyz"
  "shylock-trial.xyz www.shylock-trial.xyz"
)

if [ -d "$DATA_PATH/conf/live" ]; then
  read -p "Existing certs found in $DATA_PATH. Continue and replace them? (y/N) " decision
  if [ "$decision" != "y" ] && [ "$decision" != "Y" ]; then
    exit 0
  fi
fi

for group in "${DOMAIN_GROUPS[@]}"; do
  domains=($group)
  cert_name="${domains[0]}"

  echo "### Creating dummy certificate for $cert_name ..."
  path="/etc/letsencrypt/live/$cert_name"
  mkdir -p "$DATA_PATH/conf/live/$cert_name"
  $DC run --rm --entrypoint "\
    openssl req -x509 -nodes -newkey rsa:$RSA_KEY_SIZE -days 1\
      -keyout '$path/privkey.pem' \
      -out '$path/fullchain.pem' \
      -subj '/CN=localhost'" certbot
done

echo "### Starting nginx ..."
$DC up --force-recreate -d nginx

for group in "${DOMAIN_GROUPS[@]}"; do
  domains=($group)
  cert_name="${domains[0]}"

  echo "### Deleting dummy certificate for $cert_name ..."
  $DC run --rm --entrypoint "\
    rm -Rf /etc/letsencrypt/live/$cert_name && \
    rm -Rf /etc/letsencrypt/archive/$cert_name && \
    rm -Rf /etc/letsencrypt/renewal/$cert_name.conf" certbot

  echo "### Requesting real certificate for $cert_name ..."
  domain_args=""
  for domain in "${domains[@]}"; do
    domain_args="$domain_args -d $domain"
  done

  staging_arg=""
  if [ "$STAGING" != "0" ]; then staging_arg="--staging"; fi

  $DC run --rm --entrypoint "\
    certbot certonly --webroot -w /var/www/certbot \
      $staging_arg \
      $domain_args \
      --email $EMAIL \
      --rsa-key-size $RSA_KEY_SIZE \
      --agree-tos \
      --no-eff-email \
      --force-renewal" certbot
done

echo "### Reloading nginx ..."
$DC exec nginx nginx -s reload
