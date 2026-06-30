import type { CSSProperties } from "react";

import type { Speaker } from "@/data/scenes";

export const gameFontFamily =
  '"Pretendard Variable", Pretendard, "Apple SD Gothic Neo", "Malgun Gothic", "Segoe UI", sans-serif';

export const textBox = {
  background: "rgba(18, 12, 24, 0.85)",
  border: "1px solid #3a1028",
  borderTopAccent: "3px solid #3a1028",
  borderRadius: 10,
  padding: "20px 24px 28px",
  fontFamily: gameFontFamily,
} as const;

const SPEAKER_TAB: Record<Speaker, { bg: string; color: string }> = {
  NARRATOR: { bg: "#1a1428", color: "#6a5a8a" },
  PORTIA: { bg: "#2a0820", color: "#c0a060" },
  CROWD: { bg: "#200a08", color: "#aa6040" },
};

export function speakerTabStyle(speaker: string): CSSProperties {
  const palette = SPEAKER_TAB[speaker as Speaker] ?? SPEAKER_TAB.NARRATOR;
  return {
    display: "inline-block",
    background: palette.bg,
    color: palette.color,
    border: "1px solid #3a1028",
    padding: "5px 18px",
    fontSize: 11,
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
    fontSize: 15,
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

export const TEXT_BOX_MAX_WIDTH = 640;

/** Stable body height (~3 lines) so the box does not resize while typing. */
export const DIALOGUE_BODY_MIN_HEIGHT = 84;

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
    padding: "9px 14px",
    textAlign: "left",
    background: "#100510",
    border: "1px solid #3a1828",
    borderRadius: 2,
    color: "#e0c090",
    cursor: "pointer",
    fontSize: 13,
    fontFamily: textBox.fontFamily,
    lineHeight: 1.5,
    transition: "all 0.15s",
  };
}

export function nextSceneButtonStyle(): CSSProperties {
  return {
    width: "100%",
    padding: "10px",
    background: "#1a0810",
    color: "#c0a060",
    border: "1px solid #4a1828",
    borderRadius: 2,
    cursor: "pointer",
    fontFamily: textBox.fontFamily,
    fontSize: 12,
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
