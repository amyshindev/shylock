"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { AuthScreen } from "@/components/auth/AuthScreen";
import { PrologueScreen } from "@/components/title/PrologueScreen";
import { useAppShellHeight } from "@/hooks/use-is-mobile";
import { useTitleActive } from "@/hooks/use-title-active";
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
// button-start-plaque.png: cropped from Gemini_Generated_Image_1nvtti1nvtti1nvt.png
// (green screen + drop shadow chroma-keyed out, same despill treatment as
// login-button.png — see that asset's history). 900x394 (ratio ~2.28),
// transparent background, ragged ornate edge — not a hard rectangle like the
// old button-start-frame.png/button-loading-frame.png (1927x608, ratio
// ~3.17) it replaces. The rect below is sized to that ratio (same on-screen
// area as the original rect, recentered on its center) so
// backgroundSize:100% 100% doesn't stretch it; button-loading-frame.png
// still uses its own old ratio, so it renders via backgroundSize:"contain"
// instead — see the loading-frame layer below.
const START_BUTTON_RECT = { left: "40.69%", top: "70.5%", width: "18.62%", height: "14.61%" };

export function TitleScreen() {
  const router = useRouter();
  const appShellHeight = useAppShellHeight();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [prologueTrialId, setPrologueTrialId] = useState<string | null>(null);
  const [user, setUser] = useState<UserFromApi | null>(null);
  const [startHovered, setStartHovered] = useState(false);
  const [loginHovered, setLoginHovered] = useState(false);
  const [showLoginModal, setShowLoginModal] = useState(false);
  const { setTitleActive } = useTitleActive();

  useEffect(() => {
    void fetchMe().then(setUser);
  }, []);

  // FullscreenButton (rendered as a layout sibling, not a descendant) needs
  // to know when the black prologue screen replaces the title splash —
  // that's a local state switch, not a route change, so pathname alone
  // can't tell the two apart.
  useEffect(() => {
    setTitleActive(prologueTrialId === null);
  }, [prologueTrialId, setTitleActive]);

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
          // Fixed (not absolute) so this sits at the true screen corner
          // instead of the top of the title *image*'s own box — on screens
          // narrower than the art's own ratio (most laptops: ~1.5–1.6 vs the
          // art's 1.79), that box is letterboxed and starts well below the
          // real top edge, which was leaving a bigger gap above this row
          // than intended.
          style={{
            position: "fixed",
            top: 16,
            right: 32,
            zIndex: 5,
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
            // Icon-only like FullscreenButton — no plaque/border, just the
            // word itself. Gold gradient + emboss shadow (referencing
            // Gemini_Generated_Image_69uxvb69uxvb69ux.png's engraved-gold
            // lettering) instead of a flat color, so it doesn't read as
            // plain/flat next to the painted title art around it.
            <button
              type="button"
              aria-label="로그인"
              onClick={() => setShowLoginModal(true)}
              onMouseEnter={() => setLoginHovered(true)}
              onMouseLeave={() => setLoginHovered(false)}
              style={{
                background: "transparent",
                border: "none",
                padding: "4px 2px",
                cursor: "pointer",
                fontFamily: '"Times New Roman", Times, serif',
                fontSize: "clamp(14px, 1.6vw, 24px)",
                fontWeight: 500,
                letterSpacing: 2,
                lineHeight: 1,
                backgroundImage:
                  // Same brick-red family as "THE MERCHANT OF VENICE" baked
                  // into title-screen.png (#6a2a3a, sampled from the art).
                  "linear-gradient(180deg, #a8606e 0%, #833c48 32%, #6a2a3a 62%, #3a121c 100%)",
                WebkitBackgroundClip: "text",
                backgroundClip: "text",
                color: "transparent",
                WebkitTextFillColor: "transparent",
                textShadow: loginHovered
                  ? "0 1px 0 rgba(255, 255, 255, 0.55), 0 2px 4px rgba(0, 0, 0, 0.6), 0 0 14px rgba(255, 210, 120, 0.55)"
                  : "0 1px 0 rgba(255, 255, 255, 0.35), 0 2px 3px rgba(0, 0, 0, 0.55)",
                filter: loginHovered ? "brightness(1.15)" : "brightness(1)",
                transition: "filter 0.15s ease, text-shadow 0.15s ease",
              }}
            >
              LOGIN
            </button>
          )}
        </div>

        {showLoginModal && <AuthScreen onClose={() => setShowLoginModal(false)} />}

        <div style={{ position: "absolute", ...START_BUTTON_RECT }}>
          <div
            aria-hidden
            style={{
              position: "absolute",
              inset: 0,
              backgroundImage: `url(${
                loading ? "/assets/button-loading-frame.png" : "/assets/button-start-plaque.png"
              })`,
              // button-start-plaque.png matches this box's ratio exactly, so
              // it fills edge-to-edge; button-loading-frame.png is still the
              // old wider ratio, so it's letterboxed via "contain" instead
              // of stretched.
              backgroundSize: loading ? "contain" : "100% 100%",
              backgroundRepeat: "no-repeat",
              backgroundPosition: "center",
              borderRadius: 6,
              pointerEvents: "none",
              // drop-shadow, not box-shadow: it follows the plaque art's own
              // alpha silhouette (ragged ornate edge) instead of glowing
              // around its rectangular bounding box. The animation below
              // takes over entirely on hover, so this resting-state filter
              // only matters for the transition *into* that state.
              filter:
                !loading && startHovered
                  ? "brightness(1.18) saturate(1.25) drop-shadow(0 0 10px rgba(255, 195, 60, 0.65)) drop-shadow(0 0 22px rgba(255, 150, 30, 0.4))"
                  : "brightness(1) saturate(1) drop-shadow(0 0 0 rgba(255, 195, 60, 0))",
              animation: !loading && startHovered ? "startButtonGlow 1.6s ease-in-out infinite" : "none",
              transition: "filter 0.2s ease",
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
