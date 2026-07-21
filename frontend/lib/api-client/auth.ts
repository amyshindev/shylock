import { API_BASE, API_PREFIX } from "./config";
import { requestJson } from "./http";
import type { UserFromApi } from "./types";

const AUTH_BASE = `${API_BASE}${API_PREFIX}/auth`;

export async function signup(
  email: string,
  password: string,
  nickname: string,
): Promise<UserFromApi> {
  return requestJson<UserFromApi>(`${AUTH_BASE}/signup`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password, nickname }),
  });
}

export async function login(email: string, password: string): Promise<UserFromApi> {
  return requestJson<UserFromApi>(`${AUTH_BASE}/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
}

export async function logout(): Promise<void> {
  await requestJson<void>(`${AUTH_BASE}/logout`, { method: "POST" });
}

/** Returns the logged-in user, or null when the session is absent/expired. */
export async function fetchMe(): Promise<UserFromApi | null> {
  try {
    return await requestJson<UserFromApi>(`${AUTH_BASE}/me`);
  } catch {
    return null;
  }
}
