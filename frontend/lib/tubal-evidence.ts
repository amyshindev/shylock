export interface TubalCourtRecord {
  id: string;
  ftln: number;
  name: string;
  passage: string;
  speaker: string | null;
  actScene: string | null;
  tubalComment: string;
}

export function buildTubalCourtRecord(params: {
  ftln: number;
  passage: string;
  speaker: string | null;
  act_scene: string | null;
  tubal_comment: string;
}): TubalCourtRecord {
  const speaker = params.speaker?.trim() || null;
  const actScene = params.act_scene?.trim() || null;
  const name = speaker
    ? actScene
      ? `${speaker} (${actScene})`
      : speaker
    : "Folger 구절";

  return {
    id: `tubal-${params.ftln}`,
    ftln: params.ftln,
    name,
    passage: params.passage,
    speaker,
    actScene,
    tubalComment: params.tubal_comment,
  };
}

export function mergeTubalCourtRecords(
  existing: TubalCourtRecord[],
  incoming: TubalCourtRecord,
): TubalCourtRecord[] {
  if (existing.some((record) => record.ftln === incoming.ftln)) {
    return existing;
  }
  return [...existing, incoming];
}

export interface EvidenceDetailView {
  kind: "curated" | "tubal";
  evidenceId: string;
  name: string;
  quote: string;
  speaker?: string | null;
  actScene?: string | null;
  tubalComment?: string;
  dismissible?: boolean;
}
