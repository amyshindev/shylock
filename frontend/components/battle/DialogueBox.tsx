"use client";

import { TextBox } from "@/components/ui/TextBox";
import { useDialoguePages } from "@/hooks/use-dialogue-pages";
import { useTypingEffect } from "@/hooks/use-typing-effect";
import { extractPortiaText } from "@/lib/portia-text";
import { sanitizeDialogueLine } from "@/lib/game-text";
import { dialogueTextStyle, gameFontFamily, DIALOGUE_BODY_MIN_HEIGHT, DIALOGUE_BODY_PADDING_BOTTOM, gameFontSize } from "@/styles/text-box";
import { theme } from "@/styles/theme";

const SPEAKER_LABEL: Record<string, string> = {
  NARRATOR: "NARRATOR",
  PORTIA: "포샤",
  CROWD: "군중",
};

const portiaReplyStyle = {
  margin: 0,
  color: "#e8e0d0",
  fontSize: gameFontSize.base,
  lineHeight: 1.75,
  fontFamily: gameFontFamily,
  whiteSpace: "pre-wrap" as const,
  wordBreak: "break-word" as const,
  minHeight: "5.25em",
};

interface DialogueBoxProps {
  speaker: string;
  speakerLabel?: string;
  showSpeakerTab?: boolean;
  text: string;
  /** Portia/Tubal reply flow: paging, typing, click-to-dismiss. */
  replyMode?: "portia" | "tubal";
  loadingReply?: boolean;
  disabled?: boolean;
  showAdvanceArrow?: boolean;
  onAdvance?: () => void;
  onPortiaComplete?: () => void;
}

export function DialogueBox({
  speaker,
  speakerLabel,
  showSpeakerTab = false,
  text,
  replyMode,
  loadingReply,
  disabled,
  showAdvanceArrow,
  onAdvance,
  onPortiaComplete,
}: DialogueBoxProps) {
  const isReply = replyMode != null;
  const cleanReplyText = extractPortiaText(text);
  const {
    currentPage: replyPage,
    hasNext: replyHasNext,
    advancePage,
  } = useDialoguePages(cleanReplyText, "sentences");

  const typingSource =
    loadingReply ? "" : isReply ? replyPage : sanitizeDialogueLine(text);

  const { displayedText, isTyping, skipToEnd } = useTypingEffect(typingSource);
  const content = displayedText;
  const canAdvanceLine = !disabled && !isTyping && !isReply && !loadingReply;
  const canAdvanceReply =
    isReply && !loadingReply && (isTyping || replyHasNext);
  const canCompleteReply =
    isReply && !loadingReply && !isTyping && !replyHasNext;
  const showReplyArrow = isReply && !loadingReply && !isTyping && replyHasNext;
  const showReplyCompleteArrow = canCompleteReply;
  const resolvedLabel = speakerLabel ?? SPEAKER_LABEL[speaker] ?? speaker;

  const handleClick = () => {
    if (loadingReply) return;
    if (isReply) {
      if (isTyping) skipToEnd();
      else if (replyHasNext) advancePage();
      else onPortiaComplete?.();
      return;
    }
    if (isTyping) skipToEnd();
    else if (canAdvanceLine && onAdvance) onAdvance();
  };

  const showArrow =
    (showAdvanceArrow && canAdvanceLine) || showReplyArrow || showReplyCompleteArrow;
  const isClickable = canAdvanceLine || canAdvanceReply || canCompleteReply;

  const loadingMessage =
    replyMode === "tubal"
      ? sanitizeDialogueLine(text) || "증거를 찾고 있소…"
      : "포샤가 반응하고 있다...";

  return (
    <TextBox
      speaker={speaker}
      speakerLabel={resolvedLabel}
      showSpeakerTab={showSpeakerTab}
      onClick={isClickable ? handleClick : undefined}
      showAdvanceArrow={showArrow}
      bodyStyle={{
        minHeight: DIALOGUE_BODY_MIN_HEIGHT,
        paddingBottom: DIALOGUE_BODY_PADDING_BOTTOM,
        cursor: isClickable ? "pointer" : "default",
      }}
    >
      {isReply ? (
        loadingReply ? (
          <p style={{ ...portiaReplyStyle, color: "#5a4a3a", fontSize: gameFontSize.md }}>
            {loadingMessage}
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
