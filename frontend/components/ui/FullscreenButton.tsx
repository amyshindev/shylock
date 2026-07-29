"use client";

import { useFullscreen } from "@/hooks/use-fullscreen";

/**
 * Global fullscreen toggle, rendered once in the root layout so it's
 * available on every screen (title, battle, ending, records). Sits at
 * bottom-left — LoreChatWidget already owns bottom-right within battle.
 *
 * iOS Safari has no Fullscreen API for arbitrary elements (only <video>),
 * so isSupported is false there and the button doesn't render at all
 * rather than showing something that would silently no-op.
 */
export function FullscreenButton() {
  const { isFullscreen, isSupported, toggleFullscreen } = useFullscreen();

  if (!isSupported) return null;

  return (
    <button
      type="button"
      aria-label={isFullscreen ? "전체화면 끄기" : "전체화면으로 보기"}
      title={isFullscreen ? "전체화면 끄기" : "전체화면으로 보기"}
      onClick={toggleFullscreen}
      style={{
        position: "fixed",
        bottom: 16,
        left: 16,
        zIndex: 38,
        width: 40,
        height: 40,
        borderRadius: "50%",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        fontSize: 18,
        background: "rgba(20, 10, 18, 0.95)",
        color: "#f0d8c8",
        border: "1px solid #5a3848",
        boxShadow: "0 2px 8px rgba(0, 0, 0, 0.45)",
        cursor: "pointer",
      }}
    >
      {isFullscreen ? "🗗" : "⛶"}
    </button>
  );
}
