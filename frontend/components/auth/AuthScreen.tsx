"use client";

import { useState, type CSSProperties, type FormEvent } from "react";
import { useRouter } from "next/navigation";

import { login, signup } from "@/lib/api-client/auth";
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
