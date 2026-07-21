async function parseJson<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const text = await res.text();
    let message = text || `Request failed (${res.status})`;
    try {
      const body = JSON.parse(text) as { detail?: unknown };
      if (typeof body.detail === "string") {
        message = body.detail.startsWith("Trial not found:")
          ? "재판 기록을 찾을 수 없습니다. 백엔드가 재시작되었을 수 있으니 처음부터 다시 시작해 주세요."
          : body.detail;
      }
    } catch {
      /* keep raw text */
    }
    throw new Error(message);
  }
  if (res.status === 204) {
    return undefined as T;
  }
  return res.json() as Promise<T>;
}

export async function requestJson<T>(
  input: RequestInfo | URL,
  init?: RequestInit,
): Promise<T> {
  try {
    // Session cookie must flow on every call so logged-in trials are owned.
    const res = await fetch(input, { credentials: "include", ...init });
    return await parseJson<T>(res);
  } catch (e) {
    if (e instanceof TypeError) {
      throw new Error(
        "서버에 연결할 수 없습니다. 백엔드가 실행 중인지 확인한 뒤 다시 시도해 주세요.",
      );
    }
    throw e;
  }
}
