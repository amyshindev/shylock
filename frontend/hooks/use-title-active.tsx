"use client";

import { createContext, useContext, useMemo, useState, type ReactNode } from "react";

/**
 * Whether the title splash (not the prologue that follows it, still on the
 * same "/" route) is the thing currently on screen. Lives in root layout so
 * FullscreenButton — a sibling of the routed page, not a descendant of
 * TitleScreen — can tell "always show" (title) apart from "hover to
 * reveal" (everywhere else, including the prologue's black screen).
 *
 * Defaults to true: the provider is freshly mounted per real page load, and
 * FullscreenButton additionally gates this on pathname === "/", so a stale
 * `true` left over on other routes never matters.
 */
const TitleActiveContext = createContext<{
  titleActive: boolean;
  setTitleActive: (active: boolean) => void;
}>({ titleActive: true, setTitleActive: () => {} });

export function TitleActiveProvider({ children }: { children: ReactNode }) {
  const [titleActive, setTitleActive] = useState(true);
  const value = useMemo(() => ({ titleActive, setTitleActive }), [titleActive]);
  return <TitleActiveContext.Provider value={value}>{children}</TitleActiveContext.Provider>;
}

export function useTitleActive() {
  return useContext(TitleActiveContext);
}
