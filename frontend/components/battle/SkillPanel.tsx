"use client";

import type { CSSProperties } from "react";

import { useIsMobile } from "@/hooks/use-is-mobile";
import {
  SKILLS,
  canUseSkill,
  type SkillId,
} from "@/lib/constants/game-balance";
import { gameFontSize, hudLabelStyle, hudPanelStyle } from "@/styles/text-box";

import {
  LEFT_METER_COLUMN_WIDTH,
  LEFT_METER_COLUMN_WIDTH_MOBILE,
} from "./MeterDisplay";

const SKILL_ENABLED_COLOR = "#f0d8c8";
const SKILL_LOCKED_COLOR = "#5c5c5c";

interface SkillPanelProps {
  dp: number;
  sceneIdx: number;
  veniceParadoxUsed: boolean;
  disabled?: boolean;
  onUseSkill: (skillId: SkillId) => void;
}

function skillButtonStyle(canUse: boolean, lockedOut: boolean): CSSProperties {
  if (canUse) {
    return {
      padding: "7px 10px",
      fontSize: gameFontSize.xs,
      letterSpacing: 0.3,
      textAlign: "left",
      cursor: "pointer",
      background: "rgba(20, 10, 18, 0.95)",
      color: SKILL_ENABLED_COLOR,
      border: "1px solid #5a3848",
      borderRadius: 3,
      fontWeight: 600,
      textShadow: "0 1px 2px rgba(0, 0, 0, 0.6)",
      boxShadow: "inset 0 1px 0 rgba(255, 255, 255, 0.04)",
      filter: "none",
      opacity: 1,
      transition: "border-color 0.15s, background 0.15s, filter 0.2s, opacity 0.2s",
    };
  }

  return {
    padding: "7px 10px",
    fontSize: gameFontSize.xs,
    letterSpacing: 0.3,
    textAlign: "left",
    cursor: "not-allowed",
    background: lockedOut ? "rgba(12, 12, 14, 0.92)" : "rgba(14, 8, 14, 0.88)",
    color: SKILL_LOCKED_COLOR,
    border: "1px solid #2a2a2a",
    borderRadius: 3,
    fontWeight: 600,
    textShadow: "none",
    boxShadow: "none",
    filter: lockedOut ? "grayscale(1) brightness(0.72)" : "grayscale(0.85) brightness(0.85)",
    opacity: lockedOut ? 0.48 : 0.62,
    transition: "border-color 0.15s, background 0.15s, filter 0.2s, opacity 0.2s",
  };
}

export function SkillPanel({
  dp,
  sceneIdx,
  veniceParadoxUsed,
  disabled,
  onUseSkill,
}: SkillPanelProps) {
  const isMobile = useIsMobile();
  const skillPanelWidth = isMobile
    ? LEFT_METER_COLUMN_WIDTH_MOBILE
    : LEFT_METER_COLUMN_WIDTH / 2;
  const skillCtx = { dp, sceneIdx, veniceParadoxUsed };

  return (
    <div style={{ ...hudPanelStyle("8px 11px"), width: skillPanelWidth }}>
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
          const skillReady = canUseSkill(skill.id, skillCtx);
          const canUse = !disabled && skillReady;
          const lockedOut = !skillReady;

          return (
            <button
              key={skill.id}
              type="button"
              disabled={!canUse}
              aria-disabled={!canUse}
              onClick={() => {
                if (canUse) onUseSkill(skill.id);
              }}
              style={skillButtonStyle(canUse, lockedOut)}
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
