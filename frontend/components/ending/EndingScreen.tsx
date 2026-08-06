"use client";

import { useCallback, useMemo, useState } from "react";

import { DialogueBox } from "@/components/battle/DialogueBox";
import { useAppShellHeight, useIsMobile } from "@/hooks/use-is-mobile";
import type { EndingResponse } from "@/lib/api-client/types";
import { splitIntoSentences } from "@/lib/portia-text";
import {
  gameFontFamily,
  textBoxDockInnerStyle,
  textBoxDockStyle,
} from "@/styles/text-box";
import { theme } from "@/styles/theme";

interface EndingScreenProps {
  ending: EndingResponse;
  onRestart: () => void;
}

// Blackout hold before navigating away, for the "여운" pause the ending asked
// for — the fade-in on the other side lives in TitleScreen (it doesn't know
// whether it's being reached from here or a fresh visit, so it always fades
// in on mount; that reads fine either way).
const FADE_OUT_MS = 3000;

/**
 * Same black-screen + docked-textbox, one-line-at-a-time format as
 * PrologueScreen — ending_text is backend-generated free narration (not
 * pre-split like PROLOGUE_LINES), so it's chunked into sentence "lines" with
 * splitIntoSentences (the same splitter DialogueBox's Portia reply mode
 * uses). No ending-name/title card (meta.title, e.g. "구원받은 자") — the
 * ending type is still resolved server-side and drives ending_text itself,
 * it's just never rendered as a label here.
 */
export function EndingScreen({ ending, onRestart }: EndingScreenProps) {
  const appShellHeight = useAppShellHeight();
  const isMobile = useIsMobile();
  const [lineIdx, setLineIdx] = useState(0);
  const [fadingOut, setFadingOut] = useState(false);

  const lines = useMemo(() => {
    const sentences = splitIntoSentences(ending.ending_text);
    return sentences.length > 0 ? sentences : [ending.ending_text];
  }, [ending.ending_text]);

  const isLastLine = lineIdx >= lines.length - 1;
  const currentLine = lines[lineIdx] ?? "";

  const advance = useCallback(() => {
    if (isLastLine) {
      setFadingOut(true);
      window.setTimeout(onRestart, FADE_OUT_MS);
      return;
    }
    setLineIdx((index) => index + 1);
  }, [isLastLine, onRestart]);

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
              showAdvanceArrow={!fadingOut}
              onAdvance={advance}
            />
          </div>
        </div>
      </div>

      <div
        aria-hidden
        style={{
          position: "fixed",
          inset: 0,
          zIndex: 100,
          background: "#000",
          opacity: fadingOut ? 1 : 0,
          pointerEvents: fadingOut ? "auto" : "none",
          transition: "opacity 1.5s ease-in",
        }}
      />
    </div>
  );
}
