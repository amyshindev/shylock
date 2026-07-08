"use client";

import { useState } from "react";
import Image from "next/image";

import { EVIDENCE_BY_ID } from "@/data/evidence";
import { useIsMobile } from "@/hooks/use-is-mobile";
import { choiceButtonStyle, gameFontSize } from "@/styles/text-box";
import { theme } from "@/styles/theme";

interface ItemChoiceListProps {
  header?: string;
  prompt?: string;
  itemIds: string[];
  onSelect: (itemId: string) => void;
  disabled?: boolean;
}

const ITEM_BORDER = "#c8a060";

function ItemIcon({ evidenceId }: { evidenceId: string }) {
  const ev = EVIDENCE_BY_ID[evidenceId];
  const size = 40;

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
        fontSize: 18,
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

  return (
    <div
      style={{
        padding: isMobile ? "8px 10px 10px" : "12px 14px 14px",
        marginTop: isMobile ? 4 : 10,
        background: "rgba(18, 12, 24, 0.85)",
        border: "1px solid #3a1028",
        borderRadius: 10,
      }}
    >
      <div
        style={{
          fontSize: gameFontSize.nm,
          color: "#5a3a4a",
          letterSpacing: 2,
          marginBottom: 10,
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
            fontSize: gameFontSize.md,
            lineHeight: 1.6,
            color: "#7a5a6a",
            fontStyle: "italic",
          }}
        >
          {prompt}
        </p>
      )}
      <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
        {items.map((ev) => (
          <button
            key={ev.id}
            type="button"
            disabled={disabled}
            onClick={() => onSelect(ev.id)}
            style={{
              ...choiceButtonStyle(isMobile),
              gap: 12,
              alignItems: "flex-start",
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
            <span
              style={{
                display: "inline-flex",
                alignItems: "flex-start",
                gap: 12,
                minWidth: 0,
              }}
            >
              <ItemIcon evidenceId={ev.id} />
              <span style={{ display: "flex", flexDirection: "column", gap: 3, minWidth: 0 }}>
                <span
                  style={{
                    color: "#e0c090",
                    display: "inline-flex",
                    alignItems: "center",
                    gap: 8,
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
                      onMouseEnter={(e) => {
                        e.currentTarget.style.background = theme.gold;
                        e.currentTarget.style.color = "#1a0810";
                      }}
                      onMouseLeave={(e) => {
                        const active = openNoteId === ev.id;
                        e.currentTarget.style.background = active
                          ? theme.gold
                          : "rgba(255, 215, 0, 0.14)";
                        e.currentTarget.style.color = active ? "#1a0810" : theme.gold;
                      }}
                      style={{
                        display: "inline-flex",
                        alignItems: "center",
                        justifyContent: "center",
                        width: 20,
                        height: 20,
                        borderRadius: "50%",
                        border: `1.5px solid ${theme.gold}`,
                        background:
                          openNoteId === ev.id
                            ? theme.gold
                            : "rgba(255, 215, 0, 0.14)",
                        color: openNoteId === ev.id ? "#1a0810" : theme.gold,
                        fontSize: 13,
                        fontStyle: "italic",
                        fontWeight: 800,
                        lineHeight: 1,
                        fontFamily: "Georgia, 'Times New Roman', serif",
                        cursor: "pointer",
                        userSelect: "none",
                        flexShrink: 0,
                        transition: "all 0.15s",
                      }}
                    >
                      i
                    </span>
                  )}
                </span>
                <span
                  style={{
                    fontSize: gameFontSize.sm,
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
                      fontSize: gameFontSize.sm,
                      color: "#8f8ab0",
                      lineHeight: 1.5,
                      fontStyle: "italic",
                      whiteSpace: "normal",
                      marginTop: 2,
                      paddingLeft: 8,
                      borderLeft: "2px solid rgba(143, 138, 176, 0.4)",
                    }}
                  >
                    {ev.note}
                  </span>
                )}
              </span>
            </span>
          </button>
        ))}
      </div>
    </div>
  );
}
