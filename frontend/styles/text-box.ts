import type { CSSProperties } from "react";

import type { Speaker } from "@/data/scenes";

export const gameFontFamily =
  '"Pretendard Variable", Pretendard, "Apple SD Gothic Neo", "Malgun Gothic", "Segoe UI", sans-serif';

/** Shared in-game typography scale (px). */
export const gameFontSize = {
  xs: 11,
  sm: 13,
  nm: 14,
  md: 15,
  base: 17,
  lg: 19,
  xl: 22,
} as const;

/** Shared HUD panel chrome (meters, evidence, skills). */
export function hudPanelStyle(padding = "6px 11px"): CSSProperties {
  return {
    background: "rgba(12, 6, 16, 0.94)",
    borderRadius: 4,
    padding,
    border: "1px solid #4a2838",
    boxShadow: "0 2px 8px rgba(0, 0, 0, 0.45)",
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
  padding: "20px 24px 28px",
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
};

export function speakerTabStyle(speaker: string): CSSProperties {
  const palette = SPEAKER_TAB[speaker as Speaker] ?? SPEAKER_TAB.NARRATOR;
  return {
    display: "inline-block",
    background: palette.bg,
    color: palette.color,
    border: "1px solid #3a1028",
    padding: "6px 20px",
    fontSize: gameFontSize.sm,
    fontWeight: 700,
    letterSpacing: 3,
    textTransform: "uppercase",
    borderRadius: "4px 4px 0 0",
    marginBottom: 0,
  };
}

export function dialogueTextStyle(speaker: string): CSSProperties {
  return {
    margin: 0,
    fontSize: gameFontSize.base,
    lineHeight: 1.75,
    fontFamily: gameFontFamily,
    color: speaker === "NARRATOR" ? "#9a8aaa" : "#e8e0d0",
    whiteSpace: "pre-wrap",
    wordBreak: "break-word",
    minHeight: "5.25em",
  };
}

export function textBoxPanelStyle(): CSSProperties {
  return {
    background: textBox.background,
    border: textBox.border,
    borderRadius: textBox.borderRadius,
    backdropFilter: "blur(4px)",
    fontFamily: textBox.fontFamily,
    position: "relative",
  };
}

export const TEXT_BOX_MAX_WIDTH = 680;

/** Stable body height (~3 lines) so the box does not resize while typing. */
export const DIALOGUE_BODY_MIN_HEIGHT = 96;

/** Bottom padding always reserved for the advance arrow slot. */
export const DIALOGUE_BODY_PADDING_BOTTOM = 28;

export function textBoxDockStyle(): CSSProperties {
  return {
    flexShrink: 0,
    width: "100%",
    padding: "0 16px 20px",
    fontFamily: textBox.fontFamily,
    background: "transparent",
  };
}

export function textBoxDockInnerStyle(): CSSProperties {
  return {
    width: "100%",
    maxWidth: TEXT_BOX_MAX_WIDTH,
    margin: "0 auto",
  };
}

export function choiceButtonStyle(): CSSProperties {
  return {
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    gap: 12,
    width: "100%",
    padding: "11px 16px",
    textAlign: "left",
    background: "#100510",
    border: "1px solid #3a1828",
    borderRadius: 2,
    color: "#e0c090",
    cursor: "pointer",
    fontSize: gameFontSize.md,
    fontFamily: textBox.fontFamily,
    lineHeight: 1.5,
    transition: "all 0.15s",
  };
}

export function nextSceneButtonStyle(): CSSProperties {
  return {
    width: "100%",
    padding: "12px",
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

export function staticTextBoxStyle(padding = "20px 24px"): CSSProperties {
  return {
    ...textBoxPanelStyle(),
    padding,
    textAlign: "center",
  };
}
