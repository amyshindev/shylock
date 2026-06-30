"use client";

import { TextBox } from "@/components/ui/TextBox";
import { useTypingEffect } from "@/hooks/use-typing-effect";
import { dialogueTextStyle } from "@/styles/text-box";
import { theme } from "@/styles/theme";

const SPEAKER_LABEL: Record<string, string> = {
  NARRATOR: "NARRATOR",
  PORTIA: "PORTIA",
  CROWD: "군중",
};

interface DialogueBoxProps {
  speaker: string;
  speakerLabel?: string;
  text: string;
  isPortiaReply?: boolean;
  loadingReply?: boolean;
  disabled?: boolean;
  showAdvanceArrow?: boolean;
  onAdvance?: () => void;
}

export function DialogueBox({
  speaker,
  speakerLabel,
  text,
  isPortiaReply,
  loadingReply,
  disabled,
  showAdvanceArrow,
  onAdvance,
}: DialogueBoxProps) {
  const { displayedText, isTyping, skipToEnd } = useTypingEffect(
    isPortiaReply || loadingReply ? "" : text,
  );
  const content = isPortiaReply ? text : displayedText;
  const canAdvance = !disabled && !isTyping && !isPortiaReply && !loadingReply;
  const resolvedLabel = speakerLabel ?? SPEAKER_LABEL[speaker] ?? speaker;

  const handleClick = () => {
    if (isPortiaReply || loadingReply) return;
    if (isTyping) skipToEnd();
    else if (canAdvance && onAdvance) onAdvance();
  };

  return (
    <TextBox
      speaker={isPortiaReply || loadingReply ? "PORTIA" : speaker}
      speakerLabel={isPortiaReply || loadingReply ? "PORTIA · 판사" : resolvedLabel}
      onClick={canAdvance ? handleClick : undefined}
      showAdvanceArrow={showAdvanceArrow && canAdvance}
      style={{ borderRadius: 0, borderLeft: "none", borderRight: "none", borderBottom: "none" }}
      bodyStyle={{ paddingBottom: showAdvanceArrow && canAdvance ? 28 : 14 }}
    >
      {isPortiaReply ? (
        <div>
          <div
            style={{
              fontSize: 10,
              color: "#5a3a4a",
              letterSpacing: 2,
              marginBottom: 6,
            }}
          >
            ⚖️ PORTIA의 반응
          </div>
          {loadingReply ? (
            <p
              style={{
                margin: 0,
                color: "#5a4a3a",
                fontStyle: "italic",
                fontSize: 13,
              }}
            >
              포샤가 반응하고 있다...
            </p>
          ) : (
            <p
              style={{
                margin: 0,
                color: "#c0a060",
                fontSize: 14,
                lineHeight: 1.8,
                fontStyle: "italic",
              }}
            >
              {text}
            </p>
          )}
        </div>
      ) : (
        <p style={dialogueTextStyle(speaker)}>
          {content}
          {isTyping && (
            <span style={{ animation: "blink 0.7s infinite", color: theme.gold }}>▌</span>
          )}
        </p>
      )}
    </TextBox>
  );
}
