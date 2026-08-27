import type { CSSProperties } from "react";

import { vwSize } from "@/styles/responsive";
import { theme } from "@/styles/theme";

export const gameFontFamily =
  '"Pretendard Variable", Pretendard, "Apple SD Gothic Neo", "Malgun Gothic", "Segoe UI", sans-serif';

/**
 * 게임 전체가 공유하는 타이포그래피 스케일 — vwSize()를 통한 clamp() 문자열
 * (styles/responsive.ts 참고)이고, 각각 1512px 기준 너비에서는 예전 raw px
 * 값과 정확히 똑같이 렌더링됨. 이걸 import하는 모든 화면(battle HUD,
 * title/auth/records 등)이 이제 이 값과 함께 스케일됨 — 이건 토큰을
 * 중앙화하면서 생기는 의도적이고 리스크 낮은 부수 효과지, 컴포넌트별 범위
 * 침범이 아님.
 */
export const gameFontSize = {
  xs: vwSize(12),
  sm: vwSize(15),
  nm: vwSize(16),
  md: vwSize(18),
  base: vwSize(20),
  lg: vwSize(23),
  xl: vwSize(26),
} as const;

/** meters, evidence, skills가 공유하는 HUD 패널 chrome. */
export function hudPanelStyle(padding = `${vwSize(9)} ${vwSize(14)}`, compact = false): CSSProperties {
  return {
    background: compact ? "rgba(12, 6, 16, 0.82)" : "rgba(12, 6, 16, 0.94)",
    borderRadius: compact ? 6 : 4,
    padding,
    border: "1px solid #4a2838",
    boxShadow: compact
      ? "0 1px 6px rgba(0, 0, 0, 0.35)"
      : "0 2px 8px rgba(0, 0, 0, 0.45)",
    backdropFilter: compact ? "blur(6px)" : undefined,
  };
}

export function hudLabelStyle(color: string): CSSProperties {
  return {
    color,
    fontWeight: 600,
    textShadow: "0 1px 2px rgba(0, 0, 0, 0.6)",
  };
}

export const textBox = {
  background: "rgba(18, 12, 24, 0.72)",
  border: "1px solid #3a1028",
  borderTopAccent: "3px solid #3a1028",
  borderRadius: 10,
  padding: `${vwSize(26)} ${vwSize(30)} ${vwSize(34)}`,
  fontFamily: gameFontFamily,
} as const;

// "speakerTabStyle"라는 이름은 이게 실제 칩(bg + border + radius, 캐릭터별
// 색상)으로 렌더링되던 시절 이름 — 호출부들이 이 이름을 참조하고 있어서 그대로
// 남겨뒀지만, 지금은 그냥 화자 이름의 텍스트 스타일일 뿐이고 모든 화자가 같은
// gold 색 (캐릭터별 팔레트는 더 이상 없음).
export function speakerTabStyle(): CSSProperties {
  return {
    display: "inline-block",
    color: theme.gold,
    fontSize: gameFontSize.sm,
    fontWeight: 700,
    letterSpacing: 3,
    textTransform: "uppercase",
    // 대사창 테두리 자체도 금색이라(dialogue-box-wide.png), 라벨이 테두리
    // 가까이 있으면 옅은 그림자 하나로는 거의 안 보였음 — 배경이 금속
    // 테두리든 차콜 안쪽이든 항상 또렷하게 보이도록 진한 다중 그림자로
    // 어두운 외곽선(halo) 효과를 줌.
    textShadow:
      "0 0 3px rgba(0, 0, 0, 0.95), 0 0 6px rgba(0, 0, 0, 0.85), 0 1px 2px rgba(0, 0, 0, 0.9)",
  };
}

