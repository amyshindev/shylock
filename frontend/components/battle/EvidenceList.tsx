"use client";

import Image from "next/image";

import { EVIDENCE_BY_ID } from "@/data/evidence";
import { theme } from "@/styles/theme";

interface EvidenceListProps {
  evidenceIds: string[];
}

export function EvidenceList({ evidenceIds }: EvidenceListProps) {
  const items = evidenceIds
    .map((id) => EVIDENCE_BY_ID[id])
    .filter(Boolean);

  if (items.length === 0) return null;

  return (
    <div
      style={{
        position: "absolute",
        left: 16,
        bottom: 20,
        zIndex: 2,
        display: "flex",
        flexDirection: "column-reverse",
        alignItems: "flex-start",
        gap: 8,
        maxHeight: "min(40vh, 280px)",
        overflowY: "auto",
        padding: "8px 10px",
        background: "rgba(18, 12, 24, 0.85)",
        borderRadius: 10,
        border: "1px solid #3a1028",
      }}
    >
      {items.map((ev) => (
        <div
          key={ev.id}
          title={ev.name}
          style={{
            flexShrink: 0,
            textAlign: "left",
            width: 56,
          }}
        >
          {ev.icon ? (
            <Image
              src={ev.icon}
              alt={ev.name}
              width={48}
              height={48}
              style={{ borderRadius: "50%", objectFit: "cover" }}
              onError={(e) => {
                const el = e.target as HTMLImageElement;
                el.style.display = "none";
              }}
            />
          ) : (
            <div
              style={{
                width: 48,
                height: 48,
                margin: 0,
                borderRadius: "50%",
                background: theme.border,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: 22,
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
            }}
          >
            {ev.name}
          </div>
        </div>
      ))}
    </div>
  );
}
