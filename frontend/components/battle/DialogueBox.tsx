"use client";

import { TextBox } from "@/components/ui/TextBox";
import { useDialoguePages } from "@/hooks/use-dialogue-pages";
import { useTypingEffect } from "@/hooks/use-typing-effect";
import { extractPortiaText } from "@/lib/portia-text";
import { dialogueTextStyle, gameFontFamily, DIALOGUE_BODY_MIN_HEIGHT, DIALOGUE_BODY_PADDING_BOTTOM } from "@/styles/text-box";
import { theme } from "@/styles/theme";

const SPEAKER_LABEL: Record<string, string> = {
  NARRATOR: "NARRATOR",
  PORTIA: "PORTIA",
  CROWD: "군중",
};

const portiaReplyStyle = {
  margin: 0,
  color: "#e8e0d0",
  fontSize: 15,
  lineHeight: 1.75,
  fontFamily: gameFontFamily,
  whiteSpace: "pre-wrap" as const,
  wordBreak: "break-word" as const,
  minHeight: "5.25em",
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
  const cleanPortiaText = extractPortiaText(text);
  const {
    currentPage: portiaPage,
    hasNext: portiaHasNext,
    advancePage,
  } = useDialoguePages(cleanPortiaText, "sentences");

  const typingSource =
    loadingReply ? "" : isPortiaReply ? portiaPage : text;

  const { displayedText, isTyping, skipToEnd } = useTypingEffect(typingSource);
  const content = displayedText;
  const canAdvanceLine = !disabled && !isTyping && !isPortiaReply && !loadingReply;
  const canAdvancePortia =
    isPortiaReply && !loadingReply && (isTyping || portiaHasNext);
  const showPortiaArrow = isPortiaReply && !loadingReply && !isTyping && portiaHasNext;
  const resolvedLabel = speakerLabel ?? SPEAKER_LABEL[speaker] ?? speaker;

  const handleClick = () => {
    if (loadingReply) return;
    if (isPortiaReply) {
      if (isTyping) skipToEnd();
      else if (portiaHasNext) advancePage();
      return;
    }
    if (isTyping) skipToEnd();
    else if (canAdvanceLine && onAdvance) onAdvance();
  };

  const showArrow = (showAdvanceArrow && canAdvanceLine) || showPortiaArrow;

  return (
    <TextBox
      speaker={isPortiaReply || loadingReply ? "PORTIA" : speaker}
      speakerLabel={isPortiaReply || loadingReply ? "PORTIA · 판사" : resolvedLabel}
      onClick={canAdvanceLine || canAdvancePortia ? handleClick : undefined}
      showAdvanceArrow={showArrow}
      bodyStyle={{
        minHeight: DIALOGUE_BODY_MIN_HEIGHT,
        paddingBottom: DIALOGUE_BODY_PADDING_BOTTOM,
        cursor: canAdvanceLine || canAdvancePortia ? "pointer" : "default",
      }}
    >
      {isPortiaReply ? (
        loadingReply ? (
          <p style={{ ...portiaReplyStyle, color: "#5a4a3a", fontSize: 13 }}>
            포샤가 반응하고 있다...
          </p>
        ) : (
          <p style={portiaReplyStyle}>
            {content}
            {isTyping && (
              <span style={{ animation: "blink 0.7s infinite", color: theme.gold }}>▌</span>
            )}
          </p>
        )
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
