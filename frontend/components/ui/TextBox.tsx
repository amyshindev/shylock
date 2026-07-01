"use client";

import type { CSSProperties, ReactNode } from "react";

import { speakerTabStyle, textBoxPanelStyle } from "@/styles/text-box";

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
  const label = speakerLabel ?? speaker;
  const displayTab = showSpeakerTab && Boolean(speaker && label);

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
          <div style={{ ...speakerTabStyle(speaker), marginLeft: 12, marginTop: -1 }}>
            {label}
          </div>
        </div>
      )}

      <div
        onClick={onClick}
        style={{
          padding: displayTab ? "14px 20px 8px" : "20px 24px 8px",
          minHeight: displayTab ? 72 : undefined,
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
              fontSize: 12,
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
