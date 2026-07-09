"use client";

import { useCallback, useState } from "react";

import { DialogueBox } from "@/components/battle/DialogueBox";
import { useAppShellHeight, useIsMobile } from "@/hooks/use-is-mobile";
import { PROLOGUE_LINES } from "@/lib/constants/prologue";
import {
  gameFontFamily,
  textBoxDockInnerStyle,
  textBoxDockStyle,
} from "@/styles/text-box";
import { theme } from "@/styles/theme";

interface PrologueScreenProps {
  onComplete: () => void;
}

export function PrologueScreen({ onComplete }: PrologueScreenProps) {
  const appShellHeight = useAppShellHeight();
  const isMobile = useIsMobile();
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
        minHeight: appShellHeight,
        display: "flex",
        flexDirection: "column",
        background: theme.background,
        color: theme.textBright,
        overflow: "hidden",
        fontFamily: gameFontFamily,
        paddingTop: "env(safe-area-inset-top)",
        paddingBottom: "env(safe-area-inset-bottom)",
      }}
    >
      <div
        style={{
          position: "absolute",
          inset: 0,
          background: "linear-gradient(to bottom, #0a060c 0%, #050308 45%, #08050a 100%)",
        }}
      />

      <div
        style={{
          position: "relative",
          zIndex: 1,
          display: "flex",
          flexDirection: "column",
          flex: 1,
          minHeight: 0,
        }}
      >
        <div style={{ flex: 1, minHeight: 0 }} />

        <div style={textBoxDockStyle(isMobile)}>
          <div style={textBoxDockInnerStyle(isMobile)}>
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
