"use client";

import { useCallback, useEffect, useRef, useState } from "react";

export function useTypingEffect(text: string, speedMs = 28) {
  const [displayedText, setDisplayedText] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const typeRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const clearTimer = useCallback(() => {
    if (typeRef.current) {
      clearInterval(typeRef.current);
      typeRef.current = null;
    }
  }, []);

  useEffect(() => {
    clearTimer();
    if (!text) {
      setDisplayedText("");
      setIsTyping(false);
      return;
    }

    setDisplayedText("");
    setIsTyping(true);
    let idx = 0;
    typeRef.current = setInterval(() => {
      idx += 1;
      setDisplayedText(text.slice(0, idx));
      if (idx >= text.length) {
        clearTimer();
        setIsTyping(false);
      }
    }, speedMs);

    return clearTimer;
  }, [text, speedMs, clearTimer]);

  const skipToEnd = useCallback(() => {
    clearTimer();
    setDisplayedText(text);
    setIsTyping(false);
  }, [text, clearTimer]);

  return { displayedText, isTyping, skipToEnd };
}
