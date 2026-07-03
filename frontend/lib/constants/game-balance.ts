export const SHYLOCK_DP_START = 50;
export const DP_MAX = 100;

export const DP_FOUGHT_TO_END_THRESHOLD = 80;
export const DP_DIGNITY_ENDING_THRESHOLD = 60;
export const DP_SURVIVAL_ENDING_THRESHOLD = 40;
export const DP_JESSICA_EPILOGUE_THRESHOLD = 90;

export const LAUNCELOT_SKILL_DP_GAIN = 10;

export const SKILL_TUBAL_COST = 30;

export const VENICE_CONTRADICTION_SKILL_COST = 40;
export const VENICE_CONTRADICTION_LINES = [
  "당신들은 나를 고리대금업자라 부르오.",
  "하지만 당신들이 내게 허락한 것이 그것뿐이었소.",
  "이것이 베니스의 정의요?",
] as const;

export const LAUNCELOT_INTRUSION_LINE = "론슬롯이 갑자기 법정으로 뛰어들었다! ";
export const LAUNCELOT_LINES = [
  "기독교인이 자꾸 늘어나면~",
  "돼지고기 값이 오른다네~",
  "그게 이 재판과 무슨 상관이냐고?~",
  "모르겠네, 모르겠네, 나도 몰라~",
] as const;
export const LAUNCELOT_REACTION_LINES = [
  "모두가 당황하여 잠시 말을 잃었다.",
  "이 틈을 타 숨을 고르자...",
] as const;

/** DP gain is applied when this reaction line is shown. */
export const LAUNCELOT_DP_GAIN_AT_REACTION_INDEX = 1;

export type SkillId = "launcelot" | "tubal" | "venice_contradiction";

export const TUBAL_INTRO_LINE = "잠깐, 내가 증거를 가져왔소.";
export const TUBAL_SEARCHING_LINE = "잠시만 기다리시오. 사본을 뒤져보겠소.";
export const TUBAL_SEARCH_FAILURE_LINE = "이번에는 증거가 될 만한 걸 못 찾았소.";

export interface SkillDefinition {
  id: SkillId;
  label: string;
  /** DP required to activate; 0 means no cost. */
  cost: number;
}

export const SKILLS: SkillDefinition[] = [
  { id: "launcelot", label: "🃏 론슬롯 난입 (+10 DP)", cost: 0 },
  { id: "tubal", label: "🤝 투발의 도움 (-30 DP)", cost: SKILL_TUBAL_COST },
  {
    id: "venice_contradiction",
    label: "⚔️ 베니스의 모순 (-40 DP · 다음 선택 보호)",
    cost: VENICE_CONTRADICTION_SKILL_COST,
  },
];
