"use client";

import { useEffect, useState } from "react";

/** Matches common phone / narrow tablet portrait widths. */
export const MOBILE_BREAKPOINT_PX = 768;

export function useIsMobile(breakpointPx = MOBILE_BREAKPOINT_PX): boolean {
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    const media = window.matchMedia(`(max-width: ${breakpointPx}px)`);
    const sync = () => setIsMobile(media.matches);
    sync();
    media.addEventListener("change", sync);
    return () => media.removeEventListener("change", sync);
  }, [breakpointPx]);

  return isMobile;
}
