"use client";

import { useCallback, useState } from "react";

import { DialogueBox } from "@/components/battle/DialogueBox";
import { PROLOGUE_LINES } from "@/lib/constants/prologue";
import {
  gameFontFamily,
  gameFontSize,
  textBoxDockInnerStyle,
  textBoxDockStyle,
} from "@/styles/text-box";
import { theme } from "@/styles/theme";

interface PrologueScreenProps {
  onComplete: () => void;
}

export function PrologueScreen({ onComplete }: PrologueScreenProps) {
  const [lineIdx, setLineIdx] = useState(0);
  const isLastLine = lineIdx >= PROLOGUE_LINES.length - 1;
  const currentLine = PROLOGUE_LINES[lineIdx] ?? "";

  const advance = useCallback(() => {
    if (isLastLine) {
      onComplete();
      return;
    }
    setLineIdx((index) => index + 1);
  }, [isLastLine, onComplete]);

  return (
    <div
      style={{
        position: "relative",
        minHeight: "100vh",
        display: "flex",
        flexDirection: "column",
        background: theme.background,
        color: theme.textBright,
        overflow: "hidden",
        fontFamily: gameFontFamily,
      }}
    >
      <div
        style={{
          position: "absolute",
          inset: 0,
          background: "linear-gradient(to bottom, #0a060c 0%, #050308 45%, #08050a 100%)",
        }}
      />

      <button
        type="button"
        onClick={onComplete}
        style={{
          position: "absolute",
          top: 16,
          right: 16,
          zIndex: 2,
          padding: "8px 14px",
          fontSize: gameFontSize.sm,
          fontFamily: gameFontFamily,
          letterSpacing: 1,
          color: "#6a5a6a",
          background: "rgba(12, 8, 14, 0.85)",
          border: "1px solid #3a2830",
          borderRadius: 4,
          cursor: "pointer",
        }}
      >
        건너뛰기
      </button>

      <div
        style={{
          position: "relative",
          zIndex: 1,
          display: "flex",
          flexDirection: "column",
          flex: 1,
        }}
      >
        <div style={{ flex: 1, minHeight: 0 }} />

        <div style={textBoxDockStyle()}>
          <div style={textBoxDockInnerStyle()}>
            <DialogueBox
              speaker="NARRATOR"
              showSpeakerTab={false}
              text={currentLine}
              showAdvanceArrow
              onAdvance={advance}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
