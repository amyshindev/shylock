"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { fetchMe } from "@/lib/api-client/auth";
import { listMyTrials } from "@/lib/api-client/trial-progression";
import type { TrialSummaryFromApi, UserFromApi } from "@/lib/api-client/types";
import { useAppShellHeight, useIsMobile } from "@/hooks/use-is-mobile";
import { gameFontFamily, gameFontSize } from "@/styles/text-box";
import { theme } from "@/styles/theme";

export function RecordsScreen() {
  const router = useRouter();
  const isMobile = useIsMobile();
  const appShellHeight = useAppShellHeight();
  const [user, setUser] = useState<UserFromApi | null>(null);
  const [trials, setTrials] = useState<TrialSummaryFromApi[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    void (async () => {
      const me = await fetchMe();
      if (!me) {
        router.replace("/login");
        return;
      }
      setUser(me);
      try {
        setTrials(await listMyTrials());
      } catch (e) {
        setError(e instanceof Error ? e.message : "기록을 불러올 수 없습니다.");
      }
    })();
  }, [router]);

  return (
    <div
      style={{
        minHeight: appShellHeight,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        background: theme.background,
        padding: isMobile ? "32px 16px" : "48px 24px",
        fontFamily: "Georgia, serif",
      }}
    >
      <h1
        style={{
          color: theme.gold,
          fontSize: "clamp(22px, 6vw, 32px)",
          fontWeight: 700,
          letterSpacing: 2,
          margin: "0 0 4px",
          textShadow: "0 0 40px rgba(255, 215, 0, 0.4)",
        }}
      >
        재판 기록
      </h1>
      <p style={{ color: "#7a5a4a", fontSize: gameFontSize.md, fontStyle: "italic", marginBottom: 28 }}>
        {user ? `${user.nickname}의 법정 일지` : "확인 중…"}
      </p>

      {error && (
        <p style={{ color: "#c44", fontSize: gameFontSize.md, fontFamily: gameFontFamily }}>{error}</p>
      )}

      {trials && trials.length === 0 && (
        <p style={{ color: theme.textBright, fontSize: gameFontSize.md, fontFamily: gameFontFamily }}>
          아직 기록된 재판이 없다.
        </p>
      )}

      <div style={{ width: "min(100%, 440px)", display: "flex", flexDirection: "column", gap: 10 }}>
        {trials?.map((t, index) => {
          const inProgress = t.phase === "in_progress";
          return (
            <button
              key={t.trial_id}
              type="button"
              onClick={() => router.push(`/trial/${t.trial_id}`)}
              disabled={!inProgress}
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                gap: 12,
                padding: "14px 18px",
                background: "rgba(18, 12, 24, 0.72)",
                border: "1px solid #3a1028",
                borderRadius: 8,
                color: theme.textBright,
                fontFamily: gameFontFamily,
                fontSize: gameFontSize.md,
                cursor: inProgress ? "pointer" : "default",
                textAlign: "left",
              }}
            >
              <span>
                <span style={{ color: inProgress ? theme.gold : "#5a4a3a", fontWeight: 600 }}>
                  {inProgress ? "진행 중" : "종결"}
                </span>
                <span style={{ color: "#5a4a3a" }}> · {trials.length - index}번째 재판</span>
              </span>
              <span style={{ color: "#7a5a4a", fontSize: gameFontSize.sm }}>
                DP {t.dp} · HP {t.hp}
                {inProgress && <span style={{ color: theme.gold }}> → 이어하기</span>}
              </span>
            </button>
          );
        })}
      </div>

      <button
        type="button"
        onClick={() => router.push("/")}
        style={{
          marginTop: 32,
          background: "none",
          border: "none",
          color: "#7a5a4a",
          fontSize: gameFontSize.sm,
          fontFamily: gameFontFamily,
          cursor: "pointer",
          textDecoration: "underline",
        }}
      >
        타이틀로 돌아가기
      </button>
    </div>
  );
}
