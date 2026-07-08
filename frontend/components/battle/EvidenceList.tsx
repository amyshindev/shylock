"use client";

import Image from "next/image";

import { EVIDENCE_BY_ID } from "@/data/evidence";
import type { TubalCourtRecord } from "@/lib/tubal-evidence";
import { gameFontSize, hudLabelStyle, hudPanelStyle } from "@/styles/text-box";
import { theme } from "@/styles/theme";

interface EvidenceListProps {
  curatedIds: string[];
  tubalRecords?: TubalCourtRecord[];
  onSelectCurated?: (evidenceId: string) => void;
  onSelectTubal?: (record: TubalCourtRecord) => void;
  presentMode?: boolean;
  compact?: boolean;
  layout?: "vertical" | "horizontal";
}

const TUBAL_BORDER = "#6aaa5a";
const TUBAL_LABEL = "#b8f0a0";
const CURATED_BORDER = "#c8a060";
const CURATED_LABEL = "#f0d8b8";

export function EvidenceList({
  curatedIds,
  tubalRecords = [],
  onSelectCurated,
  onSelectTubal,
  presentMode = false,
  compact = false,
  layout = "vertical",
}: EvidenceListProps) {
  const curatedItems = curatedIds.map((id) => EVIDENCE_BY_ID[id]).filter(Boolean);
  const hasItems = curatedItems.length > 0 || tubalRecords.length > 0;
  const isHorizontal = layout === "horizontal";

  if (!hasItems) return null;

  const iconSize = isHorizontal ? 32 : compact ? 44 : 52;
  const itemWidth = isHorizontal ? iconSize : compact ? 52 : 64;
  const showLabels = !isHorizontal;

  return (
    <div
      style={{
        ...hudPanelStyle(isHorizontal ? "4px 6px" : "8px 11px", isHorizontal || compact),
        display: "flex",
        flexDirection: isHorizontal ? "row" : "column-reverse",
        alignItems: isHorizontal ? "center" : "flex-start",
        gap: isHorizontal ? 6 : 8,
        maxHeight: isHorizontal ? undefined : compact ? "min(28vh, 200px)" : "min(40vh, 280px)",
        maxWidth: isHorizontal ? "100%" : undefined,
        overflowX: isHorizontal ? "auto" : undefined,
        overflowY: isHorizontal ? "hidden" : "auto",
        WebkitOverflowScrolling: "touch",
        flexShrink: isHorizontal ? 0 : undefined,
        border: `1px solid ${presentMode ? theme.gold : "#4a2838"}`,
        boxShadow: presentMode
          ? "0 2px 12px rgba(255, 215, 0, 0.2), 0 2px 8px rgba(0, 0, 0, 0.45)"
          : isHorizontal
            ? "0 1px 6px rgba(0, 0, 0, 0.35)"
            : "0 2px 8px rgba(0, 0, 0, 0.45)",
      }}
    >
      {isHorizontal && (
        <div
          style={{
            ...hudLabelStyle(presentMode ? theme.gold : "#e8dce4"),
            fontSize: 10,
            letterSpacing: 0.5,
            flexShrink: 0,
            paddingRight: 2,
          }}
        >
          {presentMode ? "제시" : "아이템"}
        </div>
      )}

      {tubalRecords.map((record) => {
        const clickable = Boolean(onSelectTubal);
        return (
          <button
            key={record.id}
            type="button"
            title={record.name}
            disabled={!clickable}
            onClick={() => onSelectTubal?.(record)}
            style={{
              flexShrink: 0,
              textAlign: "center",
              width: itemWidth,
              padding: 0,
              border: "none",
              background: "transparent",
              cursor: clickable ? "pointer" : "default",
            }}
          >
            <div
              style={{
                width: iconSize,
                height: iconSize,
                margin: "0 auto",
                borderRadius: "50%",
                background: "rgba(20, 32, 16, 0.98)",
                border: `2px solid ${TUBAL_BORDER}`,
                boxShadow: `0 0 8px ${TUBAL_BORDER}44`,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: isHorizontal ? 14 : compact ? 18 : 22,
              }}
            >
              📜
            </div>
            {showLabels && (
              <div
                style={{
                  ...hudLabelStyle(TUBAL_LABEL),
                  fontSize: gameFontSize.xs,
                  marginTop: 5,
                  overflow: "hidden",
                  textOverflow: "ellipsis",
                  whiteSpace: "nowrap",
                  maxWidth: itemWidth + 8,
                }}
              >
                {record.name}
              </div>
            )}
          </button>
        );
      })}

      {curatedItems.map((ev) => {
        const clickable = Boolean(onSelectCurated);
        return (
          <button
            key={ev.id}
            type="button"
            title={ev.name}
            disabled={!clickable}
            onClick={() => onSelectCurated?.(ev.id)}
            style={{
              flexShrink: 0,
              textAlign: "center",
              width: itemWidth,
              padding: 0,
              border: "none",
              background: "transparent",
              cursor: clickable ? "pointer" : "default",
            }}
          >
            {ev.icon ? (
              <Image
                src={ev.icon}
                alt={ev.name}
                width={iconSize}
                height={iconSize}
                style={{
                  borderRadius: "50%",
                  objectFit: "cover",
                  border: `2px solid ${CURATED_BORDER}`,
                  boxShadow: `0 0 8px ${CURATED_BORDER}44`,
                  display: "block",
                  margin: "0 auto",
                }}
                onError={(e) => {
                  const el = e.target as HTMLImageElement;
                  el.style.display = "none";
                }}
              />
            ) : (
              <div
                style={{
                  width: iconSize,
                  height: iconSize,
                  margin: "0 auto",
                  borderRadius: "50%",
                  background: "#2a1828",
                  border: `2px solid ${CURATED_BORDER}`,
                  boxShadow: `0 0 8px ${CURATED_BORDER}44`,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontSize: isHorizontal ? 14 : compact ? 18 : 22,
                  color: theme.gold,
                }}
              >
                {ev.iconFallback ?? "✦"}
              </div>
            )}
            {showLabels && (
              <div
                style={{
                  ...hudLabelStyle(CURATED_LABEL),
                  fontSize: gameFontSize.xs,
                  marginTop: 5,
                  overflow: "hidden",
                  textOverflow: "ellipsis",
                  whiteSpace: "nowrap",
                  maxWidth: itemWidth + 8,
                }}
              >
                {ev.name}
              </div>
            )}
          </button>
        );
      })}

      {!isHorizontal && (
        <div
          style={{
            ...hudLabelStyle(presentMode ? theme.gold : "#e8dce4"),
            fontSize: gameFontSize.xs,
            letterSpacing: presentMode ? 1 : 0.8,
            marginBottom: 2,
            flexShrink: 0,
          }}
        >
          {presentMode ? "아이템 제시" : "아이템"}
        </div>
      )}
    </div>
  );
}
