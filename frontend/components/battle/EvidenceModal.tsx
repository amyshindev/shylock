"use client";

import Image from "next/image";

import { TextBox } from "@/components/ui/TextBox";
import { EVIDENCE_BY_ID } from "@/data/evidence";
import { theme } from "@/styles/theme";

interface EvidenceModalProps {
  evidenceId: string;
  name: string;
  quote: string;
}

export function EvidenceModal({ evidenceId, name, quote }: EvidenceModalProps) {
  const meta = EVIDENCE_BY_ID[evidenceId];

  return (
    <div
      style={{
        position: "fixed",
        inset: 0,
        zIndex: 55,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        background: "rgba(0, 0, 0, 0.7)",
        padding: 24,
      }}
    >
      <TextBox
        speaker="NARRATOR"
        speakerLabel="증거"
        style={{
          maxWidth: 400,
          width: "90%",
          border: `2px solid ${theme.gold}`,
          boxShadow: "0 0 40px rgba(255, 215, 0, 0.19)",
        }}
        bodyStyle={{ padding: "24px 28px", textAlign: "center" }}
      >
        {meta?.icon ? (
          <Image
            src={meta.icon}
            alt={name}
            width={96}
            height={96}
            style={{ borderRadius: "50%", objectFit: "cover" }}
            onError={(e) => {
              (e.target as HTMLImageElement).style.display = "none";
            }}
          />
        ) : (
          <div
            style={{
              width: 96,
              height: 96,
              margin: "0 auto",
              borderRadius: "50%",
              background: theme.border,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: 40,
              color: theme.gold,
            }}
          >
            {meta?.iconFallback ?? "✦"}
          </div>
        )}
        <h3 style={{ color: theme.gold, margin: "16px 0 12px", fontSize: 16 }}>{name}</h3>
        <p
          style={{
            margin: 0,
            color: "#d4b060",
            fontSize: 13,
            lineHeight: 1.8,
            fontStyle: "italic",
            borderLeft: "2px solid rgba(255, 215, 0, 0.25)",
            paddingLeft: 12,
            textAlign: "left",
          }}
        >
          &ldquo;{quote}&rdquo;
        </p>
      </TextBox>
    </div>
  );
}
