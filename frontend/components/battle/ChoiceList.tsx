"use client";

import Image from "next/image";

import { EVIDENCE_BY_ID } from "@/data/evidence";
import type { ChoiceOption } from "@/data/scenes";
import type { TubalCourtRecord } from "@/lib/tubal-evidence";
import { choiceButtonStyle, gameFontSize } from "@/styles/text-box";
import { theme } from "@/styles/theme";

const TUBAL_BORDER = "#6aaa5a";
const TUBAL_ENHANCED_TOOLTIP = "투발의 아이템으로 강화된 선택지 (+5 DP)";

interface ChoiceListProps {
  header?: string;
  prompt: string;
  options: ChoiceOption[];
  tubalEnhancedChoices?: Record<string, string>;
  tubalCourtRecords?: TubalCourtRecord[];
  onSelect: (option: ChoiceOption) => void;
  onBack?: () => void;
  showEvidenceBadge?: boolean;
  disabled?: boolean;
}

function EvidenceBadge({ evidenceId }: { evidenceId: string }) {
  const ev = EVIDENCE_BY_ID[evidenceId];
  if (!ev) return null;

  return (
    <span
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: 6,
        flexShrink: 0,
        fontSize: gameFontSize.sm,
        color: "#8b6040",
      }}
    >
      {ev.icon ? (
        <Image
          src={ev.icon}
          alt=""
          width={20}
          height={20}
          style={{ borderRadius: "50%", objectFit: "cover" }}
        />
      ) : (
        <span
          style={{
            width: 20,
            height: 20,
            borderRadius: "50%",
            background: theme.border,
            display: "inline-flex",
            alignItems: "center",
            justifyContent: "center",
            fontSize: gameFontSize.sm,
          }}
        >
          {ev.iconFallback ?? "✦"}
        </span>
      )}
      {ev.name}
    </span>
  );
}

function TubalEvidenceBadge({ name }: { name: string }) {
  return (
    <span
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: 6,
        flexShrink: 0,
        fontSize: gameFontSize.sm,
        color: "#8b6040",
      }}
    >
      <span
        style={{
          width: 20,
          height: 20,
          borderRadius: "50%",
          background: "rgba(20, 32, 16, 0.98)",
          border: `2px solid ${TUBAL_BORDER}`,
          boxShadow: `0 0 6px ${TUBAL_BORDER}44`,
          display: "inline-flex",
          alignItems: "center",
          justifyContent: "center",
          fontSize: 11,
          flexShrink: 0,
        }}
      >
        📜
      </span>
      {name}
    </span>
  );
}

export function ChoiceList({
  header,
  prompt,
  options,
  tubalEnhancedChoices,
  tubalCourtRecords = [],
  onSelect,
  onBack,
  showEvidenceBadge = true,
  disabled,
}: ChoiceListProps) {
  const latestTubalRecord = tubalCourtRecords[tubalCourtRecords.length - 1];

  return (
    <div
      style={{
        padding: "12px 14px 14px",
        marginTop: 10,
        background: "rgba(18, 12, 24, 0.85)",
        border: "1px solid #3a1028",
        borderRadius: 10,
      }}
    >
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          gap: 8,
          marginBottom: 10,
        }}
      >
        <div
          style={{
            fontSize: gameFontSize.nm,
            color: "#5a3a4a",
            letterSpacing: 2,
            paddingLeft: 4,
          }}
        >
          {header ?? "▶ 샤일록의 선택"}
        </div>
        {onBack && (
          <button
            type="button"
            disabled={disabled}
            onClick={onBack}
            style={{
              background: "transparent",
              border: "1px solid #3a1828",
              borderRadius: 4,
              color: "#7a5a6a",
              fontSize: gameFontSize.sm,
              padding: "4px 10px",
              cursor: disabled ? "not-allowed" : "pointer",
              flexShrink: 0,
            }}
          >
            ← 다른 아이템
          </button>
        )}
      </div>
      <p
        style={{
          margin: "0 0 8px",
          paddingLeft: 4,
          fontSize: gameFontSize.md,
          lineHeight: 1.6,
          color: "#7a5a6a",
          fontStyle: "italic",
        }}
      >
        {prompt}
      </p>
      <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
        {options.map((opt, index) => {
          const enhancedText = tubalEnhancedChoices?.[opt.id];
          const isEnhanced = Boolean(enhancedText);
          const choiceText = enhancedText ?? opt.text;

          return (
            <button
              key={opt.id}
              type="button"
              disabled={disabled}
              title={isEnhanced ? TUBAL_ENHANCED_TOOLTIP : undefined}
              onClick={() => onSelect(opt)}
              style={{
                ...choiceButtonStyle(),
                opacity: disabled ? 0.6 : 1,
                cursor: disabled ? "not-allowed" : "pointer",
              }}
              onMouseEnter={(e) => {
                if (!disabled) {
                  e.currentTarget.style.background = "#1a0820";
                  e.currentTarget.style.borderColor = "rgba(255, 215, 0, 0.31)";
                }
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = "#100510";
                e.currentTarget.style.borderColor = "#3a1828";
              }}
            >
              <span>
                <span style={{ color: "#5a3a4a" }}>{index + 1}. </span>
                {choiceText}
              </span>
              <span style={{ display: "inline-flex", alignItems: "center", gap: 8, flexShrink: 0 }}>
                {opt.hpCost > 0 && (
                  <span
                    style={{
                      fontSize: gameFontSize.sm,
                      color: "#dd4848",
                      fontWeight: 600,
                    }}
                  >
                    -{opt.hpCost} HP
                  </span>
                )}
                {opt.portiaDamage > 0 && (
                  <span
                    style={{
                      fontSize: gameFontSize.sm,
                      color: "#e84455",
                      fontWeight: 600,
                    }}
                  >
                    -{opt.portiaDamage} 포샤
                  </span>
                )}
                {isEnhanced ? (
                  <TubalEvidenceBadge
                    name={latestTubalRecord?.name ?? "투발 아이템"}
                  />
                ) : (
                  showEvidenceBadge &&
                  opt.evidence && <EvidenceBadge evidenceId={opt.evidence} />
                )}
              </span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
