"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { loginWithGoogle } from "@/lib/api-client/auth";
import { useAppShellHeight, useIsMobile } from "@/hooks/use-is-mobile";
import { gameFontFamily, gameFontSize } from "@/styles/text-box";
import { theme } from "@/styles/theme";

export function AuthScreen() {
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
          margin: "0 0 6px",
          letterSpacing: isMobile ? 1 : 3,
          textShadow: "0 0 40px rgba(255, 215, 0, 0.4)",
        }}
      >
        샤일록의 법정
      </h1>
      <p style={{ color: "#7a5a4a", fontSize: gameFontSize.md, fontStyle: "italic", marginBottom: 28 }}>
        그대의 이름으로 다시 서라.
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
        {error && (
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
        )}

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
            background: "#ffffff",
            color: "rgba(0, 0, 0, 0.72)",
            border: "1px solid #dadce0",
            borderRadius: 6,
            cursor: loading ? "wait" : "pointer",
            opacity: loading ? 0.7 : 1,
          }}
        >
          <svg width="18" height="18" viewBox="0 0 48 48" aria-hidden="true">
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
          {loading ? "이동하는 중…" : "Google로 시작하기"}
        </button>
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
