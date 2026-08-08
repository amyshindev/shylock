import type { CSSProperties } from "react";

import type { Speaker } from "@/data/scenes";
import { vwSize } from "@/styles/responsive";

export const gameFontFamily =
  '"Pretendard Variable", Pretendard, "Apple SD Gothic Neo", "Malgun Gothic", "Segoe UI", sans-serif';

/**
 * Shared in-game typography scale — clamp() strings via vwSize() (see
 * styles/responsive.ts), each still rendering at exactly its old raw px at
 * the 1512px reference width. Every screen that imports this (battle HUD,
 * title/auth/records, etc.) now scales with it — that's a deliberate,
 * low-risk side effect of centralizing the token, not scope creep per
 * component.
 */
export const gameFontSize = {
  xs: vwSize(12),
  sm: vwSize(15),
  nm: vwSize(16),
  md: vwSize(18),
  base: vwSize(20),
  lg: vwSize(23),
  xl: vwSize(26),
} as const;

/** Shared HUD panel chrome (meters, evidence, skills). */
export function hudPanelStyle(padding = `${vwSize(9)} ${vwSize(14)}`, compact = false): CSSProperties {
  return {
    background: compact ? "rgba(12, 6, 16, 0.82)" : "rgba(12, 6, 16, 0.94)",
    borderRadius: compact ? 6 : 4,
    padding,
    border: "1px solid #4a2838",
    boxShadow: compact
      ? "0 1px 6px rgba(0, 0, 0, 0.35)"
      : "0 2px 8px rgba(0, 0, 0, 0.45)",
    backdropFilter: compact ? "blur(6px)" : undefined,
  };
}

export function hudLabelStyle(color: string): CSSProperties {
  return {
    color,
    fontWeight: 600,
    textShadow: "0 1px 2px rgba(0, 0, 0, 0.6)",
  };
}

export const textBox = {
  background: "rgba(18, 12, 24, 0.72)",
  border: "1px solid #3a1028",
  borderTopAccent: "3px solid #3a1028",
  borderRadius: 10,
  padding: `${vwSize(26)} ${vwSize(30)} ${vwSize(34)}`,
  fontFamily: gameFontFamily,
} as const;

const SPEAKER_TAB: Record<Speaker, { bg: string; color: string }> = {
  NARRATOR: { bg: "#1a1428", color: "#6a5a8a" },
  PORTIA: { bg: "#2a0820", color: "#c0a060" },
  BASSANIO: { bg: "#142028", color: "#6a8aaa" },
  CROWD: { bg: "#200a08", color: "#aa6040" },
  LORENZO: { bg: "#1a1828", color: "#8a9acc" },
  JESSICA: { bg: "#2a1018", color: "#c87888" },
  SHYLOCK: { bg: "#241a08", color: "#c8a868" },
  ANTONIO: { bg: "#101820", color: "#7a8a94" },
  DUKE: { bg: "#0a1c18", color: "#6aab8e" },
};

export function speakerTabStyle(speaker: string): CSSProperties {
  const palette = SPEAKER_TAB[speaker as Speaker] ?? SPEAKER_TAB.NARRATOR;
  return {
    display: "inline-block",
    background: palette.bg,
    color: palette.color,
    border: "1px solid #3a1028",
    padding: `${vwSize(8)} ${vwSize(24)}`,
    fontSize: gameFontSize.sm,
    fontWeight: 700,
    letterSpacing: 3,
    textTransform: "uppercase",
    borderRadius: "4px 4px 0 0",
    marginBottom: 0,
  };
}

export function dialogueTextStyle(speaker: string, compact = false): CSSProperties {
  return {
    margin: 0,
    fontSize: compact ? gameFontSize.md : gameFontSize.base,
    lineHeight: 1.75,
    fontFamily: gameFontFamily,
    color: speaker === "NARRATOR" ? "#9a8aaa" : "#e8e0d0",
    whiteSpace: "pre-wrap",
    wordBreak: "break-word",
    minHeight: compact ? "3.25em" : "5.25em",
  };
}

export function textBoxPanelStyle(compact = false): CSSProperties {
  return {
    background: compact ? "rgba(18, 12, 24, 0.82)" : textBox.background,
    border: textBox.border,
    borderRadius: compact ? 8 : textBox.borderRadius,
    backdropFilter: "blur(6px)",
    fontFamily: textBox.fontFamily,
    position: "relative",
  };
}

export const TEXT_BOX_MAX_WIDTH = vwSize(940);
/** Narrower dock on landscape phones so dialogue does not span edge-to-edge. */
export const TEXT_BOX_MAX_WIDTH_MOBILE = vwSize(550);

/** Stable body height (~3 lines) so the box does not resize while typing. */
export const DIALOGUE_BODY_MIN_HEIGHT = vwSize(118);

/** Bottom padding always reserved for the advance arrow slot. */
export const DIALOGUE_BODY_PADDING_BOTTOM = vwSize(32);

export function textBoxDockStyle(compact = false): CSSProperties {
  return {
    flexShrink: 0,
    width: "100%",
    padding: compact ? `0 14vw ${vwSize(8)}` : `0 ${vwSize(16)} ${vwSize(20)}`,
    fontFamily: textBox.fontFamily,
    background: "transparent",
  };
}

export function textBoxDockInnerStyle(compact = false): CSSProperties {
  return {
    width: "100%",
    maxWidth: compact ? TEXT_BOX_MAX_WIDTH_MOBILE : TEXT_BOX_MAX_WIDTH,
    margin: "0 auto",
  };
}

export function choiceButtonStyle(compact = false): CSSProperties {
  return {
    display: "flex",
    alignItems: compact ? "flex-start" : "center",
    justifyContent: "space-between",
    flexWrap: compact ? "wrap" : "nowrap",
    gap: compact ? vwSize(8) : vwSize(12),
    width: "100%",
    padding: compact ? `${vwSize(8)} ${vwSize(10)}` : `${vwSize(14)} ${vwSize(20)}`,
    textAlign: "left",
    background: "#100510",
    border: "1px solid #3a1828",
    borderRadius: 2,
    color: "#e0c090",
    cursor: "pointer",
    fontSize: compact ? gameFontSize.sm : gameFontSize.md,
    fontFamily: textBox.fontFamily,
    lineHeight: 1.5,
    transition: "all 0.15s",
  };
}

export function nextSceneButtonStyle(): CSSProperties {
  return {
    width: "100%",
    padding: vwSize(15),
    background: "#1a0810",
    color: "#c0a060",
    border: "1px solid #4a1828",
    borderRadius: 2,
    cursor: "pointer",
    fontFamily: textBox.fontFamily,
    fontSize: gameFontSize.nm,
    letterSpacing: 3,
    transition: "all 0.15s",
  };
}

export function staticTextBoxStyle(padding = `${vwSize(20)} ${vwSize(24)}`): CSSProperties {
  return {
    ...textBoxPanelStyle(),
    padding,
    textAlign: "center",
  };
}
