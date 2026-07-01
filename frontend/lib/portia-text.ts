/**
 * Normalize Portia LLM output — strip JSON wrappers when parsing fails upstream.
 */
import { sanitizeDialogueLine, sanitizeGameText } from "@/lib/game-text";

export function extractPortiaText(raw: string): string {
  let trimmed = raw.trim();
  if (!trimmed) return "";

  const fence = trimmed.match(/^```(?:json)?\s*\n?([\s\S]*?)\n?```\s*$/i);
  if (fence?.[1]) trimmed = fence[1].trim();

  if (trimmed.startsWith("{")) {
    try {
      const data = JSON.parse(trimmed) as { text?: unknown };
      if (typeof data.text === "string") return sanitizeGameText(data.text);
    } catch {
      const match = trimmed.match(/"text"\s*:\s*"((?:[^"\\]|\\.)*)(?:"|$)/);
      if (match?.[1]) {
        try {
          return sanitizeGameText(JSON.parse(`"${match[1]}"`) as string);
        } catch {
          return sanitizeGameText(
            match[1].replace(/\\n/g, "\n").replace(/\\"/g, '"'),
          );
        }
      }
    }
  }

  return sanitizeGameText(trimmed);
}

/** Split prose into one sentence per click-to-continue step. */
export function splitIntoSentences(text: string): string[] {
  const normalized = extractPortiaText(text).replace(/\n+/g, " ").trim();
  if (!normalized) return [];

  const matches = normalized.match(
    /[^.!?…]+[.!?…]+(?:\s*["'"」』)]*)?|[^.!?…]+$/g,
  );
  if (!matches) return [normalized];

  const sentences = matches
    .map((s) => sanitizeDialogueLine(s))
    .filter(Boolean);
  return sentences.length > 0 ? sentences : [normalized];
}

/** @deprecated Prefer splitIntoSentences for Portia replies. */
export function splitIntoDialoguePages(text: string, maxChars = 110): string[] {
  const normalized = extractPortiaText(text);
  if (normalized.length <= maxChars) return [normalized];

  const pages: string[] = [];
  let rest = normalized;

  while (rest.length > maxChars) {
    let cut = maxChars;
    const slice = rest.slice(0, maxChars);
    const breakAt = Math.max(
      slice.lastIndexOf(". "),
      slice.lastIndexOf("? "),
      slice.lastIndexOf("! "),
      slice.lastIndexOf("… "),
      slice.lastIndexOf("다. "),
      slice.lastIndexOf("요. "),
      slice.lastIndexOf(" "),
    );
    if (breakAt > maxChars * 0.45) cut = breakAt + 1;

    pages.push(rest.slice(0, cut).trim());
    rest = rest.slice(cut).trim();
  }

  if (rest) pages.push(rest);
  return pages.length > 0 ? pages : [normalized];
}
