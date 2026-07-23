"use client";

import { useEffect, useState, type CSSProperties, type FormEvent } from "react";
import { useRouter } from "next/navigation";

import { login, signup } from "@/lib/api-client/auth";
import { API_BASE, API_PREFIX } from "@/lib/api-client/config";
import { useAppShellHeight, useIsMobile } from "@/hooks/use-is-mobile";
import { gameFontFamily, gameFontSize } from "@/styles/text-box";
import { theme } from "@/styles/theme";

type Mode = "login" | "signup";

const inputStyle: CSSProperties = {
  width: "100%",
  marginBottom: 14,
  padding: "11px 16px",
  color: "#e0c090",
  background: "#100510",
  border: "1px solid #3a1828",
  borderRadius: 2,
  fontFamily: gameFontFamily,
  fontSize: gameFontSize.md,
  outline: "none",
  boxSizing: "border-box",
};

const labelStyle: CSSProperties = {
  display: "block",
  marginBottom: 6,
  color: "#7a5a4a",
  fontSize: gameFontSize.xs,
  letterSpacing: 2,
  textTransform: "uppercase",
  fontFamily: gameFontFamily,
};

export function AuthScreen() {
  const router = useRouter();
  const isMobile = useIsMobile();
  const appShellHeight = useAppShellHeight();
  const [mode, setMode] = useState<Mode>("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [nickname, setNickname] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const isSignup = mode === "signup";

  useEffect(() => {
    // Google callback redirects back with ?error=google on failure.
    const params = new URLSearchParams(window.location.search);
    if (params.get("error") === "google") {
      setError("구글 로그인에 실패했습니다. 잠시 후 다시 시도해 주세요.");
    }
  }, []);

  const handleGoogleLogin = () => {
    window.location.href = `${API_BASE}${API_PREFIX}/auth/google/login`;
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      if (isSignup) {
        await signup(email, password, nickname);
      } else {
        await login(email, password);
      }
      router.push("/");
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
        {isSignup ? "법정에 이름을 올려라." : "그대의 이름으로 다시 서라."}
      </p>

      <form
        onSubmit={(e) => void handleSubmit(e)}
        style={{
          width: "min(100%, 380px)",
          padding: "20px 20px 24px",
          background: "rgba(18, 12, 24, 0.72)",
          border: "1px solid #3a1028",
          borderRadius: 10,
          textAlign: "left",
        }}
      >
        <label style={labelStyle} htmlFor="auth-email">
          Email
        </label>
        <input
          id="auth-email"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          autoFocus
          style={inputStyle}
        />
        {isSignup && (
          <>
            <label style={labelStyle} htmlFor="auth-nickname">
              Nickname
            </label>
            <input
              id="auth-nickname"
              type="text"
              value={nickname}
              onChange={(e) => setNickname(e.target.value)}
              required
              maxLength={32}
              style={inputStyle}
            />
          </>
        )}
        <label style={labelStyle} htmlFor="auth-password">
          Password
        </label>
        <input
          id="auth-password"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          minLength={isSignup ? 8 : 1}
          style={inputStyle}
        />

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
          type="submit"
          disabled={loading}
          style={{
            display: "block",
            width: "100%",
            padding: "14px 28px",
            fontFamily: "Georgia, serif",
            fontSize: gameFontSize.base,
            fontWeight: 700,
            letterSpacing: isMobile ? 2 : 4,
            textTransform: "uppercase",
            background: theme.red,
            color: theme.gold,
            border: "2px solid rgba(255, 215, 0, 0.4)",
            boxShadow: "0 0 24px rgba(139, 0, 0, 0.5)",
            cursor: loading ? "wait" : "pointer",
            opacity: loading ? 0.7 : 1,
          }}
        >
          {loading ? "확인 중…" : isSignup ? "서명하다" : "입장하다"}
        </button>

        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 10,
            margin: "18px 0 14px",
            color: "#5a4a3a",
            fontSize: gameFontSize.xs,
            fontFamily: gameFontFamily,
          }}
        >
          <span style={{ flex: 1, height: 1, background: "#3a1828" }} />
          또는
          <span style={{ flex: 1, height: 1, background: "#3a1828" }} />
        </div>

        <button
          type="button"
          onClick={handleGoogleLogin}
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
            cursor: "pointer",
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
          Google로 시작하기
        </button>
      </form>

      <button
        type="button"
        onClick={() => {
          setMode(isSignup ? "login" : "signup");
          setError(null);
        }}
        style={{
          marginTop: 20,
          background: "none",
          border: "none",
          color: "#7a5a4a",
          fontSize: gameFontSize.sm,
          fontFamily: gameFontFamily,
          cursor: "pointer",
          textDecoration: "underline",
        }}
      >
        {isSignup ? "이미 계정이 있다면 — 로그인" : "처음 온 자라면 — 회원가입"}
      </button>

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
