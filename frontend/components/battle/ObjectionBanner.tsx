"use client";

import { theme } from "@/styles/theme";

export function ObjectionBanner() {
  return (
    <div
      style={{
        position: "fixed",
        inset: 0,
        zIndex: 50,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        background: "rgba(0,0,0,0.55)",
        pointerEvents: "none",
      }}
    >
      <div
        className="objection-banner"
        style={{
          padding: "24px 48px",
          background: theme.red,
          border: `3px solid ${theme.gold}`,
          color: theme.gold,
          fontSize: 32,
          fontWeight: 900,
          letterSpacing: 4,
          animation: "objectionPop 0.3s ease-out",
        }}
      >
        이의 있습니다!
      </div>
    </div>
  );
}
