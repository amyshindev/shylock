import { API_BASE, API_PREFIX } from "./config";
import type {
  AdvanceSceneResponse,
  EndingResponse,
  EvidenceFromApi,
  StartTrialResponse,
  SubmitChoiceResponse,
  TrialState,
  TubalSkillResponse,
  LauncelotSkillResponse,
  PresentEvidenceResponse,
  VeniceParadoxSkillResponse,
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

async function requestJson<T>(input: RequestInfo | URL, init?: RequestInit): Promise<T> {
  try {
    const res = await fetch(input, init);
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

export async function startTrial(): Promise<StartTrialResponse> {
  return requestJson<StartTrialResponse>(`${API_BASE}${API_PREFIX}/trials`, { method: "POST" });
}

export async function startDevJessicaDuet(): Promise<StartTrialResponse> {
  return requestJson<StartTrialResponse>(
    `${API_BASE}${API_PREFIX}/dev/trials/jessica-duet`,
    { method: "POST" },
  );
}

export async function startDevJessicaIntervention(): Promise<StartTrialResponse> {
  return requestJson<StartTrialResponse>(
    `${API_BASE}${API_PREFIX}/dev/trials/jessica-intervention`,
    { method: "POST" },
  );
}

export async function getTrial(trialId: string): Promise<TrialState> {
  return requestJson<TrialState>(`${API_BASE}${API_PREFIX}/trials/${trialId}`);
}

export async function submitChoice(
  trialId: string,
  choiceId: string,
): Promise<SubmitChoiceResponse> {
  return requestJson<SubmitChoiceResponse>(`${API_BASE}${API_PREFIX}/trials/${trialId}/choices`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ choice_id: choiceId }),
  });
}

export async function advanceScene(trialId: string): Promise<AdvanceSceneResponse> {
  return requestJson<AdvanceSceneResponse>(`${API_BASE}${API_PREFIX}/trials/${trialId}/advance`, {
    method: "POST",
  });
}

export async function generateEnding(trialId: string): Promise<EndingResponse> {
  return requestJson<EndingResponse>(`${API_BASE}${API_PREFIX}/trials/${trialId}/ending`);
}

export interface InvokeTubalSkillBody {
  portia_claim?: string | null;
  scene_id?: string | null;
}

export async function invokeTubalSkill(
  trialId: string,
  body: InvokeTubalSkillBody = {},
): Promise<TubalSkillResponse> {
  return requestJson<TubalSkillResponse>(`${API_BASE}${API_PREFIX}/trials/${trialId}/skills/tubal`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
}

export async function useLauncelotSkill(trialId: string): Promise<LauncelotSkillResponse> {
  return requestJson<LauncelotSkillResponse>(
    `${API_BASE}${API_PREFIX}/trials/${trialId}/skills/launcelot`,
    { method: "POST" },
  );
}

export async function useVeniceParadoxSkill(
  trialId: string,
): Promise<VeniceParadoxSkillResponse> {
  return requestJson<VeniceParadoxSkillResponse>(
    `${API_BASE}${API_PREFIX}/trials/${trialId}/skills/venice-paradox`,
    { method: "POST" },
  );
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
  return requestJson<PresentEvidenceResponse>(
    `${API_BASE}${API_PREFIX}/trials/${trialId}/present-evidence`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    },
  );
}
