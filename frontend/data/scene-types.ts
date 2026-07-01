export type Speaker = "NARRATOR" | "PORTIA" | "CROWD";

export type DialogueLineKind = "speech" | "narration";

export interface SceneLine {
  text: string;
  kind: DialogueLineKind;
}

export interface ChoiceOption {
  id: string;
  text: string;
  evidence: string | null;
  dpChange: number;
  shylockHpChange: number;
  special?: "climax";
}

export interface Scene {
  id: string;
  speaker: Speaker;
  speakerLabel?: string;
  backgroundImage: string;
  lines: SceneLine[];
  challenge: {
    header?: string;
    text: string;
    options: ChoiceOption[];
  } | null;
  availableEvidence: string[];
}

export interface FallbackLine {
  text: string;
  kind: DialogueLineKind;
}

export interface ChoiceTemplate {
  id: string;
  fallbackText: string;
  evidence: string | null;
  dpChange: number;
  shylockHpChange: number;
  special?: "climax";
}

export interface SceneTemplate {
  id: string;
  speaker: Speaker;
  speakerLabel?: string;
  backgroundImage: string;
  fallbackLines: FallbackLine[];
  challengeTemplate: {
    header?: string;
    fallbackText: string;
    options: ChoiceTemplate[];
  } | null;
  availableEvidence: string[];
}
