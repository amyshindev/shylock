"use client";

import { useEffect, useState } from "react";
import { usePathname } from "next/navigation";

import { useFullscreen } from "@/hooks/use-fullscreen";
import { useTitleActive } from "@/hooks/use-title-active";
import { gameFontFamily, gameFontSize } from "@/styles/text-box";

const ICON_COLOR = "#f0d8c8"; // same light parchment tone used elsewhere (SkillPanel, LoreChatWidget)
// Matches the fullscreenHintFade keyframes' own total duration (globals.css) —
// the timeout just unmounts the hint once that animation has finished.
const HINT_DURATION_MS = 2600;

/**
 * Global fullscreen toggle, rendered once in the root layout so it's
 * available on every screen (title, battle, ending, records). Sits at
 * bottom-right (bottom:16, right:16) — the mirror image of LoreChatWidget's
 * launcher button at bottom-left (bottom:16, left:16).
 *
 * Enter-only: once in fullscreen there's no on-screen button to leave it
 * (browsers already bind Esc to exit fullscreen; a top-center toast reminds
 * the player of that on the way in, then fades itself out — no UI clutter
 * needed for the whole time they're fullscreen).
 *
 * On the title splash itself the enter button is always visible (dim,
 * brightens on hover). Everywhere else — including the black prologue
 * screen, which is still the "/" route so pathname alone can't tell it
 * apart from the title, hence useTitleActive() — it's hidden by default and
 * only rises up (fade + slide) when the mouse comes near the corner, so it
 * doesn't compete for attention during the game itself.
 *
 * iOS Safari has no Fullscreen API for arbitrary elements (only <video>),
 * so isSupported is false there and nothing here renders at all rather than
 * showing something that would silently no-op.
 */
export function FullscreenButton() {
  const { isFullscreen, isSupported, toggleFullscreen } = useFullscreen();
  const pathname = usePathname();
  const { titleActive } = useTitleActive();
  const [active, setActive] = useState(false);
  const [showHint, setShowHint] = useState(false);

  useEffect(() => {
    if (!isFullscreen) {
      // Without this, exiting before the timer below fires leaves showHint
      // stuck at true — re-entering fullscreen later sets it to true again,
      // which React treats as a no-op update, so <FullscreenHint> never
      // remounts and its CSS animation never replays. Explicitly resetting
      // here guarantees a real false->true transition (and a fresh DOM
      // node) on every single entry.
      setShowHint(false);
      return;
    }
    setShowHint(true);
    const timer = setTimeout(() => setShowHint(false), HINT_DURATION_MS);
    return () => clearTimeout(timer);
  }, [isFullscreen]);

  if (!isSupported) return null;

  const alwaysVisible = pathname === "/" && titleActive;
  const revealed = alwaysVisible || active;

  return (
    <>
      {showHint && <FullscreenHint />}

      {!isFullscreen && (
        <div
          // Centered around bottom:16, right:16 — the mirror image of
          // LoreChatWidget's bottom:16, left:16 — so the hover-catch area
          // grows in every direction without shifting where the icon itself
          // actually sits.
          style={{
            position: "fixed",
            bottom: 16 - 86,
            right: 16 - 86,
            zIndex: 38,
            width: 44 + 172,
            height: 44 + 172,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
          onMouseEnter={() => setActive(true)}
          onMouseLeave={() => setActive(false)}
        >
          <button
            type="button"
            aria-label="전체화면으로 보기"
            title="전체화면으로 보기"
            onClick={toggleFullscreen}
            onFocus={() => setActive(true)}
            onBlur={() => setActive(false)}
            style={{
              width: 44,
              height: 44,
              padding: 0,
              border: "none",
              background: "transparent",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              cursor: "pointer",
              opacity: alwaysVisible ? (active ? 1 : 0.85) : revealed ? 1 : 0,
              transform: alwaysVisible ? "none" : `translateY(${revealed ? 0 : 16}px)`,
              transition: "opacity 0.2s ease, transform 0.2s ease",
              pointerEvents: alwaysVisible || revealed ? "auto" : "none",
            }}
          >
            <MaximizeIcon />
          </button>
        </div>
      )}
    </>
  );
}

function FullscreenHint() {
  return (
    <div
      style={{
        position: "fixed",
        top: 20,
        left: "50%",
        zIndex: 60,
        background: "rgba(20, 10, 18, 0.94)",
        color: ICON_COLOR,
        border: "1px solid #a07840",
        borderRadius: 6,
        padding: "12px 24px",
        fontFamily: gameFontFamily,
        fontSize: gameFontSize.lg,
        boxShadow: "0 4px 20px rgba(0, 0, 0, 0.5), 0 0 24px 4px rgba(255, 195, 100, 0.35)",
        pointerEvents: "none",
        animation: "fullscreenHintFade 2.6s ease-out forwards",
      }}
    >
      전체화면을 종료하려면 Esc를 누르세요
    </div>
  );
}

function MaximizeIcon() {
  return (
    <svg width="30" height="30" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path
        d="M8 3H5a2 2 0 0 0-2 2v3m18 0V5a2 2 0 0 0-2-2h-3m0 18h3a2 2 0 0 0 2-2v-3M3 16v3a2 2 0 0 0 2 2h3"
        stroke={ICON_COLOR}
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}
