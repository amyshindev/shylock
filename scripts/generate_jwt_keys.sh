#!/usr/bin/env bash
# Generate RS256 keypair for the auth gateway (harness §2.7).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="${ROOT}/secrets"
mkdir -p "${OUT}"

openssl genrsa -out "${OUT}/jwt_private.pem" 2048
openssl rsa -in "${OUT}/jwt_private.pem" -pubout -out "${OUT}/jwt_public.pem"

b64_priv="$(base64 -w0 < "${OUT}/jwt_private.pem" 2>/dev/null || base64 < "${OUT}/jwt_private.pem" | tr -d '\n')"
b64_pub="$(base64 -w0 < "${OUT}/jwt_public.pem" 2>/dev/null || base64 < "${OUT}/jwt_public.pem" | tr -d '\n')"

cat <<EOF

Generated:
  ${OUT}/jwt_private.pem
  ${OUT}/jwt_public.pem

Put into .env.auth:
  JWT_PRIVATE_KEY=${b64_priv}
  JWT_PUBLIC_KEY=${b64_pub}

Put into .env.backend (public only):
  JWT_PUBLIC_KEY=${b64_pub}

PEM files under secrets/ are gitignored — do not commit them.
EOF
