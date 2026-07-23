export const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export const API_PREFIX = "/shylock-trial";

// Auth gateway (auth.shylock-trial.xyz in production) — issues/rotates JWTs.
export const AUTH_GATEWAY_BASE =
  process.env.NEXT_PUBLIC_AUTH_BASE_URL ?? "http://localhost:9000";
