"use client";

import { useEffect, useState } from "react";
import Image from "next/image";
import { useRouter } from "next/navigation";

import { AuthScreen } from "@/components/auth/AuthScreen";
import { PrologueScreen } from "@/components/title/PrologueScreen";
import { useAppShellHeight } from "@/hooks/use-is-mobile";
import { useTitleActive } from "@/hooks/use-title-active";
import { fetchMe, logout } from "@/lib/api-client/auth";
import { startTrial } from "@/lib/api-client/trial-progression";
import type { UserFromApi } from "@/lib/api-client/types";
import { ILLUSTRATION_IMAGE_QUALITY } from "@/lib/constants/image-optimization";
import { gameFontFamily, gameFontSize } from "@/styles/text-box";
import { theme } from "@/styles/theme";

// 타이틀 이미지에 title/subtitle/tagline/본문 텍스트가 이미 그려져 있음 (MobileGate가
// 이게 렌더링되기 전에 모바일을 걸러내니까, 이건 데스크톱 전용 image-map UI임),
// 다만 — 이전 버전과 달리 — 버튼이나 로그인 아트는 그려져 있지 않아서, 그건 텍스트
// 아래 빈 공간에 배치된 실제 UI 엘리먼트임. 소스 PNG(2752x1536)에서 직접 측정한
// 값이지 눈대중 아님.
const TITLE_IMAGE_RATIO = "(2752 / 1536)";
// button-start-plaque.png: Gemini_Generated_Image_1nvtti1nvtti1nvt.png에서 크롭함
// (그린스크린 + drop shadow를 크로마키로 제거, login-button.png와 같은 despill
// 처리 — 그 에셋의 히스토리 참고). 900x394 (비율 ~2.28), 투명 배경, 울퉁불퉁한
// 장식 테두리 — 예전 button-start-frame.png/button-loading-frame.png
// (1927x608, 비율 ~3.17)가 둘 다 대체하던 딱딱한 사각형과는 다름.
// button-loading-plaque.png: Gemini_Generated_Image_rtdmebrtdmebrtdm.png에서
// 같은 방식으로 크롭함(그린스크린 크로마키 + despill), 그다음 파일 크기를
// 적당히 유지하려고 1000x446으로 다운스케일 (비율 ~2.24, 원본 크롭은 2240x999) —
// start plaque의 비율과 충분히 비슷해서 "contain" fallback 없이 같은 박스를
// 아래에서 공유할 수 있음.
const START_BUTTON_RECT = { left: "40.69%", top: "70.5%", width: "18.62%", height: "14.61%" };

