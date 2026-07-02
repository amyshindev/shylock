export type Speaker = "NARRATOR" | "PORTIA" | "BASSANIO" | "CROWD";

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
  interactionType?: "choice" | "pressPresent";
  challenge: {
    header?: string;
    text: string;
    options: ChoiceOption[];
  } | null;
  pressPresent?: PressPresentConfig;
  availableEvidence: string[];
}

export interface PressPresentTestimony {
  id: string;
  text: string;
  pressReaction: string;
}

export interface PressPresentConfig {
  testimony: PressPresentTestimony[];
  contradiction: {
    statementId: string;
    evidenceId: string;
  };
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
  interactionType?: "choice" | "pressPresent";
  challengeTemplate: {
    header?: string;
    fallbackText: string;
    options: ChoiceTemplate[];
  } | null;
  pressPresent?: PressPresentConfig;
  availableEvidence: string[];
}
