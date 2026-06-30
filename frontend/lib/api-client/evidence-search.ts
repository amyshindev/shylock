import { API_BASE, API_PREFIX } from "./config";
import type { EvidenceFromApi } from "./types";

async function parseJson<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `Request failed (${res.status})`);
  }
  return res.json() as Promise<T>;
}

export async function listEvidence(): Promise<EvidenceFromApi[]> {
  const res = await fetch(`${API_BASE}${API_PREFIX}/evidence`);
  return parseJson<EvidenceFromApi[]>(res);
}

export async function getEvidence(evidenceId: string): Promise<EvidenceFromApi> {
  const res = await fetch(`${API_BASE}${API_PREFIX}/evidence/${evidenceId}`);
  return parseJson<EvidenceFromApi>(res);
}
