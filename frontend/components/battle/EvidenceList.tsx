"use client";

import Image from "next/image";

import { EVIDENCE_BY_ID } from "@/data/evidence";
import type { TubalCourtRecord } from "@/lib/tubal-evidence";
import { theme } from "@/styles/theme";

interface EvidenceListProps {
  curatedIds: string[];
  tubalRecords?: TubalCourtRecord[];
  onSelectCurated?: (evidenceId: string) => void;
  onSelectTubal?: (record: TubalCourtRecord) => void;
  presentMode?: boolean;
  compact?: boolean;
}

const TUBAL_BORDER = "#5a8a4a";
const CURATED_BORDER = "#3a1028";

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

  const iconSize = compact ? 40 : 48;
  const itemWidth = compact ? 48 : 56;

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column-reverse",
        alignItems: "flex-start",
        gap: 8,
        maxHeight: compact ? "min(28vh, 200px)" : "min(40vh, 280px)",
        overflowY: "auto",
        padding: "8px 10px",
        background: "rgba(18, 12, 24, 0.85)",
        borderRadius: 10,
        border: `1px solid ${presentMode ? theme.gold : CURATED_BORDER}`,
      }}
    >
      {presentMode && (
        <div
          style={{
            fontSize: 9,
            letterSpacing: 1,
            color: theme.gold,
            marginBottom: 2,
          }}
        >
          증거 제시
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
                  background: "rgba(20, 32, 16, 0.95)",
                  border: `2px solid ${TUBAL_BORDER}`,
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
                fontSize: 9,
                color: "#7ab86a",
                marginTop: 4,
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
                  background: theme.border,
                  border: `2px solid ${CURATED_BORDER}`,
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
                fontSize: 9,
                color: theme.textMuted,
                marginTop: 4,
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
    </div>
  );
}
