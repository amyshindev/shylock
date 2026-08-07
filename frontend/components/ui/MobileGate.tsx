"use client";

import { useEffect, useState, type ReactNode } from "react";

import { useIsMobile } from "@/hooks/use-is-mobile";
import { theme } from "@/styles/theme";

interface MobileGateProps {
  children: ReactNode;
}

/**
 * Mobile web isn't supported going forward — a dedicated app is planned
 * instead — so phone-class devices get a static notice rather than the game.
 *
 * Renders null until the client-side mobile check has run once, so mobile
 * visitors don't see a flash of the real game before the notice replaces it
 * (useIsMobile starts false and only resolves in an effect, since it reads
 * matchMedia which isn't available during SSR).
 */
export function MobileGate({ children }: MobileGateProps) {
  const isMobile = useIsMobile();
  const [checked, setChecked] = useState(false);

  useEffect(() => setChecked(true), []);

  if (!checked) return null;

  if (isMobile) {
    return (
      <div
        style={{
          display: "flex",
          minHeight: "100dvh",
          alignItems: "center",
          justifyContent: "center",
          padding: 24,
          textAlign: "center",
          background: theme.background,
          fontFamily: "Georgia, serif",
        }}
      >
        <div>
          <p
            style={{
              color: theme.gold,
              fontSize: 22,
              fontWeight: 700,
              letterSpacing: 1,
              margin: "0 0 12px",
              textShadow: "0 0 40px rgba(255, 215, 0, 0.4)",
            }}
          >
            샤일록의 법정
          </p>
          <p style={{ color: theme.textBright, fontSize: 16, lineHeight: 1.7, margin: 0 }}>
            모바일에서는 아직 플레이하실 수 없어요.
          </p>
        </div>
      </div>
    );
  }

  return <>{children}</>;
}
