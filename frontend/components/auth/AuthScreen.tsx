"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { loginWithGoogle } from "@/lib/api-client/auth";
import { useAppShellHeight, useIsMobile } from "@/hooks/use-is-mobile";
import { gameFontFamily, gameFontSize, textBoxPanelStyle } from "@/styles/text-box";
import { theme } from "@/styles/theme";

interface AuthScreenProps {
  /**
   * When provided, renders as a fixed-position modal overlay on top of
   * whatever's already on screen, instead of the full-page layout — used by
   * TitleScreen so clicking "로그인" doesn't navigate away. Calling it
   * dismisses the modal without navigating.
   */
  onClose?: () => void;
}

function GoogleIcon() {
  return (
    <span
      style={{
        display: "inline-flex",
        alignItems: "center",
        justifyContent: "center",
        width: 22,
        height: 22,
        borderRadius: "50%",
        background: "#ffffff",
        flexShrink: 0,
      }}
    >
      <svg width="14" height="14" viewBox="0 0 48 48" aria-hidden="true">
        <path
          fill="#EA4335"
          d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"
        />
        <path
          fill="#4285F4"
          d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"
        />
        <path
          fill="#FBBC05"
          d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"
        />
        <path
          fill="#34A853"
          d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"
        />
      </svg>
    </span>
  );
}

export function AuthScreen({ onClose }: AuthScreenProps = {}) {
  const router = useRouter();
  const isMobile = useIsMobile();
  const appShellHeight = useAppShellHeight();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Google callback redirects back with ?error=google on failure.
    const params = new URLSearchParams(window.location.search);
    if (params.get("error") === "google") {
      setError("구글 로그인에 실패했습니다. 잠시 후 다시 시도해 주세요.");
    }
  }, []);

  const handleGoogleLogin = async () => {
    setLoading(true);
    setError(null);
    try {
      await loginWithGoogle();
    } catch (err) {
      setError(err instanceof Error ? err.message : "요청을 처리할 수 없습니다.");
      setLoading(false);
    }
  };

  const googleButton = (
    <button
      type="button"
      disabled={loading}
      onClick={() => void handleGoogleLogin()}
      style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        gap: 10,
        width: "100%",
        padding: "13px 28px",
        fontFamily: gameFontFamily,
        fontSize: gameFontSize.md,
        fontWeight: 600,
        background: "#100510",
        color: "#e0c090",
        border: "1px solid #3a1828",
        borderRadius: 4,
        cursor: loading ? "wait" : "pointer",
        opacity: loading ? 0.7 : 1,
        transition: "all 0.15s",
      }}
      onMouseEnter={(e) => {
        if (!loading) {
          e.currentTarget.style.background = "#1a0820";
          e.currentTarget.style.borderColor = "rgba(255, 215, 0, 0.31)";
        }
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.background = "#100510";
        e.currentTarget.style.borderColor = "#3a1828";
      }}
    >
      <GoogleIcon />
      {loading ? "이동하는 중…" : "Google로 시작하기"}
    </button>
  );

  const errorMessage = error && (
    <p
      style={{
        color: "#c44",
        fontSize: gameFontSize.sm,
        margin: "0 0 14px",
        textAlign: "center",
        fontFamily: gameFontFamily,
      }}
    >
      {error}
    </p>
  );

  if (onClose) {
    // Deliberately NOT a portal to document.body: ForceLandscape wraps
    // {children} in a container it CSS-rotates on narrow/portrait viewports
    // (see globals.css .force-landscape-frame), which also makes that
    // container the containing block for any `position: fixed` descendant.
    // A portal to document.body escapes that container, so it never got the
    // same rotation/sizing. Rendering inline here keeps it inside the same
    // rotated frame as everything else.
    //
    // Same panel chrome as every other in-game text box (textBoxPanelStyle)
    // rather than a standalone art asset — no separate image to keep in
    // sync with the rest of the UI, and no image-aspect-ratio sizing to get
    // wrong across viewports (an earlier parchment-image version of this
    // modal broke specifically that way in real browser fullscreen).
    return (
      <div
        onClick={onClose}
        style={{
          position: "fixed",
          inset: 0,
          zIndex: 50,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          background: "rgba(0, 0, 0, 0.7)",
          padding: 16,
        }}
      >
        <div
          onClick={(e) => e.stopPropagation()}
          style={{
            ...textBoxPanelStyle(false),
            width: "min(92vw, 400px)",
            padding: "24px 26px 28px",
            fontFamily: gameFontFamily,
            textAlign: "center",
          }}
        >
          <button
            type="button"
            aria-label="닫기"
            onClick={onClose}
            style={{
              position: "absolute",
              top: 10,
              right: 12,
              background: "transparent",
              border: "none",
              color: theme.textMuted,
              fontSize: gameFontSize.md,
              cursor: "pointer",
              padding: 4,
            }}
          >
            ✕
          </button>

          <p
            style={{
              color: theme.gold,
              fontWeight: 600,
              fontSize: gameFontSize.md,
              fontFamily: gameFontFamily,
              letterSpacing: 0.5,
              margin: "0 0 16px",
              textShadow: "0 0 24px rgba(255, 215, 0, 0.3)",
            }}
          >
            그대의 이름을 법정에 새기시오
          </p>

          {errorMessage}
          {googleButton}

          <button
            type="button"
            onClick={onClose}
            style={{
              marginTop: 12,
              background: "none",
              border: "none",
              color: "#5a4a3a",
              fontSize: gameFontSize.sm,
              fontFamily: gameFontFamily,
              cursor: "pointer",
              textAlign: "center",
            }}
          >
            로그인 없이 계속하기
          </button>
        </div>
      </div>
    );
  }

  return (
    <div
      style={{
        minHeight: appShellHeight,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        background: theme.background,
        padding: isMobile ? 16 : 24,
        textAlign: "center",
        fontFamily: "Georgia, serif",
      }}
    >
      <p
        style={{
          color: "#6a2a3a",
          letterSpacing: isMobile ? 4 : 8,
          fontSize: gameFontSize.sm,
          marginBottom: 14,
          textTransform: "uppercase",
        }}
      >
        The Merchant of Venice
      </p>
      <h1
        style={{
          color: theme.gold,
          fontSize: "clamp(28px, 8vw, 40px)",
          fontWeight: 700,
          fontFamily: gameFontFamily,
          margin: "0 0 6px",
          letterSpacing: isMobile ? 1 : 3,
          textShadow: "0 0 40px rgba(255, 215, 0, 0.4)",
        }}
      >
        샤일록의 법정
      </h1>
      <p
        style={{
          color: "#7a5a4a",
          fontSize: gameFontSize.md,
          fontFamily: gameFontFamily,
          fontStyle: "italic",
          marginBottom: 28,
        }}
      >
        그대의 이름을 법정에 새기시오.
      </p>

      <div
        style={{
          width: "min(100%, 380px)",
          padding: "20px 20px 24px",
          background: "rgba(18, 12, 24, 0.72)",
          border: "1px solid #3a1028",
          borderRadius: 10,
          textAlign: "left",
        }}
      >
        {errorMessage}
        {googleButton}
      </div>

      <button
        type="button"
        onClick={() => router.push("/")}
        style={{
          marginTop: 8,
          background: "none",
          border: "none",
          color: "#5a4a3a",
          fontSize: gameFontSize.sm,
          fontFamily: gameFontFamily,
          cursor: "pointer",
        }}
      >
        로그인 없이 돌아가기
      </button>
    </div>
  );
}
