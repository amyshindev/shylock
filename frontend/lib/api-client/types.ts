export type TrialPhase = "in_progress" | "ended";

export type DialogueLineKind = "speech" | "narration";

export interface SceneDialogueLineFromApi {
  text: string;
  kind: DialogueLineKind;
}

export interface SceneDialogueFromApi {
  lines: SceneDialogueLineFromApi[];
  challenge_header?: string | null;
  challenge_text?: string | null;
  choice_texts?: Record<string, string>;
}

export interface TrialState {
  trial_id: string;
  scene_index: number;
  shylock_hp: number;
  dp: number;
  alien_law_executed: boolean;
  phase: TrialPhase;
  choice_history?: string[];
  narration_text?: string | null;
  scene_dialogue?: SceneDialogueFromApi | null;
  tubal_enhanced_choices?: Record<string, string>;
}

export interface StartTrialResponse extends TrialState {
  scene_dialogue: SceneDialogueFromApi;
}

export interface SubmitChoiceResponse {
  trial_id: string;
  scene_index: number;
  shylock_hp: number;
  dp: number;
  alien_law_executed: boolean;
  phase: TrialPhase;
  portia_response: string;
  ending_type: string | null;
  is_ending: boolean;
  tubal_enhanced_choices?: Record<string, string>;
}

export interface AdvanceSceneResponse {
  trial_id: string;
  scene_index: number;
  scene_data: { scene_index: number };
  scene_dialogue: SceneDialogueFromApi;
}

export interface EndingResponse {
  trial_id: string;
  ending_type: string;
  ending_text: string;
  shylock_hp: number;
  dp: number;
  alien_law_executed: boolean;
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

export interface TubalSkillResponse {
  trial_id: string;
  dp: number;
  shylock_hp: number;
  success: boolean;
  ftln: number | null;
  passage: string | null;
  speaker: string | null;
  act_scene: string | null;
  tubal_comment: string | null;
  tubal_enhanced_choices?: Record<string, string>;
}

export interface LauncelotSkillResponse {
  trial_id: string;
  dp: number;
  shylock_hp: number;
  launcelot_comment: string;
}

export interface VeniceContradictionSkillResponse {
  trial_id: string;
  dp: number;
  shylock_hp: number;
  skill_comment: string;
}

export interface PresentEvidenceResponse {
  trial_id: string;
  shylock_hp: number;
  dp: number;
  contradiction_valid: boolean;
  portia_response: string;
}
