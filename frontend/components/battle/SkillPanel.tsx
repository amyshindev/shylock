"use client";

import { useState, type CSSProperties } from "react";
import { createPortal } from "react-dom";

import { useIsMobile } from "@/hooks/use-is-mobile";
import {
  SKILLS,
  canUseSkill,
  type SkillId,
} from "@/lib/constants/game-balance";
import { gameFontSize, hudLabelStyle, hudPanelStyle } from "@/styles/text-box";

import {
  LEFT_METER_COLUMN_WIDTH,
  LANDSCAPE_HUD_RAIL_WIDTH,
} from "./MeterDisplay";

const SKILL_ENABLED_COLOR = "#f0d8c8";
const SKILL_LOCKED_COLOR = "#5c5c5c";

const SKILL_ICON: Record<SkillId, string> = {
  launcelot: "🃏",
  tubal: "🤝",
  venice_paradox: "⚔️",
};

interface SkillPanelProps {
  dp: number;
  sceneIdx: number;
  veniceParadoxUsed: boolean;
  disabled?: boolean;
  onUseSkill: (skillId: SkillId) => void;
  horizontal?: boolean;
  /** Circular emoji buttons only — no captions. */
  iconsOnly?: boolean;
}

function skillButtonStyle(
  canUse: boolean,
  lockedOut: boolean,
  iconsOnly: boolean,
): CSSProperties {
  if (iconsOnly) {
    return {
      width: 34,
      height: 34,
      padding: 0,
      fontSize: 15,
      display: "inline-flex",
      alignItems: "center",
      justifyContent: "center",
      cursor: canUse ? "pointer" : "not-allowed",
      background: canUse ? "rgba(20, 10, 18, 0.95)" : "rgba(12, 12, 14, 0.92)",
      color: canUse ? SKILL_ENABLED_COLOR : SKILL_LOCKED_COLOR,
      border: `1px solid ${canUse ? "#5a3848" : "#2a2a2a"}`,
      borderRadius: "50%",
      fontWeight: 600,
      filter: lockedOut ? "grayscale(1) brightness(0.72)" : canUse ? "none" : "grayscale(0.85)",
      opacity: lockedOut ? 0.48 : canUse ? 1 : 0.62,
      flexShrink: 0,
      transition: "border-color 0.15s, background 0.15s, filter 0.2s, opacity 0.2s",
    };
  }

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
  horizontal: horizontalProp,
  iconsOnly = false,
}: SkillPanelProps) {
  const isMobile = useIsMobile();
  const [confirmSkillId, setConfirmSkillId] = useState<SkillId | null>(null);
  const confirmSkill = confirmSkillId
    ? SKILLS.find((skill) => skill.id === confirmSkillId)
    : undefined;
  const horizontal = iconsOnly || (horizontalProp ?? false);
  const skillPanelWidth = iconsOnly
    ? LANDSCAPE_HUD_RAIL_WIDTH
    : horizontal
      ? undefined
      : isMobile
        ? LANDSCAPE_HUD_RAIL_WIDTH
        : LEFT_METER_COLUMN_WIDTH / 2;
  const skillCtx = { dp, sceneIdx, veniceParadoxUsed };

  return (
    <div
      style={{
        ...hudPanelStyle(iconsOnly || horizontal ? "4px 6px" : "8px 11px", iconsOnly || horizontal),
        width: skillPanelWidth,
        boxSizing: "border-box",
        display: horizontal || iconsOnly ? "flex" : "block",
        flexDirection: iconsOnly ? "column" : undefined,
        alignItems: iconsOnly ? "stretch" : horizontal ? "center" : undefined,
        justifyContent: iconsOnly ? "space-between" : undefined,
        gap: horizontal || iconsOnly ? 6 : undefined,
        flexShrink: 0,
        maxWidth: "100%",
      }}
    >
      {(!horizontal || iconsOnly) && (
        <div
          style={{
            ...hudLabelStyle("#e8dce4"),
            fontSize: horizontal ? 10 : gameFontSize.xs,
            letterSpacing: 0.8,
            marginBottom: horizontal ? 0 : 6,
            flexShrink: 0,
          }}
        >
          스킬
        </div>
      )}
      <div
        style={{
          display: "flex",
          flexDirection: iconsOnly || horizontal ? "row" : "column",
          gap: iconsOnly ? 4 : horizontal ? 4 : 5,
          flex: iconsOnly ? 1 : undefined,
          justifyContent: iconsOnly ? "space-between" : undefined,
          width: iconsOnly ? "100%" : undefined,
        }}
      >
        {SKILLS.map((skill) => {
          const skillReady = canUseSkill(skill.id, skillCtx);
          const canUse = !disabled && skillReady;
          const lockedOut = !skillReady;
          const content = iconsOnly ? SKILL_ICON[skill.id] : skill.label;

          return (
            <button
              key={skill.id}
              type="button"
              disabled={!canUse}
              aria-disabled={!canUse}
              title={skill.label}
              aria-label={skill.label}
              onClick={() => {
                if (!canUse) return;
                if (iconsOnly) {
                  setConfirmSkillId((prev) => (prev === skill.id ? null : skill.id));
                } else {
                  onUseSkill(skill.id);
                }
              }}
              style={skillButtonStyle(canUse, lockedOut, iconsOnly)}
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
              {content}
            </button>
          );
        })}
      </div>

      {iconsOnly &&
        confirmSkill &&
        typeof document !== "undefined" &&
        createPortal(
          <div
            onClick={() => setConfirmSkillId(null)}
            style={{
              position: "fixed",
              inset: 0,
              zIndex: 30,
              background: "rgba(6, 3, 8, 0.45)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            <div
              onClick={(e) => e.stopPropagation()}
              style={{
                ...hudPanelStyle("14px 16px", false),
                width: 240,
                maxWidth: "80vw",
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                gap: 10,
              }}
            >
              <div
                style={{
                  ...hudLabelStyle(SKILL_ENABLED_COLOR),
                  fontSize: gameFontSize.sm,
                  lineHeight: 1.4,
                  textAlign: "center",
                }}
              >
                {confirmSkill.label}
              </div>
              <button
                type="button"
                onClick={() => {
                  if (!disabled && canUseSkill(confirmSkill.id, skillCtx)) {
                    onUseSkill(confirmSkill.id);
                  }
                  setConfirmSkillId(null);
                }}
                style={{
                  padding: "7px 24px",
                  fontSize: gameFontSize.xs,
                  fontWeight: 700,
                  letterSpacing: 1,
                  cursor: "pointer",
                  background: "rgba(90, 30, 48, 0.95)",
                  color: SKILL_ENABLED_COLOR,
                  border: "1px solid #7a5060",
                  borderRadius: 3,
                }}
              >
                사용
              </button>
            </div>
          </div>,
          document.body,
        )}
    </div>
  );
}
