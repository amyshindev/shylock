"use client";

import { TextBox } from "@/components/ui/TextBox";
import { gameFontSize } from "@/styles/text-box";
import { theme } from "@/styles/theme";

interface ClimaxOverlayProps {
  quote: string;
  onContinue: () => void;
}

export function ClimaxOverlay({ quote, onContinue }: ClimaxOverlayProps) {
  return (
    <div
      style={{
        position: "fixed",
        inset: 0,
        zIndex: 60,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        background: "rgba(0, 0, 0, 0.82)",
        padding: 24,
      }}
    >
      <TextBox
        speaker="NARRATOR"
        speakerLabel="ACT III · SCENE 1"
        style={{
          maxWidth: 480,
          width: "min(520px, 100%)",
          border: `2px solid ${theme.gold}`,
          boxShadow: "0 0 60px rgba(255, 215, 0, 0.19)",
        }}
        bodyStyle={{ padding: "24px 28px", textAlign: "center" }}
        footer={
          <div style={{ padding: "0 12px 16px", textAlign: "center" }}>
            <div
              style={{
                color: "#6a4a2a",
                fontSize: gameFontSize.sm,
                marginBottom: 18,
                letterSpacing: 2,
              }}
            >
              — William Shakespeare
            </div>
            <button
              type="button"
              onClick={onContinue}
              style={{
                background: theme.red,
                color: theme.gold,
                border: "none",
                padding: "12px 32px",
                borderRadius: 2,
                cursor: "pointer",
                fontFamily: "Georgia, serif",
                fontSize: gameFontSize.md,
                letterSpacing: 2,
              }}
            >
              계속
            </button>
          </div>
        }
      >
        <p
          style={{
            margin: 0,
            color: "#f0d090",
            fontSize: gameFontSize.base,
            lineHeight: 2.2,
            fontStyle: "italic",
            whiteSpace: "pre-wrap",
          }}
        >
          {quote}
        </p>
      </TextBox>
    </div>
  );
}
