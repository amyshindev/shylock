export type TrialPhase = "in_progress" | "ended";

export type DialogueLineKind = "speech" | "narration";

export interface SceneDialogueLineFromApi {
  text: string;
  kind: DialogueLineKind;
  speaker?: string | null;
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
  dp: number;
  hp: number;
  portia_hp: number;
  phase: TrialPhase;
  choice_history?: string[];
  narration_text?: string | null;
  scene_dialogue?: SceneDialogueFromApi | null;
  tubal_enhanced_choices?: Record<string, string>;
  venice_dp_shield?: boolean;
  venice_paradox_used?: boolean;
}

export interface StartTrialResponse extends TrialState {
  scene_dialogue: SceneDialogueFromApi;
}

export interface UserFromApi {
  user_id: string;
  email: string | null;
  nickname: string;
}

export interface TrialSummaryFromApi {
  trial_id: string;
  scene_index: number;
  dp: number;
  hp: number;
  portia_hp: number;
  phase: TrialPhase;
}

export interface SubmitChoiceResponse {
  trial_id: string;
  scene_index: number;
  dp: number;
  hp: number;
  portia_hp: number;
  phase: TrialPhase;
  portia_response: string;
  // portia_response가 누구 목소리로 나오는지 — 거의 모든 씬에서 "PORTIA"/"포샤"이고;
  // 소수의 opt-in 집합(backend의 scene_progression.REACTOR_OVERRIDE_SCENES 참고,
  // 예: bassanio_plea)에서만 그 씬 고유의 화자로 바뀜.
  portia_response_speaker?: string;
  portia_response_speaker_label?: string;
  ending_type: string | null;
  is_ending: boolean;
  tubal_enhanced_choices?: Record<string, string>;
  venice_dp_shield: boolean;
  // 이번 라운드에 대한 공작(Duke)의 판결 — 위 dp/portia_hp는 이미 이걸 반영한
  // 값임(backend의 trial_progression_interactor._judge_choice 참고). 이 줄은
  // portia_response보다 먼저 실제 dialogue-box 답변으로(speaker tag "DUKE"/
  // "공작", 포샤 답변처럼 타이핑됨) 보여짐 — use-trial-progression.ts의
  // dukeVerdict state와 dismissDukeVerdict 참고. duke_verdict_result는 지금
  // 당장은 어디에도 렌더링되지 않음; 나중에 쓸 수 있게 그냥 실어 보내는 것.
  duke_verdict_result: "win" | "lose";
  duke_verdict_line: string;
}

export interface AdvanceSceneResponse {
  trial_id: string;
  scene_index: number;
  scene_data: { scene_index: number };
  scene_dialogue: SceneDialogueFromApi;
  dp: number;
  hp: number;
  portia_hp: number;
}

export interface EndingResponse {
  trial_id: string;
  ending_type: string;
  ending_text: string;
  dp: number;
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
  hp: number;
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
  hp: number;
  launcelot_comment: string;
}

export interface VeniceParadoxSkillResponse {
  trial_id: string;
  dp: number;
  hp: number;
  venice_paradox_used: boolean;
  skill_comment: string;
}

export interface PresentEvidenceResponse {
  trial_id: string;
  dp: number;
  contradiction_valid: boolean;
  portia_response: string;
}

export interface LoreChatSourceFromApi {
  ftln: number;
  act_scene: string;
  speaker: string;
  excerpt: string;
}

export interface LoreChatAskResponse {
  session_id: string;
  answer: string;
  sources: LoreChatSourceFromApi[];
}
