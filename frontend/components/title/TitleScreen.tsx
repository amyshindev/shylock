"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { PrologueScreen } from "@/components/title/PrologueScreen";
import { TextBox } from "@/components/ui/TextBox";
import { useAppShellHeight, useIsMobile } from "@/hooks/use-is-mobile";
import { fetchMe, logout } from "@/lib/api-client/auth";
import { startTrial } from "@/lib/api-client/trial-progression";
import type { UserFromApi } from "@/lib/api-client/types";
import { gameFontFamily, gameFontSize } from "@/styles/text-box";
import { theme } from "@/styles/theme";

export function TitleScreen() {
  const router = useRouter();
  const isMobile = useIsMobile();
  const appShellHeight = useAppShellHeight();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [prologueTrialId, setPrologueTrialId] = useState<string | null>(null);
  const [user, setUser] = useState<UserFromApi | null>(null);

  useEffect(() => {
    void fetchMe().then(setUser);
  }, []);

  const handleLogout = async () => {
    await logout();
    setUser(null);
  };

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
        minHeight: appShellHeight,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        background: theme.background,
        padding: isMobile
          ? "max(16px, env(safe-area-inset-top)) 16px max(16px, env(safe-area-inset-bottom))"
          : 24,
        textAlign: "center",
        fontFamily: "Georgia, serif",
        position: "relative",
      }}
    >
      <div
        style={{
          position: "absolute",
          top: isMobile ? "max(12px, env(safe-area-inset-top))" : 16,
          right: isMobile ? 12 : 20,
          display: "flex",
          alignItems: "center",
          gap: 12,
          fontFamily: gameFontFamily,
          fontSize: gameFontSize.sm,
        }}
      >
        {user ? (
          <>
            <span style={{ color: theme.textBright }}>
              <span style={{ color: theme.gold }}>{user.nickname}</span> 님
            </span>
            <button
              type="button"
              onClick={() => router.push("/records")}
              style={{
                background: "none",
                border: "none",
                color: "#7a5a4a",
                fontSize: gameFontSize.sm,
                fontFamily: gameFontFamily,
                cursor: "pointer",
                textDecoration: "underline",
              }}
            >
              재판 기록
            </button>
            <button
              type="button"
              onClick={() => void handleLogout()}
              style={{
                background: "none",
                border: "none",
                color: "#7a5a4a",
                fontSize: gameFontSize.sm,
                fontFamily: gameFontFamily,
                cursor: "pointer",
                textDecoration: "underline",
              }}
            >
              로그아웃
            </button>
          </>
        ) : (
          <button
            type="button"
            onClick={() => router.push("/login")}
            style={{
              background: "none",
              border: "1px solid #3a1828",
              borderRadius: 4,
              padding: "6px 14px",
              color: "#c0a060",
              fontSize: gameFontSize.sm,
              fontFamily: gameFontFamily,
              cursor: "pointer",
            }}
          >
            로그인
          </button>
        )}
      </div>
      <p
        style={{
          color: "#6a2a3a",
          letterSpacing: isMobile ? 4 : 8,
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
          fontSize: "clamp(28px, 8vw, 40px)",
          fontWeight: 700,
          margin: "0 0 6px",
          letterSpacing: isMobile ? 1 : 3,
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
        style={{ maxWidth: 380, width: "100%", marginBottom: 32 }}
        bodyStyle={{ textAlign: "center", padding: isMobile ? "14px 16px" : "16px 20px" }}
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
          padding: isMobile ? "14px 28px" : "14px 48px",
          width: isMobile ? "100%" : undefined,
          maxWidth: isMobile ? 320 : undefined,
          fontSize: gameFontSize.base,
          fontWeight: 700,
          letterSpacing: isMobile ? 2 : 4,
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
