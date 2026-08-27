"use client";

import { useEffect, useState } from "react";
import Image from "next/image";
import { useRouter } from "next/navigation";

import { loginWithGoogle } from "@/lib/api-client/auth";
import { useAppShellHeight, useIsMobile } from "@/hooks/use-is-mobile";
import { ILLUSTRATION_IMAGE_QUALITY } from "@/lib/constants/image-optimization";
import { gameFontFamily, gameFontSize } from "@/styles/text-box";
import { theme } from "@/styles/theme";

// login-modal-panel.png에는 제목/버튼 라벨/skip-link 텍스트가 이미 그려져 있음
// (그린스크린 소스에서 border-flood-fill 크로마키로 크롭함 — 단순 색상 threshold가
// 아니라서, 순진한 방식이었다면 Google 로고 자체의 초록색 부분에 구멍을 뚫었을
// 텐데 그러지 않음; 그려진 "✕" 닫기 아이콘도 대칭인 좌측 상단 모서리를 미러링해서
// 지워버림), 원본 917x590 그대로. 아래 두 개의 상호작용 가능한 hit-area는 그
// 소스 이미지 자체의 픽셀 bbox 기준으로 배치된 투명 버튼이지 눈대중 아님:
//   Google 버튼(흰색 pill): (167,275)-(749,369)
//   "로그인 없이 계속하기" 텍스트: (329,423)-(588,467) (그려진 작은 텍스트 주변에
//   편안한 hit target을 위해 몇 px 여유를 둠)
const LOGIN_MODAL_RATIO = "917 / 590";
const GOOGLE_BUTTON_RECT = { left: "18.21%", top: "46.61%", width: "63.47%", height: "15.93%" };
const SKIP_BUTTON_RECT = { left: "35.88%", top: "71.69%", width: "28.24%", height: "7.46%" };

interface AuthScreenProps {
  /**
   * 전달되면 전체 페이지 레이아웃 대신 화면에 이미 떠 있는 것 위에 fixed-position
   * 모달 오버레이로 렌더링됨 — TitleScreen에서 "로그인" 클릭 시 다른 페이지로
   * 이동하지 않도록 쓰임. 호출하면 이동 없이 모달만 닫힘.
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
    // 실패하면 Google 콜백이 ?error=google을 붙여서 리다이렉트해옴.
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
    // 의도적으로 document.body에 대한 portal을 쓰지 않음: ForceLandscape는 좁은/세로
    // 뷰포트에서 {children}을 CSS로 회전시키는 컨테이너로 감싸는데(globals.css의
    // .force-landscape-frame 참고), 이 컨테이너가 `position: fixed` descendant의
    // containing block 역할도 함께 함. document.body로의 portal은 이 컨테이너를
    // 벗어나버려서 같은 회전/사이징을 절대 받지 못함. 여기서 inline으로 렌더링하면
    // 나머지 모든 것과 같은 회전된 프레임 안에 남아있게 됨.
    //
    // login-modal-panel.png에는 제목 + 버튼 라벨 + skip-link 텍스트가 이미 아트로
    // 그려져 있음(그 소스 hit-area 픽셀은 파일 최상단 주석 참고). 사이징은
    // `width: min(92vw, 400px)` + CSS `aspect-ratio` 조합임 (TitleScreen의 배경이
    // 필요로 하는 이전의 vw/vh dual-min() 방식이 아님) — 모달은 max-width 상한만
    // 있으면 되니까, aspect-ratio로 높이를 유도하는 방식이 이 모달의 이전 이미지
    // 버전이 실제 브라우저 fullscreen에서 깨졌던 수동 사이징 버그를 피하게 해줌.
    return (
      <div
        onClick={onClose}
        style={{
          position: "fixed",
          inset: 0,
          zIndex: 50,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          background: "rgba(0, 0, 0, 0.7)",
          padding: 16,
        }}
      >
        <div
          onClick={(e) => e.stopPropagation()}
          style={{
            position: "relative",
            width: "min(92vw, 400px)",
            aspectRatio: LOGIN_MODAL_RATIO,
          }}
        >
          <Image
            src="/assets/login-modal-panel.png"
            alt="그대의 이름을 법정에 새기시오"
            fill
            sizes="400px"
            quality={ILLUSTRATION_IMAGE_QUALITY}
            style={{ objectFit: "contain" }}
          />

          <button
            type="button"
            aria-label="Google로 로그인하기"
            disabled={loading}
            onClick={() => void handleGoogleLogin()}
            style={{
              position: "absolute",
              ...GOOGLE_BUTTON_RECT,
              background: "transparent",
              border: "none",
              padding: 0,
              cursor: loading ? "wait" : "pointer",
            }}
          />
          {loading && (
            // 이미 그려진 라벨은 예전 실제 <button> 텍스트가 하던 것처럼
            // "이동하는 중…"으로 바꿔치기가 안 되니까 — 대신 흰 pill을 어둡게
            // 하고 그 위에 같은 로딩 문구를 오버레이함.
            <div
              aria-hidden
              style={{
                position: "absolute",
                ...GOOGLE_BUTTON_RECT,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                background: "rgba(10, 6, 10, 0.6)",
                borderRadius: 14,
                color: "#e0c090",
                fontFamily: gameFontFamily,
                fontSize: gameFontSize.sm,
                pointerEvents: "none",
              }}
            >
              이동하는 중…
            </div>
          )}

          <button
            type="button"
            aria-label="로그인 없이 계속하기"
            onClick={onClose}
            style={{
              position: "absolute",
              ...SKIP_BUTTON_RECT,
              background: "transparent",
              border: "none",
              padding: 0,
              cursor: "pointer",
            }}
          />
        </div>

        {errorMessage && (
          <div onClick={(e) => e.stopPropagation()} style={{ marginTop: 14 }}>
            {errorMessage}
          </div>
        )}
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
