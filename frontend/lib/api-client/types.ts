export type TrialPhase = "in_progress" | "ended";

export interface TrialState {
  trial_id: string;
  scene_index: number;
  dignity: number;
  confidence: number;
  phase: TrialPhase;
  choice_history?: string[];
  narration_text?: string | null;
}

export interface StartTrialResponse extends TrialState {
  narration_text: string;
}

export interface SubmitChoiceResponse {
  trial_id: string;
  scene_index: number;
  dignity: number;
  confidence: number;
  phase: TrialPhase;
  portia_response: string;
  ending_type: string | null;
  is_ending: boolean;
}

export interface EndingResponse {
  trial_id: string;
  ending_type: string;
  ending_text: string;
  dignity: number;
  confidence: number;
}

export interface EvidenceFromApi {
  evidence_id: string;
  quote: string;
  act_scene: string;
  icon: string;
  description: string;
  source_ftln_start: number;
  source_ftln_end: number;
}
