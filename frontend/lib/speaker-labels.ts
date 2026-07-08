import type { Speaker } from "@/data/scene-types";

const SPEAKER_LABELS: Record<Speaker, string | undefined> = {
  NARRATOR: undefined,
  PORTIA: "포샤",
  BASSANIO: "바사니오",
  CROWD: "군중",
  JESSICA: "제시카",
  LORENZO: "로렌조",
  SHYLOCK: "샤일록",
};

export function resolveSpeakerLabel(
  speaker: Speaker | undefined,
  explicitLabel?: string,
): string | undefined {
  if (explicitLabel) return explicitLabel;
  if (!speaker) return undefined;
  return SPEAKER_LABELS[speaker];
}
