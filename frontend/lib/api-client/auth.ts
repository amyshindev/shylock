import { API_BASE, API_PREFIX, AUTH_GATEWAY_BASE } from "./config";
import { requestJson } from "./http";
import type { UserFromApi } from "./types";

const ME_URL = `${API_BASE}${API_PREFIX}/auth/me`;
const GATEWAY_AUTH_BASE = `${AUTH_GATEWAY_BASE}/auth`;

/** Redirects the browser to Google's consent screen via the auth gateway. */
export async function loginWithGoogle(): Promise<void> {
  const { authorization_url } = await requestJson<{ authorization_url: string }>(
    `${GATEWAY_AUTH_BASE}/login`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ provider: "google" }),
    },
  );
  window.location.href = authorization_url;
}

export async function logout(): Promise<void> {
  await requestJson<void>(`${GATEWAY_AUTH_BASE}/logout`, { method: "POST" });
}

/** Returns the logged-in user, or null when the session is absent/expired. */
export async function fetchMe(): Promise<UserFromApi | null> {
  try {
    return await requestJson<UserFromApi>(ME_URL);
  } catch {
    return null;
  }
}
