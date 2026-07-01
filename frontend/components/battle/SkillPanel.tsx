"use client";

import { SKILLS, type SkillId } from "@/lib/constants/game-balance";
import { theme } from "@/styles/theme";

import { LEFT_METER_COLUMN_WIDTH } from "./MeterDisplay";

const SKILL_PANEL_WIDTH = LEFT_METER_COLUMN_WIDTH / 2;

interface SkillPanelProps {
  dp: number;
  disabled?: boolean;
  onUseSkill: (skillId: SkillId) => void;
}

export function SkillPanel({ dp, disabled, onUseSkill }: SkillPanelProps) {
  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        gap: 5,
        width: SKILL_PANEL_WIDTH,
      }}
    >
      {SKILLS.map((skill) => {
        const canUse = dp > skill.cost && !disabled;
        return (
          <button
            key={skill.id}
            type="button"
            disabled={!canUse}
            onClick={() => onUseSkill(skill.id)}
            style={{
              padding: "6px 8px",
              fontSize: 9,
              letterSpacing: 0.3,
              textAlign: "left",
              cursor: canUse ? "pointer" : "not-allowed",
              background: canUse ? "rgba(20, 10, 16, 0.9)" : "rgba(12, 6, 10, 0.7)",
              color: canUse ? theme.textBright : theme.textMuted,
              border: `1px solid ${canUse ? "#4a3040" : "#2a1820"}`,
              borderRadius: 3,
              opacity: canUse ? 1 : 0.55,
            }}
          >
            {skill.label}
          </button>
        );
      })}
    </div>
  );
}
