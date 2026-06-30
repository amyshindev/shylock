/**
 * Normalize Portia LLM output — strip JSON wrappers when parsing fails upstream.
 */
export function extractPortiaText(raw: string): string {
  const trimmed = raw.trim();
  if (!trimmed) return "";

  if (trimmed.startsWith("{")) {
    try {
      const data = JSON.parse(trimmed) as { text?: unknown };
      if (typeof data.text === "string") return data.text.trim();
    } catch {
      const match = trimmed.match(/"text"\s*:\s*"((?:[^"\\]|\\.)*)(?:"|$)/);
      if (match?.[1]) {
        try {
          return JSON.parse(`"${match[1]}"`) as string;
        } catch {
          return match[1].replace(/\\n/g, "\n").replace(/\\"/g, '"').trim();
        }
      }
    }
  }

  return trimmed;
}

/** Split prose into one sentence per click-to-continue step. */
export function splitIntoSentences(text: string): string[] {
  const normalized = extractPortiaText(text).replace(/\n+/g, " ").trim();
  if (!normalized) return [];

  const matches = normalized.match(
    /[^.!?…]+[.!?…]+(?:\s*["'"」』)]*)?|[^.!?…]+$/g,
  );
  if (!matches) return [normalized];

  const sentences = matches.map((s) => s.trim()).filter(Boolean);
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
