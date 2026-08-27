"use client";

import { useEffect, useState } from "react";
import { usePathname } from "next/navigation";

import { useFullscreen } from "@/hooks/use-fullscreen";
import { useTitleActive } from "@/hooks/use-title-active";
import { gameFontFamily, gameFontSize } from "@/styles/text-box";

const ICON_COLOR = "#f0d8c8"; // 다른 곳(SkillPanel, LoreChatWidget)에서 쓰는 것과 같은 밝은 양피지 톤
// fullscreenHintFade 키프레임(globals.css) 자체의 전체 duration과 일치 —
// 타임아웃은 그 애니메이션이 끝난 시점에 hint를 그냥 unmount시킬 뿐.
const HINT_DURATION_MS = 2600;

/**
 * 전역 fullscreen 토글 — root layout에 한 번만 렌더링해서 모든 화면(title, battle,
 * ending, records)에서 쓸 수 있게 함. 우측 하단(bottom:16, right:16)에 위치 —
 * 좌측 하단(bottom:16, left:16)에 있는 LoreChatWidget의 launcher 버튼과 대칭.
 *
 * 진입 전용: 일단 fullscreen에 들어가면 그걸 벗어나는 화면상의 버튼은 없음
 * (브라우저가 이미 Esc를 fullscreen 종료에 바인딩해두고 있어서, 진입 시 화면 상단
 * 중앙에 그 사실을 알려주는 토스트가 뜬 뒤 스스로 사라짐 — fullscreen인 동안 내내
 * UI가 어수선해질 필요는 없음).
 *
 * 타이틀 스플래시 화면 자체에서는 진입 버튼이 항상 보임(희미하게, hover 시 밝아짐).
 * 그 외 모든 곳 — 검은 프롤로그 화면 포함 (이 화면도 여전히 "/" 라우트라 pathname만
 * 으로는 타이틀과 구분이 안 돼서 useTitleActive()를 쓰는 이유) — 에서는 기본적으로
 * 숨겨져 있다가 마우스가 모서리 근처로 올 때만 (fade + slide로) 떠오름 — 게임 진행
 * 중에는 시선을 뺏지 않기 위함.
 *
 * iOS Safari는 임의 엘리먼트에 대한 Fullscreen API가 없어서(<video>만 가능),
 * 거기서는 isSupported가 false가 되고 조용히 no-op으로 보이는 것보다는 아예
 * 아무것도 렌더링하지 않음.
 */
export function FullscreenButton() {
  const { isFullscreen, isSupported, toggleFullscreen } = useFullscreen();
  const pathname = usePathname();
  const { titleActive } = useTitleActive();
  const [active, setActive] = useState(false);
  const [showHint, setShowHint] = useState(false);

  useEffect(() => {
    if (!isFullscreen) {
      // 이게 없으면, 아래 타이머가 발동하기 전에 나가버릴 경우 showHint가
      // true로 멈춰있게 됨 — 나중에 다시 fullscreen에 진입하면 다시 true로
      // 세팅되는데, React는 이걸 no-op 업데이트로 취급해서 <FullscreenHint>가
      // 절대 remount되지 않고 CSS 애니메이션도 다시 재생되지 않음. 여기서
      // 명시적으로 리셋해줘야 매번 진입할 때마다 진짜 false->true 전환
      // (그리고 새 DOM 노드)이 보장됨.
      setShowHint(false);
      return;
    }
    setShowHint(true);
    const timer = setTimeout(() => setShowHint(false), HINT_DURATION_MS);
    return () => clearTimeout(timer);
  }, [isFullscreen]);

  if (!isSupported) return null;

  const alwaysVisible = pathname === "/" && titleActive;
  const revealed = alwaysVisible || active;

  return (
    <>
      {showHint && <FullscreenHint />}

      {!isFullscreen && (
        <div
          // bottom:16, right:16을 중심으로 — LoreChatWidget의 bottom:16, left:16과
          // 대칭 — hover 감지 영역이 사방으로 넓어져도 아이콘 자체가 실제로 놓이는
          // 위치는 바뀌지 않게 함.
          style={{
            position: "fixed",
            bottom: 16 - 86,
            right: 16 - 86,
            zIndex: 38,
            width: 44 + 172,
            height: 44 + 172,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
          onMouseEnter={() => setActive(true)}
          onMouseLeave={() => setActive(false)}
        >
          <button
            type="button"
            aria-label="전체화면으로 보기"
            title="전체화면으로 보기"
            onClick={toggleFullscreen}
            onFocus={() => setActive(true)}
            onBlur={() => setActive(false)}
            style={{
              width: 44,
              height: 44,
              padding: 0,
              border: "none",
              background: "transparent",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              cursor: "pointer",
              opacity: alwaysVisible ? (active ? 1 : 0.85) : revealed ? 1 : 0,
              transform: alwaysVisible ? "none" : `translateY(${revealed ? 0 : 16}px)`,
              transition: "opacity 0.2s ease, transform 0.2s ease",
              pointerEvents: alwaysVisible || revealed ? "auto" : "none",
            }}
          >
            <MaximizeIcon />
          </button>
        </div>
      )}
    </>
  );
}

function FullscreenHint() {
  return (
    <div
      style={{
        position: "fixed",
        top: 20,
        left: "50%",
        zIndex: 60,
        background: "rgba(20, 10, 18, 0.94)",
        color: ICON_COLOR,
        border: "1px solid #a07840",
        borderRadius: 6,
        padding: "12px 24px",
        fontFamily: gameFontFamily,
        fontSize: gameFontSize.lg,
        boxShadow: "0 4px 20px rgba(0, 0, 0, 0.5), 0 0 24px 4px rgba(255, 195, 100, 0.35)",
        pointerEvents: "none",
        animation: "fullscreenHintFade 2.6s ease-out forwards",
      }}
    >
      전체화면을 종료하려면 Esc를 누르세요
    </div>
  );
}

function MaximizeIcon() {
  return (
    <svg width="30" height="30" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path
        d="M8 3H5a2 2 0 0 0-2 2v3m18 0V5a2 2 0 0 0-2-2h-3m0 18h3a2 2 0 0 0 2-2v-3M3 16v3a2 2 0 0 0 2 2h3"
        stroke={ICON_COLOR}
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}
