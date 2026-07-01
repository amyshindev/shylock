"use client";

import type { GameOverReason } from "@/lib/constants/ending-thresholds";
import { gameOverMeta } from "@/lib/constants/ending-thresholds";
import { theme } from "@/styles/theme";

interface GameOverScreenProps {
  reason: GameOverReason;
  onRestart: () => void;
}

export function GameOverScreen({ reason, onRestart }: GameOverScreenProps) {
  const { title, subtitle } = gameOverMeta(reason);
  const emoji = reason === "shylock_hp" ? "⚖️" : "🕯️";

  return (
    <div
      style={{
        minHeight: "100vh",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        background: theme.background,
        padding: 32,
        textAlign: "center",
        fontFamily: "Georgia, serif",
      }}
    >
      <div style={{ fontSize: 60, marginBottom: 8 }}>{emoji}</div>
      <h2
        style={{
          fontSize: 26,
          fontWeight: "bold",
          letterSpacing: 4,
          color: "#c84040",
          margin: "0 0 12px",
          textShadow: "0 0 20px rgba(204, 0, 0, 0.4)",
        }}
      >
        {title}
      </h2>
      <p
        style={{
          margin: "0 0 32px",
          color: theme.textMuted,
          fontSize: 14,
          lineHeight: 1.8,
          maxWidth: 420,
        }}
      >
        {subtitle}
      </p>
      <button
        type="button"
        onClick={onRestart}
        style={{
          padding: "10px 28px",
          background: "transparent",
          color: theme.textMuted,
          border: "1px solid #3a2a2a",
          borderRadius: 2,
          cursor: "pointer",
          fontSize: 12,
          letterSpacing: 3,
        }}
      >
        다시 법정에 서다
      </button>
    </div>
  );
}
