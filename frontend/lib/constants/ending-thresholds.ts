/** Mirror of backend `ending_type_map.py` — display hints only; server is authoritative. */
export const VICTORY_DIGNITY_THRESHOLD = 70;
export const STANDARD_DEFEAT_DIGNITY_THRESHOLD = 40;

export type EndingType = "victory" | "standard_defeat" | "silent_defeat";

export function endingLabel(type: EndingType): string {
  switch (type) {
    case "victory":
      return "승리 — 존엄이 지켜졌다";
    case "standard_defeat":
      return "패배 — 법정이 무너졌다";
    case "silent_defeat":
      return "침묵의 패배";
    default:
      return "재판 종료";
  }
}
