"use client";

import Image from "next/image";

import { EVIDENCE_BY_ID } from "@/data/evidence";
import type { ChoiceOption } from "@/data/scenes";
import { choiceButtonStyle } from "@/styles/text-box";
import { theme } from "@/styles/theme";

interface ChoiceListProps {
  header?: string;
  prompt: string;
  options: ChoiceOption[];
  onSelect: (option: ChoiceOption) => void;
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
        fontSize: 11,
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
            fontSize: 11,
          }}
        >
          {ev.iconFallback ?? "✦"}
        </span>
      )}
      {ev.name}
    </span>
  );
}

export function ChoiceList({
  header,
  prompt,
  options,
  onSelect,
  disabled,
}: ChoiceListProps) {
  return (
    <div
      style={{
        borderTop: "1px solid #2a1020",
        padding: "10px 12px 12px",
        background: "rgba(18, 12, 24, 0.85)",
      }}
    >
      <div
        style={{
          fontSize: 10,
          color: "#5a3a4a",
          letterSpacing: 2,
          marginBottom: 8,
          paddingLeft: 4,
        }}
      >
        {header ?? "▶ 샤일록의 선택"}
      </div>
      <p
        style={{
          margin: "0 0 8px",
          paddingLeft: 4,
          fontSize: 12,
          lineHeight: 1.6,
          color: "#7a5a6a",
          fontStyle: "italic",
        }}
      >
        {prompt}
      </p>
      <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
        {options.map((opt, index) => (
          <button
            key={opt.id}
            type="button"
            disabled={disabled}
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
              {opt.text}
            </span>
            {opt.evidence && <EvidenceBadge evidenceId={opt.evidence} />}
          </button>
        ))}
      </div>
    </div>
  );
}
