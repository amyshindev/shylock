import { API_BASE, API_PREFIX } from "./config";
import { requestJson } from "./http";
import type { LoreChatAskResponse } from "./types";

export interface AskLoreChatBody {
  message: string;
  session_id?: string | null;
}

export async function askLoreChat(body: AskLoreChatBody): Promise<LoreChatAskResponse> {
  return requestJson<LoreChatAskResponse>(`${API_BASE}${API_PREFIX}/lore-chat/ask`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
}
