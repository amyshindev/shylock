export const SHYLOCK_HP_MAX = 60;
export const SHYLOCK_DP_START = 50;
export const PORTIA_HP_MAX = 100;
export const DP_MAX = 100;
export const DP_GOOD_ENDING_THRESHOLD = 70;

export const SKILL_OBJECTION_COST = 20;
export const SKILL_TUBAL_COST = 30;
export const SKILL_CROWD_COST = 40;

export const LAUNCELOT_SKILL_COST = 20;
export const LAUNCELOT_PORTIA_HP_DAMAGE = 20;

export const LAUNCELOT_INTRUSION_LINE = "론슬롯이 갑자기 법정으로 뛰어들었다!";
export const LAUNCELOT_LINES = [
  "기독교인이 자꾸 늘어나면~",
  "돼지고기 값이 오른다네~",
  "그게 이 재판과 무슨 상관이냐고?~",
  "모르겠네, 모르겠네, 나도 몰라~",
] as const;
export const LAUNCELOT_PORTIA_REACTION_LINE = "포샤가 당황해 말문이 막혔다!";

export type SkillId = "objection" | "tubal" | "crowd";

export const TUBAL_INTRO_LINE = "잠깐, 내가 증거를 가져왔소.";
export const TUBAL_SEARCHING_LINE = "잠시만 기다리시오. 사본을 뒤져보겠소.";
export const TUBAL_SEARCH_FAILURE_LINE = "이번에는 증거가 될 만한 걸 못 찾았소.";

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