// 색상이 더 이상 이걸로 분기하지 않는데도 `speaker`를 시그니처에 남겨둠
// (DialogueBox가 항상 이걸 넘김) — 예전엔 NARRATOR가 다른 모든 화자
// ("#e8e0d0")보다 더 어둡게("#9a8aaa") 렌더링돼서, 같은 DialogueBox를 공유하는
// prologue/opening(항상 speaker="NARRATOR")이 in-battle 대사보다 칙칙한 다른
// 색으로 보이는 문제가 있었음. 모두 같은 색을 쓰면 prologue와 battle 텍스트가
// 시각적으로 동일하게 보임.
export function dialogueTextStyle(_speaker: string, compact = false): CSSProperties {
  return {
    margin: 0,
    fontSize: compact ? gameFontSize.md : gameFontSize.base,
    lineHeight: 1.75,
    fontFamily: gameFontFamily,
    color: "#e8e0d0",
    whiteSpace: "pre-wrap",
    wordBreak: "break-word",
    minHeight: compact ? "3.25em" : "5.25em",
  };
}

// dialogue-box-panel.png: brass 프레임의 parchment-dark 패널 (green/magenta-
// screen 소스를 chroma-key 처리한 뒤 border-flood-erode 패스를 거침 — 이
// 파일의 git history 참고 — flat threshold key가 남기는 fringe를 없애기
// 위해서). flat한 background+border 대신 CSS border-image(9-slice)로
// 렌더링해서, 같은 아트가 어떤 박스의 종횡비(dialogue box ~6:1, choice
// panel, 개별 choice 버튼 등)에도 corner radius나 border 두께를 뒤틀지 않고
// 깔끔하게 늘어남 — 단순 <img>/object-fit이었다면 프레임이 일그러지거나
// letterbox가 생겼을 것. DIALOGUE_PANEL_SLICE는 *원본* 이미지 자체의
// 픽셀 기준(1187x333)이고, border-image-slice는 렌더링 크기를 아예 무시하기
// 때문에 compact/vwSize에 맞춰 바뀔 필요가 없음.
const DIALOGUE_PANEL_SLICE = 60;

/**
 * "같은 세트에서 깎아낸" 느낌을 원하는 모든 패널/버튼(dialogue box, choice
 * panel, choice 버튼)이 공유하는 brass-frame border-image. `fill`을 켜면
 * 소스의 (반투명) 중앙 slice도 그 엘리먼트 자신의 background로 칠해짐 —
 * 버튼처럼 그 아래에 자체 solid `background`를 깔고 싶은 컨트롤은 false를
 * 넘길 것 (border-image와 별도의 `background`는 함께 잘 합성됨; `fill`은
 * 그냥 그 위를 덮어버릴 뿐).
 */
export function brassFrameStyle(borderWidth: string, fill: boolean): CSSProperties {
  return {
    boxSizing: "border-box",
    borderStyle: "solid",
    borderWidth,
    borderImageSource: "url(/assets/dialogue-box-panel.png)",
    borderImageSlice: fill ? `${DIALOGUE_PANEL_SLICE} fill` : `${DIALOGUE_PANEL_SLICE}`,
    borderImageWidth: borderWidth,
    borderImageRepeat: "stretch",
    // border-radius 없음: border-image는 어차피 이걸 무시함 (두 속성 사이의
    // 잘 알려진 CSS 간극) — 둥근 모양은 클리핑이 아니라 소스 PNG 자체의 alpha
    // 모양(모서리가 이미 투명 처리돼 있음)에서 나옴.
  };
}

// dialogue-box-wide.png: brassFrameStyle의 dialogue-box-panel.png와 별개
// 파일(대사창의 실제 종횡비 ~6.6:1에 가깝게 새로 뽑음) — 늘려서(stretch)
// 채우는 것만으로는 결국 미묘하게 안 맞아서, 다시 9-slice로 돌아옴.
// 소스 자체 픽셀 기준 모서리 반경 실측(~40px)에 여유를 둔 값.
const DIALOGUE_WIDE_SLICE = 60;

