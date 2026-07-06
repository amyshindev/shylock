"use client";

import Image from "next/image";

import { TextBox } from "@/components/ui/TextBox";
import { EVIDENCE_BY_ID } from "@/data/evidence";
import type { EvidenceDetailView } from "@/lib/tubal-evidence";
import { gameFontSize } from "@/styles/text-box";
import { theme } from "@/styles/theme";

interface CourtEvidenceModalProps {
  detail: EvidenceDetailView;
  onClose?: () => void;
}

export function CourtEvidenceModal({ detail, onClose }: CourtEvidenceModalProps) {
  const isTubal = detail.kind === "tubal";
  const meta = detail.kind === "curated" ? EVIDENCE_BY_ID[detail.evidenceId] : null;
  const metaLine = [detail.speaker, detail.actScene].filter(Boolean).join(" · ");

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
      onClick={onClose}
    >
      <div onClick={(e) => e.stopPropagation()}>
        <TextBox
          speaker="NARRATOR"
          speakerLabel={isTubal ? "법정 기록" : "아이템"}
          style={{
            maxWidth: isTubal ? 440 : 400,
            width: "90vw",
            border: `2px solid ${isTubal ? "#5a8a4a" : theme.gold}`,
            boxShadow: isTubal
              ? "0 0 40px rgba(90, 138, 74, 0.25)"
              : "0 0 40px rgba(255, 215, 0, 0.19)",
          }}
          bodyStyle={{
            padding: "24px 28px",
            textAlign: isTubal ? "left" : "center",
          }}
        >
          {isTubal ? (
            <>
              {detail.tubalComment && (
                <p
                  style={{
                    margin: "0 0 16px",
                    fontSize: gameFontSize.md,
                    lineHeight: 1.6,
                    color: theme.textBright,
                  }}
                >
                  {detail.tubalComment}
                </p>
              )}
              {metaLine && (
                <p
                  style={{
                    margin: "0 0 8px",
                    fontSize: gameFontSize.nm,
                    letterSpacing: 1,
                    color: "#7ab86a",
                    textTransform: "uppercase",
                  }}
                >
                  {metaLine}
                </p>
              )}
              <blockquote
                style={{
                  margin: 0,
                  padding: "12px 16px",
                  borderLeft: "3px solid #5a8a4a",
                  fontSize: gameFontSize.md,
                  lineHeight: 1.7,
                  fontStyle: "italic",
                  color: theme.textMuted,
                }}
              >
                {detail.quote}
              </blockquote>
            </>
          ) : (
            <>
              {meta?.icon ? (
                <Image
                  src={meta.icon}
                  alt={detail.name}
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
              <h3 style={{ color: theme.gold, margin: "16px 0 12px", fontSize: gameFontSize.lg }}>
                {detail.name}
              </h3>
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
                &ldquo;{detail.quote}&rdquo;
              </p>
              {meta?.note && (
                <p
                  style={{
                    margin: "14px 0 0",
                    color: "#8f8ab0",
                    fontSize: gameFontSize.xs,
                    lineHeight: 1.7,
                    textAlign: "left",
                    borderLeft: "2px solid rgba(143, 138, 176, 0.4)",
                    paddingLeft: 12,
                  }}
                >
                  {meta.note}
                </p>
              )}
            </>
          )}

          {onClose && (
            <button
              type="button"
              onClick={onClose}
              style={{
                marginTop: 20,
                width: "100%",
                padding: "10px 16px",
                fontSize: gameFontSize.sm,
                letterSpacing: 1,
                cursor: "pointer",
                background: isTubal ? "rgba(90, 138, 74, 0.15)" : "rgba(255, 215, 0, 0.12)",
                color: isTubal ? "#7ab86a" : theme.gold,
                border: `1px solid ${isTubal ? "#5a8a4a" : theme.gold}`,
                borderRadius: 3,
              }}
            >
              닫기
            </button>
          )}
        </TextBox>
      </div>
    </div>
  );
}
