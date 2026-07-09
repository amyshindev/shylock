"use client";

import type { ReactNode } from "react";

interface ForceLandscapeProps {
  children: ReactNode;
}

/**
 * On portrait phones, CSS rotates the shell 90° so the game renders landscape
 * while the device is held upright.
 */
export function ForceLandscape({ children }: ForceLandscapeProps) {
  return (
    <div className="force-landscape-frame">
      <div className="force-landscape-shell">{children}</div>
    </div>
  );
}
