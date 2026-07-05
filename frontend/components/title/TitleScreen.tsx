"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

import { PrologueScreen } from "@/components/title/PrologueScreen";
import { TextBox } from "@/components/ui/TextBox";
import { startTrial } from "@/lib/api-client/trial-progression";
import { gameFontSize } from "@/styles/text-box";
import { theme } from "@/styles/theme";

export function TitleScreen() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [prologueTrialId, setPrologueTrialId] = useState<string | null>(null);

  const handleStart = async () => {
    setLoading(true);
    setError(null);
    try {
      const trial = await startTrial();
      setPrologueTrialId(trial.trial_id);
    } catch (e) {
      setError(e instanceof Error ? e.message : "재판을 시작할 수 없습니다");
      setLoading(false);
    }
  };

  if (prologueTrialId) {
    return (
      <PrologueScreen
        onComplete={() => router.push(`/trial/${prologueTrialId}`)}
      />
    );
  }

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
        fontFamily: "Georgia, serif",
      }}
    >
      <p
        style={{
          color: "#6a2a3a",
          letterSpacing: 8,
          fontSize: gameFontSize.sm,
          marginBottom: 14,
          textTransform: "uppercase",
        }}
      >
        The Merchant of Venice
      </p>
      <h1
        style={{
          color: theme.gold,
          fontSize: "clamp(32px, 6vw, 40px)",
          fontWeight: 700,
          margin: "0 0 6px",
          letterSpacing: 3,
          textShadow: "0 0 40px rgba(255, 215, 0, 0.4)",
        }}
      >
        샤일록의 법정
      </h1>
      <p style={{ color: "#7a5a4a", fontSize: gameFontSize.md, fontStyle: "italic", marginBottom: 28 }}>
        당신은 유죄인가, 피해자인가.
      </p>

      <TextBox
        speaker="NARRATOR"
        speakerLabel="NARRATOR"
        style={{ maxWidth: 380, marginBottom: 32 }}
        bodyStyle={{ textAlign: "center", padding: "16px 20px" }}
      >
        <p style={{ color: theme.textBright, fontSize: gameFontSize.md, lineHeight: 2, margin: 0 }}>
          베네치아, 1596년.
          <br />
          당신은 <span style={{ color: theme.gold }}>샤일록</span>이다.
          <br />
          계약은 유효하다. 하지만 이 법정은
          <br />
          처음부터 당신 편이 아니다.
        </p>
      </TextBox>

      <button
        type="button"
        onClick={() => void handleStart()}
        disabled={loading}
        style={{
          padding: "14px 48px",
          fontSize: gameFontSize.base,
          fontWeight: 700,
          letterSpacing: 4,
          textTransform: "uppercase",
          background: theme.red,
          color: theme.gold,
          border: `2px solid rgba(255, 215, 0, 0.4)`,
          cursor: loading ? "wait" : "pointer",
          opacity: loading ? 0.7 : 1,
          boxShadow: "0 0 24px rgba(139, 0, 0, 0.5)",
        }}
      >
        {loading ? "법정으로 들어가는 중…" : "법정에 서다"}
      </button>
      {error && (
        <p style={{ color: "#c44", marginTop: 20, fontSize: gameFontSize.md }}>{error}</p>
      )}
    </div>
  );
}
