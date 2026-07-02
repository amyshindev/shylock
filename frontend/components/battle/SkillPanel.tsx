"use client";

import { SKILLS, type SkillId } from "@/lib/constants/game-balance";
import { gameFontSize, hudLabelStyle, hudPanelStyle } from "@/styles/text-box";

import { LEFT_METER_COLUMN_WIDTH } from "./MeterDisplay";

const SKILL_PANEL_WIDTH = LEFT_METER_COLUMN_WIDTH / 2;

const SKILL_ENABLED_COLOR = "#f0d8c8";
const SKILL_DISABLED_COLOR = "#9a8a92";

interface SkillPanelProps {
  dp: number;
  disabled?: boolean;
  onUseSkill: (skillId: SkillId) => void;
}

export function SkillPanel({ dp, disabled, onUseSkill }: SkillPanelProps) {
  return (
    <div style={{ ...hudPanelStyle("8px 11px"), width: SKILL_PANEL_WIDTH }}>
      <div
        style={{
          ...hudLabelStyle("#e8dce4"),
          fontSize: gameFontSize.xs,
          letterSpacing: 0.8,
          marginBottom: 6,
        }}
      >
        스킬
      </div>
      <div style={{ display: "flex", flexDirection: "column", gap: 5 }}>
        {SKILLS.map((skill) => {
          const canUse = dp >= skill.cost && !disabled;
          return (
            <button
              key={skill.id}
              type="button"
              disabled={!canUse}
              onClick={() => onUseSkill(skill.id)}
              style={{
                padding: "7px 10px",
                fontSize: gameFontSize.xs,
                letterSpacing: 0.3,
                textAlign: "left",
                cursor: canUse ? "pointer" : "not-allowed",
                background: canUse ? "rgba(20, 10, 18, 0.95)" : "rgba(14, 8, 14, 0.9)",
                color: canUse ? SKILL_ENABLED_COLOR : SKILL_DISABLED_COLOR,
                border: `1px solid ${canUse ? "#5a3848" : "#3a2830"}`,
                borderRadius: 3,
                fontWeight: 600,
                textShadow: canUse ? "0 1px 2px rgba(0, 0, 0, 0.6)" : "none",
                boxShadow: canUse ? "inset 0 1px 0 rgba(255, 255, 255, 0.04)" : "none",
                opacity: canUse ? 1 : 0.82,
                transition: "border-color 0.15s, background 0.15s",
              }}
              onMouseEnter={(e) => {
                if (!canUse) return;
                e.currentTarget.style.borderColor = "#7a5060";
                e.currentTarget.style.background = "rgba(28, 14, 22, 0.98)";
              }}
              onMouseLeave={(e) => {
                if (!canUse) return;
                e.currentTarget.style.borderColor = "#5a3848";
                e.currentTarget.style.background = "rgba(20, 10, 18, 0.95)";
              }}
            >
              {skill.label}
            </button>
          );
        })}
      </div>
    </div>
  );
}
