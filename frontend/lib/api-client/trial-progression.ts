import { API_BASE, API_PREFIX } from "./config";
import type {
  AdvanceSceneResponse,
  EndingResponse,
  EvidenceFromApi,
  StartTrialResponse,
  SubmitChoiceResponse,
  TrialState,
  TubalSkillResponse,
  PresentEvidenceResponse,
} from "./types";

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

export async function advanceScene(trialId: string): Promise<AdvanceSceneResponse> {
  const res = await fetch(`${API_BASE}${API_PREFIX}/trials/${trialId}/advance`, {
    method: "POST",
  });
  return parseJson<AdvanceSceneResponse>(res);
}

export async function generateEnding(trialId: string): Promise<EndingResponse> {
  const res = await fetch(`${API_BASE}${API_PREFIX}/trials/${trialId}/ending`);
  return parseJson<EndingResponse>(res);
}

export interface InvokeTubalSkillBody {
  portia_claim?: string | null;
  scene_id?: string | null;
}

export async function invokeTubalSkill(
  trialId: string,
  body: InvokeTubalSkillBody = {},
): Promise<TubalSkillResponse> {
  const res = await fetch(`${API_BASE}${API_PREFIX}/trials/${trialId}/skills/tubal`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  return parseJson<TubalSkillResponse>(res);
}

export interface PresentEvidenceBody {
  scene_id: string;
  evidence_id: string;
  evidence_text: string;
}

export async function presentEvidence(
  trialId: string,
  body: PresentEvidenceBody,
): Promise<PresentEvidenceResponse> {
  const res = await fetch(`${API_BASE}${API_PREFIX}/trials/${trialId}/present-evidence`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  return parseJson<PresentEvidenceResponse>(res);
}
