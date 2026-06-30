"use client";

import { useCallback, useEffect, useMemo, useState } from "react";

import { splitIntoDialoguePages, splitIntoSentences } from "@/lib/portia-text";

export type DialoguePageMode = "sentences" | "chars";

export function useDialoguePages(
  text: string,
  mode: DialoguePageMode = "sentences",
  maxChars = 110,
) {
  const pages = useMemo(
    () =>
      mode === "sentences"
        ? splitIntoSentences(text)
        : splitIntoDialoguePages(text, maxChars),
    [text, mode, maxChars],
  );
  const [pageIndex, setPageIndex] = useState(0);

  useEffect(() => {
    setPageIndex(0);
  }, [text]);

  const currentPage = pages[pageIndex] ?? "";
  const hasNext = pageIndex < pages.length - 1;

  const advancePage = useCallback(() => {
    setPageIndex((i) => Math.min(i + 1, pages.length - 1));
  }, [pages.length]);

  return {
    currentPage,
    hasNext,
    isMultiPage: pages.length > 1,
    pageIndex,
    totalPages: pages.length,
    advancePage,
  };
}
