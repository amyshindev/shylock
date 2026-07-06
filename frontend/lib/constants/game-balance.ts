import { CROWD_JEERS_SCENE_INDEX } from "@/lib/constants/scene-progression";

export const SHYLOCK_DP_START = 50;
export const DP_MAX = 100;

export const SHYLOCK_HP_START = 100;
export const HP_MAX = 100;
export const LOW_HP_THRESHOLD = 30;

export const PORTIA_HP_START = 100;
export const PORTIA_HP_MAX = 100;

/** Keep in sync with backend scene_choices.compute_portia_damage */
export const PORTIA_DAMAGE_DP_RATIO = 0.55;
export const PORTIA_DAMAGE_MIN = 2;
export const PORTIA_DAMAGE_MAX = 14;

/** Higher DP gains deal more Portia HP damage. Negative DP choices barely scratch Portia. */
export function computePortiaDamage(dpChange: number): number {
  if (dpChange <= 0) return dpChange <= -5 ? 0 : 1;
  const scaled = Math.round(dpChange * PORTIA_DAMAGE_DP_RATIO);
  return Math.max(PORTIA_DAMAGE_MIN, Math.min(PORTIA_DAMAGE_MAX, scaled));
}

export const DP_RESCUED_ENDING_THRESHOLD = 90;
export const DP_FOUGHT_TO_END_THRESHOLD = 80;
export const DP_DIGNITY_ENDING_THRESHOLD = 60;
export const DP_SURVIVAL_ENDING_THRESHOLD = 40;

// All skills convert DP into HP: negative dpChange spends DP, negative hpCost heals.
// DP can only be *gained* through scene choices.
export const TUBAL_SKILL_EFFECT = { dpChange: -6, hpCost: -8 } as const;
export const TUBAL_SKILL_HP_GAIN = -TUBAL_SKILL_EFFECT.hpCost;

export const LAUNCELOT_SKILL_EFFECT = { dpChange: -8, hpCost: -12 } as const;
export const LAUNCELOT_SKILL_HP_GAIN = -LAUNCELOT_SKILL_EFFECT.hpCost;

export const VENICE_PARADOX_SKILL_EFFECT = { dpChange: -14, hpCost: -20 } as const;
export const VENICE_PARADOX_SKILL_HP_GAIN = -VENICE_PARADOX_SKILL_EFFECT.hpCost;
export const VENICE_PARADOX_LINES = [
  "당신들은 나를 고리대금업자라 부르오.",
  "허나 묻겠소 — 내가 상인이 되는 것을 당신들의 길드가 허락했소?",
  "내가 땅을 사는 것을, 당신들의 법이 허락했소?",
  "당신들은 내게 문을 하나만 열어두고, 그 문으로 들어온 나를 손가락질하며 더럽다 하는구려.",
  "돈을 빌려주는 것. 그것이 당신들이 내게 허락한 유일한 일이었소.",
  "그리고 이제 와서, 내가 그 일을 너무 잘한다고 나를 벌하려 하시오?",
  "이것이 베니스의 정의요?",
  "당신들이 내게 증오를 가르쳤다면, 나는 그저 훌륭한 학생이었을 뿐이오.",
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

/** HP gain is applied when this reaction line is shown. */
export const LAUNCELOT_HP_GAIN_AT_REACTION_INDEX = 1;

export type SkillId = "launcelot" | "tubal" | "venice_paradox";

export const TUBAL_INTRO_LINE = "잠깐, 내가 증거를 가져왔소.";
export const TUBAL_SEARCHING_LINE = "잠시만 기다리시오. 사본을 뒤져보겠소.";
export const TUBAL_SEARCH_FAILURE_LINE = "이번에는 증거가 될 만한 걸 못 찾았소.";

export interface SkillDefinition {
  id: SkillId;
  label: string;
  /** Minimum DP required to activate (when skill costs DP). */
  cost: number;
}

export const SKILLS: SkillDefinition[] = [
  {
    id: "launcelot",
    label: "🃏 론슬롯 난입 (-8 DP · +12 HP)",
    cost: -LAUNCELOT_SKILL_EFFECT.dpChange,
  },
  {
    id: "tubal",
    label: "🤝 투발의 도움 (-6 DP · +8 HP)",
    cost: -TUBAL_SKILL_EFFECT.dpChange,
  },
  {
    id: "venice_paradox",
    label: "⚔️ 베니스의 모순 (-14 DP · +20 HP · 1회)",
    cost: -VENICE_PARADOX_SKILL_EFFECT.dpChange,
  },
];

export function canUseSkill(
  skillId: SkillId,
  ctx: { dp: number; sceneIdx: number; veniceParadoxUsed: boolean },
): boolean {
  switch (skillId) {
    case "launcelot":
      return ctx.dp >= -LAUNCELOT_SKILL_EFFECT.dpChange;
    case "tubal":
      return ctx.dp >= -TUBAL_SKILL_EFFECT.dpChange;
    case "venice_paradox":
      return (
        ctx.sceneIdx > CROWD_JEERS_SCENE_INDEX &&
        !ctx.veniceParadoxUsed &&
        ctx.dp >= -VENICE_PARADOX_SKILL_EFFECT.dpChange
      );
    default:
      return false;
  }
}
