"use client";

import { useEffect, useState } from "react";

/**
 * Phone / touch devices, including landscape.
 * Portrait phones: max-width ≤ 900.
 * Landscape phones: short side is height (≤ 520) while width can exceed 768.
 */
export function useIsMobile(): boolean {
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    const sync = () => {
      const coarse =
        window.matchMedia("(hover: none) and (pointer: coarse)").matches;
      const narrow = window.matchMedia("(max-width: 900px)").matches;
      const shortLandscape = window.matchMedia(
        "(orientation: landscape) and (max-height: 520px)",
      ).matches;
      setIsMobile(coarse || narrow || shortLandscape);
    };
    sync();
    window.addEventListener("resize", sync);
    window.addEventListener("orientationchange", sync);
    return () => {
      window.removeEventListener("resize", sync);
      window.removeEventListener("orientationchange", sync);
    };
  }, []);

  return isMobile;
}

/** True when the viewport is taller than it is wide. */
export function useIsPortrait(): boolean {
  const [isPortrait, setIsPortrait] = useState(false);

  useEffect(() => {
    const sync = () => {
      setIsPortrait(window.innerHeight > window.innerWidth);
    };
    sync();
    window.addEventListener("resize", sync);
    window.addEventListener("orientationchange", sync);
    return () => {
      window.removeEventListener("resize", sync);
      window.removeEventListener("orientationchange", sync);
    };
  }, []);

  return isPortrait;
}

/** Portrait phone: rotate UI to landscape instead of blocking with a prompt. */
export function useForceLandscape(): boolean {
  const isMobile = useIsMobile();
  const isPortrait = useIsPortrait();
  return isMobile && isPortrait;
}

/** Full-screen shell height; uses % when the viewport is CSS-rotated. */
export function useAppShellHeight(): string {
  const isMobile = useIsMobile();
  const forceLandscape = useForceLandscape();
  if (forceLandscape) return "100%";
  if (isMobile) return "100dvh";
  return "100vh";
}
