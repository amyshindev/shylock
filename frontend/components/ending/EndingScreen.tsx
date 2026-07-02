"use client";

import { TextBox } from "@/components/ui/TextBox";
import type { EndingResponse } from "@/lib/api-client/types";
import {
  getEndingMetaByType,
  type EndingType,
} from "@/lib/constants/ending-thresholds";
import { theme } from "@/styles/theme";

interface EndingScreenProps {
  ending: EndingResponse;
  onRestart: () => void;
}

export function EndingScreen({ ending, onRestart }: EndingScreenProps) {
  const meta = getEndingMetaByType(ending.ending_type as EndingType);

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
      <div style={{ fontSize: 60, marginBottom: 8 }}>{meta.emoji}</div>
      <h2
        style={{
          fontSize: 26,
          fontWeight: "bold",
          letterSpacing: 4,
          color: theme.gold,
          margin: "0 0 8px",
          textShadow: "0 0 20px rgba(255, 215, 0, 0.4)",
        }}
      >
        {meta.title}
      </h2>
      <p
        style={{
          margin: "0 0 24px",
          color: theme.textMuted,
          fontSize: 13,
          letterSpacing: 1,
          fontStyle: "italic",
        }}
      >
        {meta.subtitle}
      </p>

      <div style={{ display: "flex", gap: 40, marginBottom: 24 }}>
        {[
          ["HP", ending.shylock_hp, "#ff6666"],
          ["DP", ending.dp, theme.gold],
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
