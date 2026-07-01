/** Normalize LLM dialogue for display. */

const PORTIA_NAME_PATTERNS: [RegExp, string][] = [
  [/발타사르/g, "포샤"],
  [/발타자(?:르|사)?/g, "포샤"],
  [/포르샤/g, "포샤"],
  [/Balthazar/gi, "포샤"],
];

const QUOTE_PAIRS: [string, string][] = [
  ['"', '"'],
  ['"', '"'],
  ["「", "」"],
  ["『", "』"],
];

export function normalizePortiaNames(text: string): string {
  let normalized = text;
  for (const [pattern, replacement] of PORTIA_NAME_PATTERNS) {
    normalized = normalized.replace(pattern, replacement);
  }
  return normalized;
}

export function sanitizeDialogueLine(line: string): string {
  let s = normalizePortiaNames(line.trim());
  if (!s) return s;

  if (s.split('"').length - 1 === 1) {
    if (s.startsWith('"')) s = s.slice(1).trimStart();
    else if (s.endsWith('"')) s = s.slice(0, -1).trimEnd();
  }

  for (const [openQ, closeQ] of QUOTE_PAIRS) {
    const opens = s.split(openQ).length - 1;
    const closes = s.split(closeQ).length - 1;
    if (opens === closes) continue;
    if (closes > opens && s.endsWith(closeQ)) {
      s = s.slice(0, -closeQ.length).trimEnd();
    }
    if (opens > closes && s.startsWith(openQ)) {
      s = s.slice(openQ.length).trimStart();
    }
  }

  return s.trim();
}

export function sanitizeGameText(text: string): string {
  return normalizePortiaNames(text.trim());
}
