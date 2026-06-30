"use client";

import type { CSSProperties, ReactNode } from "react";

import { speakerTabStyle, textBox, textBoxPanelStyle } from "@/styles/text-box";

interface TextBoxProps {
  speaker?: string;
  speakerLabel?: string;
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
  children,
  onClick,
  showAdvanceArrow,
  style,
  bodyStyle,
  footer,
}: TextBoxProps) {
  const label = speakerLabel ?? speaker;

  return (
    <div style={{ ...textBoxPanelStyle(), ...style }}>
      {label && speaker && (
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
          padding: label ? "14px 20px 8px" : textBox.padding,
          minHeight: label ? 72 : undefined,
          cursor: onClick ? "pointer" : "default",
          position: "relative",
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
