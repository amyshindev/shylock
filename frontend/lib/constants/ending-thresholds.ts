/** Mirror of backend `ending_type_map.py` — display hints only; server is authoritative. */
import {
  DP_DIGNITY_ENDING_THRESHOLD,
  DP_FOUGHT_TO_END_THRESHOLD,
  DP_SURVIVAL_ENDING_THRESHOLD,
} from "@/lib/constants/game-balance";

export type EndingType =
  | "rescued_ending"
  | "fought_to_end_ending"
  | "dignity_kept_ending"
  | "survived_ending"
  | "silent_ending";

export interface EndingMeta {
  title: string;
  subtitle: string;
  emoji: string;
}

export function getEnding(dp: number): EndingMeta {
  if (dp >= DP_FOUGHT_TO_END_THRESHOLD) {
    return {
      title: "끝까지 싸운 자",
      subtitle: "법정은 그를 무너뜨리지 못했다",
      emoji: "⚔️",
    };
  }
  if (dp >= DP_DIGNITY_ENDING_THRESHOLD) {
    return {
      title: "존엄을 지킨 자",
      subtitle: "그는 흔들렸지만 꺾이지 않았다",
      emoji: "⚖️",
    };
  }
  if (dp >= DP_SURVIVAL_ENDING_THRESHOLD) {
    return {
      title: "살아남은 자",
      subtitle: "살아남았다. 그것으로 충분한가?",
      emoji: "💔",
    };
  }
  return {
    title: "침묵한 자",
    subtitle: "그는 결국 법정이 원하는 대로 무너졌다",
    emoji: "🕯️",
  };
}

export function endingLabel(type: EndingType): string {
  return getEndingMetaByType(type).title;
}

export function getEndingMetaByType(type: EndingType): EndingMeta {
  switch (type) {
    case "rescued_ending":
      return {
        title: "구원받은 자",
        subtitle: "법정은 그를 꺾지 못했고, 그의 존엄은 온전했다",
        emoji: "✨",
      };
    case "fought_to_end_ending":
      return getEnding(DP_FOUGHT_TO_END_THRESHOLD);
    case "dignity_kept_ending":
      return getEnding(DP_DIGNITY_ENDING_THRESHOLD);
    case "survived_ending":
      return getEnding(DP_SURVIVAL_ENDING_THRESHOLD);
    case "silent_ending":
      return getEnding(0);
    default:
      return { title: "재판 종료", subtitle: "", emoji: "⚖️" };
  }
}

export type GameOverReason = "dp" | "hp";

export function gameOverMeta(reason: GameOverReason): { title: string; subtitle: string } {
  if (reason === "hp") {
    return {
      title: "법정에서 쓰러지다",
      subtitle: "샤일록이 더 이상 버틸 수 없었다. 정신과 몸이 한계에 달했다.",
    };
  }
  return {
    title: "스스로 포기하다",
    subtitle: "샤일록이 스스로 포기했다. 더 이상 싸울 수 없다.",
  };
}