// choice 패널/버튼(brassFrameStyle, choiceButtonStyle)은 여전히 기존
// dialogue-box-panel.png(자기 slice=60)를 그대로 씀 — 이 함수만 새
// 이미지+새 slice 상수로 바뀐 것.
export function textBoxPanelStyle(compact = false): CSSProperties {
  // 예전 dialogue-box-panel.png 버전과 렌더링 크기가 정확히 같도록 같은
  // border-width 값(vwSize(7)/vwSize(10))을 그대로 씀.
  const borderWidth = vwSize(compact ? 7 : 10);
  return {
    position: "relative",
    boxSizing: "border-box",
    borderStyle: "solid",
    borderWidth,
    borderImageSource: "url(/assets/dialogue-box-wide.png)",
    borderImageSlice: `${DIALOGUE_WIDE_SLICE} fill`,
    borderImageWidth: borderWidth,
    borderImageRepeat: "stretch",
    fontFamily: textBox.fontFamily,
  };
}

export const TEXT_BOX_MAX_WIDTH = vwSize(940);
/** landscape 휴대폰에서는 dialogue가 화면 끝까지 늘어나지 않도록 dock을 더 좁게. */
export const TEXT_BOX_MAX_WIDTH_MOBILE = vwSize(550);

/** 타이핑 중에 박스 크기가 바뀌지 않도록 고정한 body 높이 (~3줄 분량). */
export const DIALOGUE_BODY_MIN_HEIGHT = vwSize(118);

/** advance arrow 자리를 위해 항상 남겨두는 하단 padding. */
export const DIALOGUE_BODY_PADDING_BOTTOM = vwSize(32);

export function textBoxDockStyle(compact = false): CSSProperties {
  return {
    flexShrink: 0,
    width: "100%",
    padding: compact ? `0 14vw ${vwSize(8)}` : `0 ${vwSize(16)} ${vwSize(20)}`,
    fontFamily: textBox.fontFamily,
    background: "transparent",
  };
}

export function textBoxDockInnerStyle(compact = false): CSSProperties {
  return {
    width: "100%",
    maxWidth: compact ? TEXT_BOX_MAX_WIDTH_MOBILE : TEXT_BOX_MAX_WIDTH,
    margin: "0 auto",
  };
}

export function choiceButtonStyle(compact = false): CSSProperties {
  return {
    ...brassFrameStyle(vwSize(compact ? 4 : 6), false),
    display: "flex",
    alignItems: compact ? "flex-start" : "center",
    justifyContent: "space-between",
    flexWrap: compact ? "wrap" : "nowrap",
    gap: compact ? vwSize(8) : vwSize(12),
    width: "100%",
    padding: compact ? `${vwSize(8)} ${vwSize(10)}` : `${vwSize(14)} ${vwSize(20)}`,
    textAlign: "left",
    // (fill 없는) 프레임 아래에 자체 solid fill — 이미 반투명한 choice
    // panel 안에 또 다른 반투명+블러 레이어를 겹쳐 쌓는 대신, 버튼이 잘
    // 보이도록 유지.
    background: "#100510",
    color: "#e0c090",
    cursor: "pointer",
    fontSize: compact ? gameFontSize.sm : gameFontSize.md,
    fontFamily: textBox.fontFamily,
    lineHeight: 1.5,
    transition: "background 0.15s, box-shadow 0.15s",
  };
}

export function nextSceneButtonStyle(): CSSProperties {
  return {
    width: "100%",
    padding: vwSize(15),
    background: "#1a0810",
    color: "#c0a060",
    border: "1px solid #4a1828",
    borderRadius: 2,
    cursor: "pointer",
    fontFamily: textBox.fontFamily,
    fontSize: gameFontSize.nm,
    letterSpacing: 3,
    transition: "all 0.15s",
  };
}

export function staticTextBoxStyle(padding = `${vwSize(20)} ${vwSize(24)}`): CSSProperties {
  return {
    ...textBoxPanelStyle(),
    padding,
    textAlign: "center",
  };
}
