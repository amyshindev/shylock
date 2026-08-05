"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { PrologueScreen } from "@/components/title/PrologueScreen";
import { useAppShellHeight } from "@/hooks/use-is-mobile";
import { fetchMe, logout } from "@/lib/api-client/auth";
import { startTrial } from "@/lib/api-client/trial-progression";
import type { UserFromApi } from "@/lib/api-client/types";
import { gameFontFamily, gameFontSize } from "@/styles/text-box";
import { theme } from "@/styles/theme";

// The title image bakes in the title/subtitle/tagline/body text (MobileGate
// excludes mobile before this renders, so this is desktop-only image-map UI),
// but — unlike the previous version — has no button or login art drawn into
// it, so those are real UI elements positioned in the empty space below the
// text. Measured directly off the source PNG (2752x1536), not eyeballed.
const TITLE_IMAGE_RATIO = "(2752 / 1536)";
// The start/loading button images (both 1927x608, ratio ~3.17) have their
// "법정에 서기" / "법정으로 들어가는 중..." labels baked in, cropped tight to the
// frame's hard edge to drop the soft outer glow that blended with the
// checker canvas. No live text on top.
const START_BUTTON_RECT = { left: "40%", top: "70.06%", width: "20%", height: "11.31%" };

export function TitleScreen() {
  const router = useRouter();
  const appShellHeight = useAppShellHeight();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [prologueTrialId, setPrologueTrialId] = useState<string | null>(null);
  const [user, setUser] = useState<UserFromApi | null>(null);
  const [startHovered, setStartHovered] = useState(false);

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
        alignItems: "center",
        justifyContent: "center",
        background: theme.background,
      }}
    >
      <div
        style={{
          position: "relative",
          width: `min(100vw, calc(${appShellHeight} * ${TITLE_IMAGE_RATIO}))`,
          height: `min(${appShellHeight}, calc(100vw / ${TITLE_IMAGE_RATIO}))`,
          backgroundImage: "url(/assets/title-screen.png)",
          backgroundSize: "100% 100%",
          backgroundRepeat: "no-repeat",
          fontFamily: "Georgia, serif",
        }}
      >
        <div
          style={{
            position: "absolute",
            top: "3.6%",
            right: "1.9%",
            display: "flex",
            alignItems: "center",
            gap: 12,
            whiteSpace: "nowrap",
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

        <div style={{ position: "absolute", ...START_BUTTON_RECT }}>
          <div
            aria-hidden
            style={{
              position: "absolute",
              inset: 0,
              backgroundImage: `url(${
                loading ? "/assets/button-loading-frame.png" : "/assets/button-start-frame.png"
              })`,
              backgroundSize: "100% 100%",
              backgroundRepeat: "no-repeat",
              borderRadius: 6,
              pointerEvents: "none",
              filter:
                !loading && startHovered
                  ? "brightness(1.18) saturate(1.25)"
                  : "brightness(1) saturate(1)",
              boxShadow:
                !loading && startHovered
                  ? "0 0 18px 4px rgba(255, 195, 60, 0.55), 0 0 42px 14px rgba(255, 150, 30, 0.35)"
                  : "0 0 0 0 rgba(255, 195, 60, 0)",
              animation: !loading && startHovered ? "startButtonGlow 1.6s ease-in-out infinite" : "none",
              transition: "filter 0.2s ease, box-shadow 0.2s ease",
            }}
          />
          <button
            type="button"
            onClick={() => void handleStart()}
            disabled={loading}
            style={{
              position: "absolute",
              inset: 0,
              background: "transparent",
              border: "none",
              borderRadius: 6,
              padding: 0,
              cursor: loading ? "wait" : "pointer",
            }}
            onMouseEnter={() => setStartHovered(true)}
            onMouseLeave={() => setStartHovered(false)}
          />
        </div>

        {error && (
          <div
            style={{
              position: "absolute",
              left: "50%",
              top: "78.5%",
              transform: "translateX(-50%)",
              maxWidth: "70%",
              background: "rgba(8, 3, 10, 0.85)",
              color: "#e88",
              padding: "6px 16px",
              borderRadius: 4,
              fontFamily: gameFontFamily,
              fontSize: "clamp(11px, 1.2vw, 15px)",
              textAlign: "center",
            }}
          >
            {error}
          </div>
        )}
      </div>
    </div>
  );
}
