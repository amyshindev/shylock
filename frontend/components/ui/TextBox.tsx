"use client";

import type { CSSProperties, ReactNode } from "react";

import { useIsMobile } from "@/hooks/use-is-mobile";
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
  const sidePad = displayTab ? (isMobile ? 14 : 22) : isMobile ? 16 : 26;
  const topPad = displayTab ? (isMobile ? 12 : 16) : isMobile ? 16 : 22;

  return (
    <div style={{ ...textBoxPanelStyle(), ...style }}>
      {displayTab && speaker && (
        <div
          style={{
            display: "flex",
            alignItems: "center",
            borderBottom: "1px solid #2a1020",
            margin: `-1px -1px 0`,
            paddingBottom: 0,
          }}
        >
          <div style={{ ...speakerTabStyle(speaker), marginLeft: isMobile ? 8 : 12, marginTop: -1 }}>
            {label}
          </div>
        </div>
      )}

      <div
        onClick={onClick}
        style={{
          paddingTop: topPad,
          paddingRight: sidePad,
          paddingLeft: sidePad,
          paddingBottom: 10,
          minHeight: displayTab ? (isMobile ? 72 : 84) : undefined,
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
              right: 16,
              bottom: 8,
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
