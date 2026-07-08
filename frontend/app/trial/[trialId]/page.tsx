"use client";

import { LandscapeGate } from "@/components/ui/LandscapeGate";
import { BattleScreen } from "@/components/battle/BattleScreen";
import { GameOverScreen } from "@/components/battle/GameOverScreen";
import { EndingScreen } from "@/components/ending/EndingScreen";
import { useTrialProgression } from "@/hooks/use-trial-progression";
import { theme } from "@/styles/theme";
import { useParams, useRouter } from "next/navigation";

export default function TrialPage() {
  const params = useParams();
  const router = useRouter();
  const trialId = params.trialId as string;
  const trial = useTrialProgression(trialId);

  if (!trial.initialized) {
    return (
      <LandscapeGate>
        <div
          style={{
            minHeight: "100dvh",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            background: theme.background,
            color: theme.textMuted,
          }}
        >
          재판 기록을 불러오는 중…
        </div>
      </LandscapeGate>
    );
  }

  if (trial.error && trial.phase === "game" && !trial.portiaReply) {
    return (
      <LandscapeGate>
        <div
          style={{
            minHeight: "100dvh",
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
      </LandscapeGate>
    );
  }

  if (trial.phase === "gameover" && trial.gameOverReason) {
    return (
      <LandscapeGate>
        <GameOverScreen
          reason={trial.gameOverReason}
          onRestart={() => router.push("/")}
        />
      </LandscapeGate>
    );
  }

  if (trial.phase === "ending" && trial.ending) {
    return (
      <LandscapeGate>
        <EndingScreen ending={trial.ending} onRestart={() => router.push("/")} />
      </LandscapeGate>
    );
  }

  return (
    <LandscapeGate>
      <BattleScreen trial={trial} />
    </LandscapeGate>
  );
}
