"use client";

import { useIsMobile } from "@/hooks/use-is-mobile";
import type { GameOverReason } from "@/lib/constants/ending-thresholds";
import { gameOverMeta } from "@/lib/constants/ending-thresholds";
import { theme } from "@/styles/theme";

interface GameOverScreenProps {
  reason: GameOverReason;
  onRestart: () => void;
}

export function GameOverScreen({ reason, onRestart }: GameOverScreenProps) {
  const isMobile = useIsMobile();
  const { title, subtitle } = gameOverMeta(reason);
  const emoji = "🕯️";

  return (
    <div
      style={{
        minHeight: isMobile ? "100dvh" : "100vh",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        background: theme.background,
        padding: isMobile
          ? "max(20px, env(safe-area-inset-top)) 16px max(20px, env(safe-area-inset-bottom))"
          : 32,
        textAlign: "center",
        fontFamily: "Georgia, serif",
      }}
    >
      <div style={{ fontSize: isMobile ? 48 : 60, marginBottom: 8 }}>{emoji}</div>
      <h2
        style={{
          fontSize: isMobile ? 22 : 26,
          fontWeight: "bold",
          letterSpacing: isMobile ? 2 : 4,
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
          padding: isMobile ? "12px 24px" : "10px 28px",
          width: isMobile ? "100%" : undefined,
          maxWidth: isMobile ? 320 : undefined,
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
