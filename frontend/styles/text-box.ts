import type { CSSProperties } from "react";

import type { Speaker } from "@/data/scenes";

export const textBox = {
  background: "rgba(18, 12, 24, 0.85)",
  border: "1px solid #3a1028",
  borderTopAccent: "3px solid #3a1028",
  borderRadius: 10,
  padding: "20px 24px 28px",
  fontFamily: "Georgia, 'Times New Roman', serif",
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
    lineHeight: 1.8,
    color: speaker === "NARRATOR" ? "#9a8aaa" : "#e8e0d0",
    whiteSpace: "pre-wrap",
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

export function textBoxDockStyle(): CSSProperties {
  return {
    flexShrink: 0,
    width: "100%",
    background: "#08030a",
    borderTop: textBox.borderTopAccent,
    fontFamily: textBox.fontFamily,
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