export function TitleScreen() {
  const router = useRouter();
  const appShellHeight = useAppShellHeight();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [prologueTrialId, setPrologueTrialId] = useState<string | null>(null);
  const [user, setUser] = useState<UserFromApi | null>(null);
  const [startHovered, setStartHovered] = useState(false);
  const [loginHovered, setLoginHovered] = useState(false);
  const [showLoginModal, setShowLoginModal] = useState(false);
  const [revealed, setRevealed] = useState(false);
  const { setTitleActive } = useTitleActive();

  useEffect(() => {
    void fetchMe().then(setUser);
  }, []);

  // 도착하면 검은 화면에서 페이드인 — 이게 첫 방문인지 EndingScreen 자체의
  // 블랙아웃에서 돌아온 건지는 알 필요도 없고 알지도 못함; opacity 트랜지션이
  // 애니메이션을 시작할 프레임을 실제로 갖도록 즉시 true로 세팅하는 대신
  // 짧은 타임아웃을 둠.
  useEffect(() => {
    const timer = window.setTimeout(() => setRevealed(true), 50);
    return () => window.clearTimeout(timer);
  }, []);

  // FullscreenButton(descendant가 아니라 layout sibling으로 렌더링됨)은 검은
  // 프롤로그 화면이 타이틀 스플래시를 대체하는 시점을 알아야 함 — 이건 라우트
  // 변경이 아니라 로컬 state 전환이라, pathname만으로는 둘을 구분할 수 없음.
  useEffect(() => {
    setTitleActive(prologueTrialId === null);
  }, [prologueTrialId, setTitleActive]);

  const handleLogout = async () => {
    await logout();
    setUser(null);
  };

  const handleStart = async () => {
    setLoading(true);
    setError(null);
    try {
      const trial = await startTrial();
      setPrologueTrialId(trial.trial_id);
    } catch (e) {
      setError(e instanceof Error ? e.message : "재판을 시작할 수 없습니다");
      setLoading(false);
    }
  };

  if (prologueTrialId) {
    return (
      <PrologueScreen
        onComplete={() => router.push(`/trial/${prologueTrialId}`)}
      />
    );
  }

  return (
    <div
      style={{
        minHeight: appShellHeight,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        background: theme.background,
      }}
    >
      <div
        style={{
          position: "relative",
          overflow: "hidden",
          width: `min(100vw, calc(${appShellHeight} * ${TITLE_IMAGE_RATIO}))`,
          height: `min(${appShellHeight}, calc(100vw / ${TITLE_IMAGE_RATIO}))`,
          fontFamily: "Georgia, serif",
        }}
      >
        <Image
          src="/assets/title-screen.png"
          alt=""
          fill
          priority
          sizes="100vw"
          quality={ILLUSTRATION_IMAGE_QUALITY}
          style={{ objectFit: "cover" }}
        />
        <div
          aria-hidden
          // title-screen.png에 그려진 게 아니라 실제 텍스트임 — "THE MERCHANT OF
          // VENICE"는 원래 2752x1536 기준 (927,184)-(1824,216)에 그려진 아트였는데,
          // 그걸 지워버려서(title-screen.png 자체의 편집 히스토리 참고) 두 줄을
          // 하나의 블록으로 움직일 수 있게 됨: 위로 올려서 아래 "샤일록의 법정"
          // (그려진 것, y=268에 고정)과의 간격이 같은 아트의 다른 곳에 있는 그려진
          // "당신은 가해자인가…" → "베네치아, 16세기…" 간격(663−561 = 102px)과
          // 이제 맞도록 함. 색상/letter-spacing/크기는 여전히 원본 그려진 텍스트에서
          // 샘플링한 값(평균 ~#642225, cap-height 32px / 0.7 / 2752px 너비 ⇒ 1.66vw)
          // 이라 예전과 똑같이 읽히고 위치만 옮겨진 것.
          style={{
            position: "absolute",
            left: "50%",
            top: `${(96 / 1536) * 100}%`,
            transform: "translateX(-50%)",
            whiteSpace: "nowrap",
            pointerEvents: "none",
            fontFamily: 'Georgia, "Times New Roman", Times, serif',
            fontSize: "1.3vw",
            fontWeight: 500,
            letterSpacing: "0.35em",
            color: "#642225",
            opacity: 0.65,
            textShadow: "0 0 10px rgba(140, 50, 50, 0.25), 0 2px 3px rgba(0, 0, 0, 0.5)",
          }}
        >
          BASED ON
        </div>
        <div
          aria-hidden
          style={{
            position: "absolute",
            left: "50%",
            top: `${(146 / 1536) * 100}%`,
            transform: "translateX(-50%)",
            whiteSpace: "nowrap",
            pointerEvents: "none",
            fontFamily: 'Georgia, "Times New Roman", Times, serif',
            fontSize: "1.66vw",
            fontWeight: 500,
            letterSpacing: "0.35em",
            color: "#642225",
            opacity: 0.7,
            textShadow: "0 0 10px rgba(140, 50, 50, 0.25), 0 2px 3px rgba(0, 0, 0, 0.5)",
          }}
        >
          THE MERCHANT OF VENICE
        </div>
        <div
          // fixed가 아니라 absolute로, START_BUTTON_RECT 바로 아래
          // (같은 스케일링 컨테이너 기준 70.5%–85.11%)에 중앙 정렬 — 예전엔
          // 화면 우측 상단 모서리에 그냥 fixed로 박혀 있었는데, 그러니 화면이
          // 복잡한 타이틀 아트 위에서 동떨어져 보이고 놓치기 쉬웠음. START
          // 버튼 자체의 좌표 공간에 앵커링하면 플레이어가 메인 CTA를 본 직후
          // 시선이 이미 가 있는 위치에 놓이지, 눈이 안 가는 구석에 놓이지 않음.
          style={{
            position: "absolute",
            left: "50%",
            top: "87%",
            transform: "translateX(-50%)",
            zIndex: 5,
            display: "flex",
            alignItems: "center",
            gap: 12,
            whiteSpace: "nowrap",
            fontFamily: gameFontFamily,
            fontSize: gameFontSize.sm,
          }}
        >
          {user ? (
            <>
              <span style={{ color: theme.textBright }}>
                <span style={{ color: theme.gold }}>{user.nickname}</span> 님
              </span>
              <button
                type="button"
                onClick={() => router.push("/records")}
                style={{
                  background: "none",
                  border: "none",
                  color: "#7a5a4a",
                  fontSize: gameFontSize.sm,
                  fontFamily: gameFontFamily,
                  cursor: "pointer",
                  textDecoration: "underline",
                }}
              >
                재판 기록
              </button>
              <button
                type="button"
                onClick={() => void handleLogout()}
                style={{
                  background: "none",
                  border: "none",
                  color: "#7a5a4a",
                  fontSize: gameFontSize.sm,
                  fontFamily: gameFontFamily,
                  cursor: "pointer",
                  textDecoration: "underline",
                }}
              >
                로그아웃
              </button>
            </>
          ) : (
            // 아이콘만, plaque/border/배경 없음 — 원래와 같은 borderless
            // gradient-clip 텍스트인데, chip/button 모양 대신 더 밝고 채도
            // 높은 골드 그라디언트를 씀 (예전엔 칙칙한 벽돌색이라 아트에
            // 너무 쉽게 묻혔음).
            <button
              type="button"
              aria-label="로그인"
              onClick={() => setShowLoginModal(true)}
              onMouseEnter={() => setLoginHovered(true)}
              onMouseLeave={() => setLoginHovered(false)}
              style={{
                background: "transparent",
                border: "none",
                padding: "4px 2px",
                cursor: "pointer",
                fontFamily: '"Times New Roman", Times, serif',
                fontSize: "clamp(14px, 1.6vw, 24px)",
                fontWeight: 500,
                letterSpacing: 2,
                lineHeight: 1,
                backgroundImage:
                  "linear-gradient(180deg, #fff2b8 0%, #ffd700 28%, #e8a838 58%, #a86818 100%)",
                WebkitBackgroundClip: "text",
                backgroundClip: "text",
                color: "transparent",
                WebkitTextFillColor: "transparent",
                textShadow: loginHovered
                  ? "0 1px 0 rgba(255, 255, 255, 0.65), 0 2px 4px rgba(0, 0, 0, 0.6), 0 0 16px rgba(255, 215, 0, 0.7)"
                  : "0 1px 0 rgba(255, 255, 255, 0.45), 0 2px 3px rgba(0, 0, 0, 0.55)",
                filter: loginHovered ? "brightness(1.15)" : "brightness(1)",
                transition: "filter 0.15s ease, text-shadow 0.15s ease",
              }}
            >
              LOGIN
            </button>
          )}
        </div>

        {showLoginModal && <AuthScreen onClose={() => setShowLoginModal(false)} />}

        <div style={{ position: "absolute", ...START_BUTTON_RECT }}>
          <div
            aria-hidden
            style={{
              position: "absolute",
              inset: 0,
              borderRadius: 6,
              pointerEvents: "none",
              // box-shadow가 아니라 drop-shadow: 사각형 bounding box 주변에
              // 빛나는 대신 plaque 아트 자체의 알파 실루엣(울퉁불퉁한 장식
              // 테두리)을 그대로 따라감. 아래 애니메이션이 hover 시 완전히
              // 대체하니까, 이 resting-state filter는 그 상태로 *전환되는*
              // 순간에만 의미가 있음.
              filter:
                !loading && startHovered
                  ? "brightness(1.32) saturate(1.45) drop-shadow(0 0 14px rgba(255, 205, 80, 0.85)) drop-shadow(0 0 34px rgba(255, 150, 30, 0.6)) drop-shadow(0 0 60px rgba(255, 120, 20, 0.4))"
                  : "brightness(1) saturate(1) drop-shadow(0 0 0 rgba(255, 195, 60, 0))",
              animation: !loading && startHovered ? "startButtonGlow 1.6s ease-in-out infinite" : "none",
              transition: "filter 0.2s ease",
            }}
          >
            <Image
              key={loading ? "loading" : "start"}
              src={loading ? "/assets/button-loading-plaque.png" : "/assets/button-start-plaque.png"}
              alt=""
              fill
              sizes="20vw"
              quality={ILLUSTRATION_IMAGE_QUALITY}
              // 두 plaque 모두 이 박스 비율에 충분히 가깝게 크롭돼 있어서
              // 레터박스나 눈에 띄는 늘어남 없이 가장자리까지 꽉 채움.
              style={{ objectFit: "cover" }}
            />
          </div>
          <button
            type="button"
            onClick={() => void handleStart()}
            disabled={loading}
            style={{
              position: "absolute",
              inset: 0,
              background: "transparent",
              border: "none",
              borderRadius: 6,
              padding: 0,
              cursor: loading ? "wait" : "pointer",
            }}
            onMouseEnter={() => setStartHovered(true)}
            onMouseLeave={() => setStartHovered(false)}
          />
        </div>

        {error && (
          <div
            style={{
              position: "absolute",
              left: "50%",
              top: "78.5%",
              transform: "translateX(-50%)",
              maxWidth: "70%",
              background: "rgba(8, 3, 10, 0.85)",
              color: "#e88",
              padding: "6px 16px",
              borderRadius: 4,
              fontFamily: gameFontFamily,
              fontSize: "clamp(11px, 1.2vw, 15px)",
              textAlign: "center",
            }}
          >
            {error}
          </div>
        )}
      </div>

      <div
        aria-hidden
        style={{
          position: "fixed",
          inset: 0,
          zIndex: 90,
          background: "#000",
          opacity: revealed ? 0 : 1,
          pointerEvents: revealed ? "none" : "auto",
          transition: "opacity 3s ease-out",
        }}
      />
    </div>
  );
}
