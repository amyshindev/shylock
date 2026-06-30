"use client";

import { TextBox } from "@/components/ui/TextBox";
import type { EndingResponse } from "@/lib/api-client/types";
import { theme } from "@/styles/theme";

interface EndingScreenProps {
  ending: EndingResponse;
  onRestart: () => void;
}

function endingTitle(dignity: number): string {
  if (dignity >= 70) return "존엄을 지켰다";
  if (dignity >= 40) return "그는 패했다";
  return "침묵만이 남았다";
}

function endingEmoji(dignity: number): string {
  if (dignity >= 70) return "⚖️";
  if (dignity >= 40) return "🕯️";
  return "💔";
}

export function EndingScreen({ ending, onRestart }: EndingScreenProps) {
  const won = ending.dignity >= 60;
  const dignityColor =
    ending.dignity > 60 ? theme.gold : ending.dignity > 30 ? "#ff8800" : "#ff4444";
  const confColor =
    ending.confidence > 60 ? "#44ff88" : ending.confidence > 30 ? "#44aaff" : "#ff4444";

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
      <div style={{ fontSize: 60, marginBottom: 8 }}>{endingEmoji(ending.dignity)}</div>
      <h2
        style={{
          fontSize: 26,
          fontWeight: "bold",
          letterSpacing: 4,
          color: won ? theme.gold : "#c84040",
          margin: "0 0 20px",
          textShadow: won ? "0 0 20px rgba(255, 215, 0, 0.4)" : "0 0 20px rgba(204, 0, 0, 0.4)",
        }}
      >
        {endingTitle(ending.dignity)}
      </h2>

      <div style={{ display: "flex", gap: 40, marginBottom: 24 }}>
        {[
          ["존엄", ending.dignity, dignityColor],
          ["확신도", ending.confidence, confColor],
        ].map(([label, val, color]) => (
          <div key={label as string}>
            <div style={{ color: theme.textMuted, fontSize: 10, letterSpacing: 2, marginBottom: 4 }}>
              {label}
            </div>
            <div style={{ color: color as string, fontSize: 28, fontWeight: "bold" }}>
              {val}
            </div>
          </div>
        ))}
      </div>

      <TextBox
        speaker="NARRATOR"
        speakerLabel="NARRATOR"
        style={{ maxWidth: 480, marginBottom: 24 }}
        bodyStyle={{ padding: "20px 24px" }}
      >
        <p
          style={{
            margin: 0,
            color: theme.textBright,
            fontSize: 14,
            lineHeight: 2,
            fontStyle: "italic",
            whiteSpace: "pre-wrap",
            textAlign: "center",
          }}
        >
          {ending.ending_text}
        </p>
      </TextBox>

      <button
        type="button"
        onClick={onRestart}
        style={{
          padding: "10px 28px",
          background: "transparent",
          color: theme.textMuted,
          border: `1px solid #3a2a2a`,
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
