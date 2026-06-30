import { API_BASE, API_PREFIX } from "./config";
import type {
  EndingResponse,
  EvidenceFromApi,
  StartTrialResponse,
  SubmitChoiceResponse,
  TrialState,
} from "./types";

async function parseJson<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `Request failed (${res.status})`);
  }
  return res.json() as Promise<T>;
}

export async function startTrial(): Promise<StartTrialResponse> {
  const res = await fetch(`${API_BASE}${API_PREFIX}/trials`, { method: "POST" });
  return parseJson<StartTrialResponse>(res);
}

export async function getTrial(trialId: string): Promise<TrialState> {
  const res = await fetch(`${API_BASE}${API_PREFIX}/trials/${trialId}`);
  return parseJson<TrialState>(res);
}

export async function submitChoice(
  trialId: string,
  choiceId: string,
): Promise<SubmitChoiceResponse> {
  const res = await fetch(`${API_BASE}${API_PREFIX}/trials/${trialId}/choices`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ choice_id: choiceId }),
  });
  return parseJson<SubmitChoiceResponse>(res);
}

export async function advanceScene(trialId: string): Promise<{ scene_index: number }> {
  const res = await fetch(`${API_BASE}${API_PREFIX}/trials/${trialId}/advance`, {
    method: "POST",
  });
  const data = await parseJson<{ scene_index: number }>(res);
  return data;
}

export async function generateEnding(trialId: string): Promise<EndingResponse> {
  const res = await fetch(`${API_BASE}${API_PREFIX}/trials/${trialId}/ending`);
  return parseJson<EndingResponse>(res);
}
