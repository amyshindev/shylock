"use client";

import { useParams, useRouter } from "next/navigation";

import { BattleScreen } from "@/components/battle/BattleScreen";
import { GameOverScreen } from "@/components/battle/GameOverScreen";
import { EndingScreen } from "@/components/ending/EndingScreen";
import { useTrialProgression } from "@/hooks/use-trial-progression";
import { theme } from "@/styles/theme";

export default function TrialPage() {
  const params = useParams();
  const router = useRouter();
  const trialId = params.trialId as string;
  const trial = useTrialProgression(trialId);

  if (!trial.initialized) {
    return (
      <div
        style={{
          minHeight: "100vh",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          background: theme.background,
          color: theme.textMuted,
        }}
      >
        재판 기록을 불러오는 중…
      </div>
    );
  }

  if (trial.error && trial.phase === "game" && !trial.portiaReply) {
    return (
      <div
        style={{
          minHeight: "100vh",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          background: theme.background,
          padding: 24,
          textAlign: "center",
        }}
      >
        <p style={{ color: "#c44" }}>{trial.error}</p>
        <button
          type="button"
          onClick={() => router.push("/")}
          style={{
            marginTop: 16,
            padding: "10px 24px",
            border: `1px solid ${theme.gold}`,
            background: "transparent",
            color: theme.gold,
            cursor: "pointer",
          }}
        >
          타이틀로
        </button>
      </div>
    );
  }

  if (trial.phase === "gameover" && trial.gameOverReason) {
    return (
      <GameOverScreen
        reason={trial.gameOverReason}
        onRestart={() => router.push("/")}
      />
    );
  }

  if (trial.phase === "ending" && trial.ending) {
    return (
      <EndingScreen ending={trial.ending} onRestart={() => router.push("/")} />
    );
  }

  return <BattleScreen trial={trial} />;
}
