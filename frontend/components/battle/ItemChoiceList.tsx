"use client";

import { useState } from "react";
import Image from "next/image";

import { EVIDENCE_BY_ID } from "@/data/evidence";
import { useIsMobile } from "@/hooks/use-is-mobile";
import { gameFontSize } from "@/styles/text-box";
import { theme } from "@/styles/theme";

interface ItemChoiceListProps {
  header?: string;
  prompt?: string;
  itemIds: string[];
  onSelect: (itemId: string) => void;
  disabled?: boolean;
}

const ITEM_BORDER = "#c8a060";

function ItemIcon({ evidenceId, size }: { evidenceId: string; size: number }) {
  const ev = EVIDENCE_BY_ID[evidenceId];

  if (ev?.icon) {
    return (
      <Image
        src={ev.icon}
        alt=""
        width={size}
        height={size}
        style={{
          borderRadius: "50%",
          objectFit: "cover",
          border: `2px solid ${ITEM_BORDER}`,
          boxShadow: `0 0 6px ${ITEM_BORDER}44`,
          flexShrink: 0,
        }}
      />
    );
  }

  return (
    <span
      style={{
        width: size,
        height: size,
        borderRadius: "50%",
        background: "#2a1828",
        border: `2px solid ${ITEM_BORDER}`,
        boxShadow: `0 0 6px ${ITEM_BORDER}44`,
        display: "inline-flex",
        alignItems: "center",
        justifyContent: "center",
        fontSize: size > 40 ? 22 : 18,
        color: theme.gold,
        flexShrink: 0,
      }}
    >
      {ev?.iconFallback ?? "✦"}
    </span>
  );
}

export function ItemChoiceList({
  header,
  prompt,
  itemIds,
  onSelect,
  disabled,
}: ItemChoiceListProps) {
  const isMobile = useIsMobile();
  const [openNoteId, setOpenNoteId] = useState<string | null>(null);

  const items = itemIds
    .map((id) => EVIDENCE_BY_ID[id])
    .filter((ev): ev is NonNullable<typeof ev> => Boolean(ev));

  if (items.length === 0) return null;

  const iconSize = isMobile ? 44 : 48;

  return (
    <div
      style={{
        padding: isMobile ? "8px 10px 10px" : "12px 14px 14px",
        marginTop: isMobile ? 0 : 10,
        background: "rgba(18, 12, 24, 0.85)",
        border: "1px solid #3a1028",
        borderRadius: 10,
      }}
    >
      <div
        style={{
          fontSize: isMobile ? gameFontSize.sm : gameFontSize.nm,
          color: "#5a3a4a",
          letterSpacing: 2,
          marginBottom: isMobile ? 6 : 10,
          paddingLeft: 4,
        }}
      >
        {header ?? "▶ 제시할 아이템을 선택하시오"}
      </div>
      {prompt && (
        <p
          style={{
            margin: "0 0 8px",
            paddingLeft: 4,
            fontSize: isMobile ? gameFontSize.sm : gameFontSize.md,
            lineHeight: 1.5,
            color: "#7a5a6a",
            fontStyle: "italic",
          }}
        >
          {prompt}
        </p>
      )}
      {/* Side-by-side cards so two items fit without scrolling. */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: items.length === 1 ? "1fr" : "1fr 1fr",
          gap: isMobile ? 6 : 8,
          alignItems: "stretch",
        }}
      >
        {items.map((ev) => (
          <button
            key={ev.id}
            type="button"
            disabled={disabled}
            onClick={() => onSelect(ev.id)}
            style={{
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              justifyContent: "flex-start",
              gap: isMobile ? 6 : 8,
              width: "100%",
              minHeight: isMobile ? 120 : 140,
              padding: isMobile ? "10px 8px" : "12px 10px",
              textAlign: "center",
              background: "#100510",
              border: "1px solid #3a1828",
              borderRadius: 4,
              color: "#e0c090",
              cursor: disabled ? "not-allowed" : "pointer",
              opacity: disabled ? 0.6 : 1,
              fontFamily: "inherit",
              transition: "all 0.15s",
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
            <ItemIcon evidenceId={ev.id} size={iconSize} />
            <span
              style={{
                color: "#e0c090",
                fontSize: isMobile ? gameFontSize.sm : gameFontSize.md,
                fontWeight: 600,
                lineHeight: 1.35,
                display: "inline-flex",
                alignItems: "center",
                justifyContent: "center",
                gap: 6,
                flexWrap: "wrap",
              }}
            >
              {ev.name}
              {ev.note && (
                <span
                  role="button"
                  tabIndex={0}
                  aria-label="각색 설명 보기"
                  title="각색 설명"
                  onClick={(e) => {
                    e.stopPropagation();
                    setOpenNoteId((cur) => (cur === ev.id ? null : ev.id));
                  }}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" || e.key === " ") {
                      e.preventDefault();
                      e.stopPropagation();
                      setOpenNoteId((cur) => (cur === ev.id ? null : ev.id));
                    }
                  }}
                  style={{
                    display: "inline-flex",
                    alignItems: "center",
                    justifyContent: "center",
                    width: 18,
                    height: 18,
                    borderRadius: "50%",
                    border: `1.5px solid ${theme.gold}`,
                    background:
                      openNoteId === ev.id ? theme.gold : "rgba(255, 215, 0, 0.14)",
                    color: openNoteId === ev.id ? "#1a0810" : theme.gold,
                    fontSize: 12,
                    fontStyle: "italic",
                    fontWeight: 800,
                    lineHeight: 1,
                    fontFamily: "Georgia, 'Times New Roman', serif",
                    cursor: "pointer",
                    userSelect: "none",
                    flexShrink: 0,
                  }}
                >
                  i
                </span>
              )}
            </span>
            <span
              style={{
                fontSize: isMobile ? 11 : gameFontSize.sm,
                color: "#7a5a6a",
                lineHeight: 1.4,
                whiteSpace: "normal",
              }}
            >
              {ev.desc}
            </span>
            {ev.note && openNoteId === ev.id && (
              <span
                style={{
                  fontSize: 11,
                  color: "#8f8ab0",
                  lineHeight: 1.45,
                  fontStyle: "italic",
                  whiteSpace: "normal",
                  textAlign: "left",
                  width: "100%",
                  paddingLeft: 6,
                  borderLeft: "2px solid rgba(143, 138, 176, 0.4)",
                }}
              >
                {ev.note}
              </span>
            )}
          </button>
        ))}
      </div>
    </div>
  );
}
