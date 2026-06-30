export const theme = {
  background: "#08030a",
  panelBackground: "#0d0510",
  border: "#3a1a28",
  gold: "#ffd700",
  red: "#8b0000",
  textMuted: "#5a4a3a",
  textBright: "#c8a080",
} as const;

export type Theme = typeof theme;
