"use client";

import { useCallback, useEffect, useState } from "react";

/**
 * Fullscreen API wrapper. iOS Safari never implemented this API for
 * arbitrary elements (only <video>), so isSupported is false there and
 * callers should hide the toggle rather than show a button that no-ops.
 */
export function useFullscreen() {
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [isSupported, setIsSupported] = useState(false);

  useEffect(() => {
    setIsSupported(
      typeof document !== "undefined" &&
        (document.fullscreenEnabled ?? false),
    );

    const handleChange = () => setIsFullscreen(document.fullscreenElement != null);
    document.addEventListener("fullscreenchange", handleChange);
    handleChange();
    return () => document.removeEventListener("fullscreenchange", handleChange);
  }, []);

  const toggleFullscreen = useCallback(() => {
    if (document.fullscreenElement) {
      void document.exitFullscreen();
    } else {
      void document.documentElement.requestFullscreen().catch(() => {
        // Blocked (missing user gesture, permissions policy, etc.) — no-op.
      });
    }
  }, []);

  return { isFullscreen, isSupported, toggleFullscreen };
}
