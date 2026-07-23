# Local setup for the auth gateway (shylock)

See also: [auth-gateway-harness.md](auth-gateway-harness.md)

## Cloudflare (manual)

```
auth.shylock-trial.xyz  → http://auth:9000
api.shylock-trial.xyz   → http://backend:8000
shylock-trial.xyz       → http://frontend:3000
```

```bash
cloudflared tunnel route dns <tunnel-name> auth.shylock-trial.xyz
```

## Keys + env

```bash
bash scripts/generate_jwt_keys.sh
cp .env.auth.example .env.auth      # paste JWT_* + Google secrets
cp .env.backend.example .env.backend  # JWT_PUBLIC_KEY only (no private key)
docker compose up -d --build
curl -s https://auth.shylock-trial.xyz/healthz
```
