/** Mirror of backend `ending_type_map.py` — display hints only; server is authoritative. */
import { DP_GOOD_ENDING_THRESHOLD } from "@/lib/constants/game-balance";

export type EndingType =
  | "dignity_ending"
  | "bad_ending"
  | "history_changed_ending"
  | "survival_ending";

export interface EndingMeta {
  title: string;
  subtitle: string;
  emoji: string;
}

export function getEnding(dp: number, alienLawExecuted: boolean): EndingMeta {
  const good = dp >= DP_GOOD_ENDING_THRESHOLD;
  if (alienLawExecuted) {
    return good
      ? {
          title: "존엄 엔딩",
          subtitle: "법은 그를 꺾었지만, 아무도 그를 굴복시키지 못했다",
          emoji: "⚖️",
        }
      : {
          title: "배드 엔딩",
          subtitle: "침묵이 그를 삼켰다",
          emoji: "🕯️",
        };
  }
  return good
    ? {
        title: "역사를 바꾼 엔딩",
        subtitle: "베네치아의 법정에서, 역사가 다른 길을 택했다",
        emoji: "✨",
      }
    : {
        title: "그냥 살아남는 엔딩",
        subtitle: "살아남았다. 그것뿐이다",
        emoji: "💔",
      };
}

export function endingLabel(type: EndingType): string {
  return getEndingMetaByType(type).title;
}

export function getEndingMetaByType(type: EndingType): EndingMeta {
  switch (type) {
    case "dignity_ending":
      return getEnding(DP_GOOD_ENDING_THRESHOLD, true);
    case "bad_ending":
      return getEnding(0, true);
    case "history_changed_ending":
      return getEnding(DP_GOOD_ENDING_THRESHOLD, false);
    case "survival_ending":
      return getEnding(0, false);
    default:
      return { title: "재판 종료", subtitle: "", emoji: "⚖️" };
  }
}

export type GameOverReason = "shylock_hp" | "dp";

export function gameOverMeta(reason: GameOverReason): { title: string; subtitle: string } {
  if (reason === "shylock_hp") {
    return {
      title: "법정에서 쓰러지다",
      subtitle: "포샤가 법적으로 쓰러뜨렸다. 재판은 끝났다.",
    };
  }
  return {
    title: "스스로 포기하다",
    subtitle: "샤일록이 스스로 포기했다. 더 이상 싸울 수 없다.",
  };
}
