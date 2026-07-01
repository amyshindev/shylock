"use client";

import { gameFontSize } from "@/styles/text-box";
import { theme } from "@/styles/theme";

import type { PressPresentConfig } from "@/data/scene-types";

interface PressPresentPanelProps {
  config: PressPresentConfig;
  testimonyIndex: number;
  pressedIds: string[];
  loadingPresent: boolean;
  onPress: () => void;
  onPresent: () => void;
  onContinue: () => void;
  canContinue: boolean;
}

export function PressPresentPanel({
  config,
  testimonyIndex,
  pressedIds,
  loadingPresent,
  onPress,
  onPresent,
  onContinue,
  canContinue,
}: PressPresentPanelProps) {
  const current = config.testimony[testimonyIndex];
  const currentPressed = current ? pressedIds.includes(current.id) : false;
  const canPresent =
    current?.id === config.contradiction.statementId && currentPressed && !loadingPresent;

  return (
    <div
      style={{
        marginTop: 14,
        padding: "14px 16px",
        background: "rgba(12, 6, 14, 0.92)",
        border: `1px solid ${theme.border}`,
        borderRadius: 4,
      }}
    >
      <div
        style={{
          fontSize: gameFontSize.nm,
          letterSpacing: 1.5,
          color: theme.gold,
          marginBottom: 12,
        }}
      >
        ▶ 군중의 증언에 대응하라
      </div>
      <div
        style={{
          fontSize: gameFontSize.md,
          lineHeight: 1.65,
          color: theme.textBright,
          marginBottom: 14,
        }}
      >
        {current?.text}
      </div>
      <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
        <button
          type="button"
          disabled={!current || currentPressed || loadingPresent}
          onClick={onPress}
          style={actionButtonStyle(!current || currentPressed || loadingPresent)}
        >
          Press (반박)
        </button>
        <button
          type="button"
          disabled={!canPresent}
          onClick={onPresent}
          style={actionButtonStyle(!canPresent, true)}
        >
          {loadingPresent ? "판정 중…" : "Present (증거 제시)"}
        </button>
        {canContinue && (
          <button
            type="button"
            onClick={onContinue}
            style={actionButtonStyle(false)}
          >
            다음 장면
          </button>
        )}
      </div>
    </div>
  );
}

function actionButtonStyle(disabled: boolean, accent = false) {
  return {
    padding: "10px 16px",
    fontSize: gameFontSize.sm,
    letterSpacing: 0.5,
    cursor: disabled ? "not-allowed" : "pointer",
    background: disabled
      ? "rgba(12, 6, 10, 0.7)"
      : accent
        ? "rgba(90, 138, 74, 0.2)"
        : "rgba(20, 10, 16, 0.9)",
    color: disabled ? theme.textMuted : accent ? "#7ab86a" : theme.textBright,
    border: `1px solid ${disabled ? "#2a1820" : accent ? "#5a8a4a" : "#4a3040"}`,
    borderRadius: 3,
    opacity: disabled ? 0.55 : 1,
  } as const;
}
