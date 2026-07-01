export const SHYLOCK_HP_MAX = 60;
export const SHYLOCK_DP_START = 50;
export const PORTIA_HP_MAX = 100;
export const DP_MAX = 100;
export const DP_GOOD_ENDING_THRESHOLD = 70;

export const SKILL_OBJECTION_COST = 20;
export const SKILL_TUBAL_COST = 30;
export const SKILL_CROWD_COST = 40;

export type SkillId = "objection" | "tubal" | "crowd";

export const TUBAL_INTRO_LINE = "잠깐, 내가 증거를 가져왔소.";
export const TUBAL_SEARCHING_LINE = "투발이 Folger 사본을 뒤지는 중…";

export interface SkillDefinition {
  id: SkillId;
  label: string;
  cost: number;
}

export const SKILLS: SkillDefinition[] = [
  { id: "objection", label: "⚖️ 이의 있습니다 (-20 DP)", cost: SKILL_OBJECTION_COST },
  { id: "tubal", label: "🤝 투발의 도움 (-30 DP)", cost: SKILL_TUBAL_COST },
  { id: "crowd", label: "📣 군중에 호소 (-40 DP)", cost: SKILL_CROWD_COST },
];
