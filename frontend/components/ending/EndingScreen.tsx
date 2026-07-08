"use client";

import { TextBox } from "@/components/ui/TextBox";
import { useIsMobile } from "@/hooks/use-is-mobile";
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
  const isMobile = useIsMobile();
  const meta = getEndingMetaByType(ending.ending_type as EndingType);

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
      <div style={{ fontSize: isMobile ? 48 : 60, marginBottom: 8 }}>{meta.emoji}</div>
      <h2
        style={{
          fontSize: isMobile ? 22 : 26,
          fontWeight: "bold",
          letterSpacing: isMobile ? 2 : 4,
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

      <div style={{ marginBottom: 24 }}>
        <div style={{ color: theme.textMuted, fontSize: 10, letterSpacing: 2, marginBottom: 4 }}>
          DP
        </div>
        <div style={{ color: theme.gold, fontSize: isMobile ? 24 : 28, fontWeight: "bold" }}>
          {ending.dp}
        </div>
      </div>

      <TextBox
        speaker="NARRATOR"
        speakerLabel="NARRATOR"
        style={{ maxWidth: 480, width: "100%", marginBottom: 24 }}
        bodyStyle={{ padding: isMobile ? "16px 18px" : "20px 24px" }}
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
