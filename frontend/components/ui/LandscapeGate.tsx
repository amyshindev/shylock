"use client";

import { useEffect, type ReactNode } from "react";

import { useIsMobile, useIsPortrait } from "@/hooks/use-is-mobile";
import { gameFontFamily, gameFontSize } from "@/styles/text-box";
import { theme } from "@/styles/theme";

interface LandscapeGateProps {
  children: ReactNode;
}

/**
 * On phones: prefer landscape. Blocks portrait with a rotate prompt,
 * and locks orientation via Screen Orientation API when the browser allows it.
 */
export function LandscapeGate({ children }: LandscapeGateProps) {
  const isMobile = useIsMobile();
  const isPortrait = useIsPortrait();

  useEffect(() => {
    if (!isMobile) return;

    const orientation = screen.orientation as ScreenOrientation & {
      lock?: (orientation: string) => Promise<void>;
    };

    const tryLock = () => {
      void orientation?.lock?.("landscape").catch(() => {
        // Browsers often reject lock outside fullscreen / user-gesture context.
      });
    };

    tryLock();
    window.addEventListener("orientationchange", tryLock);
    return () => window.removeEventListener("orientationchange", tryLock);
  }, [isMobile]);

  if (isMobile && isPortrait) {
    return (
      <div
        style={{
          minHeight: "100dvh",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          background: theme.background,
          color: theme.textBright,
          padding: 28,
          textAlign: "center",
          fontFamily: gameFontFamily,
          gap: 14,
        }}
      >
        <div style={{ fontSize: 48, lineHeight: 1 }} aria-hidden>
          ⟲
        </div>
        <p
          style={{
            margin: 0,
            fontSize: gameFontSize.lg,
            color: theme.gold,
            letterSpacing: 2,
            fontWeight: 700,
          }}
        >
          가로 화면으로 돌려 주세요
        </p>
        <p
          style={{
            margin: 0,
            fontSize: gameFontSize.md,
            color: theme.textMuted,
            lineHeight: 1.7,
            maxWidth: 280,
          }}
        >
          이 게임은 가로 모드에 맞춰져 있습니다.
          <br />
          기기를 가로로 회전한 뒤 이어서 플레이해 주세요.
        </p>
      </div>
    );
  }

  return <>{children}</>;
}
