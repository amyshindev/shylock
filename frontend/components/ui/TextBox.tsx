"use client";

import type { CSSProperties, ReactNode } from "react";

import { useIsMobile } from "@/hooks/use-is-mobile";
import { vwSize } from "@/styles/responsive";
import { speakerTabStyle, textBoxPanelStyle, gameFontSize } from "@/styles/text-box";

interface TextBoxProps {
  speaker?: string;
  speakerLabel?: string;
  showSpeakerTab?: boolean;
  children: ReactNode;
  onClick?: () => void;
  showAdvanceArrow?: boolean;
  style?: CSSProperties;
  bodyStyle?: CSSProperties;
  footer?: ReactNode;
}

export function TextBox({
  speaker,
  speakerLabel,
  showSpeakerTab = false,
  children,
  onClick,
  showAdvanceArrow,
  style,
  bodyStyle,
  footer,
}: TextBoxProps) {
  const isMobile = useIsMobile();
  const label = speakerLabel ?? speaker;
  const displayTab = showSpeakerTab && Boolean(speaker && label);
  const sidePad = vwSize(displayTab ? (isMobile ? 14 : 22) : isMobile ? 16 : 26);
  const topPad = vwSize(displayTab ? (isMobile ? 12 : 16) : isMobile ? 16 : 22);

  return (
    <div style={{ ...textBoxPanelStyle(isMobile), ...style }}>
      {displayTab && speaker && (
        // 이제 그냥 텍스트 라벨임 — chip/card chrome(background, border,
        // radius) 없음. 예전에 이 태그가 갖고 있던 `margin: -1px -1px 0`은
        // 이 행 자신의 border를 패널의 옛 1px flat border에 딱 맞붙이기
        // 위한 것이었는데, 그 트릭이 border-image 프레임에는 적용되지
        // 않아서 나머지 card 스타일링과 함께 빠짐.
        <div style={{ paddingTop: topPad, paddingLeft: `calc(${sidePad} + ${vwSize(10)})` }}>
          <span style={speakerTabStyle()}>{label}</span>
        </div>
      )}

      <div
        onClick={onClick}
        style={{
          paddingTop: topPad,
          paddingRight: sidePad,
          paddingLeft: sidePad,
          paddingBottom: vwSize(10),
          minHeight: displayTab ? vwSize(isMobile ? 72 : 84) : undefined,
          cursor: onClick ? "pointer" : "default",
          position: "relative",
          boxSizing: "border-box",
          ...bodyStyle,
        }}
      >
        {children}

        {showAdvanceArrow && (
          <span
            aria-hidden
            className="dialogue-advance-arrow"
            style={{
              position: "absolute",
              right: vwSize(16),
              bottom: vwSize(8),
              color: "#ffd700",
              fontSize: gameFontSize.nm,
              lineHeight: 1,
            }}
          >
            ▼
          </span>
        )}
      </div>

      {footer}
    </div>
  );
}
