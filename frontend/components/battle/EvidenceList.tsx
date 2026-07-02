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
}: EvidenceListProps) {
  const curatedItems = curatedIds.map((id) => EVIDENCE_BY_ID[id]).filter(Boolean);
  const hasItems = curatedItems.length > 0 || tubalRecords.length > 0;

  if (!hasItems) return null;

  const iconSize = compact ? 44 : 52;
  const itemWidth = compact ? 52 : 64;

  return (
    <div
      style={{
        ...hudPanelStyle("8px 11px"),
        display: "flex",
        flexDirection: "column-reverse",
        alignItems: "flex-start",
        gap: 8,
        maxHeight: compact ? "min(28vh, 200px)" : "min(40vh, 280px)",
        overflowY: "auto",
        border: `1px solid ${presentMode ? theme.gold : "#4a2838"}`,
        boxShadow: presentMode
          ? "0 2px 12px rgba(255, 215, 0, 0.2), 0 2px 8px rgba(0, 0, 0, 0.45)"
          : "0 2px 8px rgba(0, 0, 0, 0.45)",
      }}
    >
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
              textAlign: "left",
              width: itemWidth,
              padding: 0,
              border: "none",
              background: "transparent",
              cursor: clickable ? "pointer" : "default",
            }}
          >
            <div style={{ position: "relative", width: iconSize, height: iconSize }}>
              <div
                style={{
                  width: iconSize,
                  height: iconSize,
                  borderRadius: "50%",
                  background: "rgba(20, 32, 16, 0.98)",
                  border: `2px solid ${TUBAL_BORDER}`,
                  boxShadow: `0 0 8px ${TUBAL_BORDER}44`,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontSize: compact ? 18 : 22,
                }}
              >
                📜
              </div>
            </div>
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
              textAlign: "left",
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
                  margin: 0,
                  borderRadius: "50%",
                  background: "#2a1828",
                  border: `2px solid ${CURATED_BORDER}`,
                  boxShadow: `0 0 8px ${CURATED_BORDER}44`,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontSize: compact ? 18 : 22,
                  color: theme.gold,
                }}
              >
                {ev.iconFallback ?? "✦"}
              </div>
            )}
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
          </button>
        );
      })}

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
    </div>
  );
}
