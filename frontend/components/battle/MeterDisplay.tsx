"use client";

import { theme } from "@/styles/theme";

interface MeterDisplayProps {
  dignity: number;
  confidence: number;
}

function clampMeter(value: number): number {
  return Math.max(0, Math.min(100, value));
}

function dignityColor(value: number): string {
  if (value > 60) return theme.gold;
  if (value > 30) return "#ff8800";
  return "#ff4444";
}

function confidenceColor(value: number): string {
  if (value > 60) return "#44ff88";
  if (value > 30) return "#44aaff";
  return "#ff4444";
}

function MeterBar({
  label,
  value,
  color,
}: {
  label: string;
  value: number;
  color: string;
}) {
  const clamped = clampMeter(value);

  return (
    <div
      style={{
        flex: 1,
        background: "rgba(8, 3, 10, 0.8)",
        borderRadius: 3,
        padding: "6px 10px",
        border: "1px solid #2a1020",
      }}
    >
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          fontSize: 9,
          letterSpacing: 1,
          marginBottom: 3,
        }}
      >
        <span style={{ color: "#5a3a4a" }}>{label}</span>
        <span style={{ color, fontWeight: 700 }}>{clamped}</span>
      </div>
      <div
        style={{
          background: "#1a0814",
          height: 5,
          borderRadius: 2,
          overflow: "hidden",
        }}
      >
        <div
          style={{
            width: `${clamped}%`,
            height: "100%",
            background: `linear-gradient(90deg, ${color}80, ${color})`,
            borderRadius: 2,
            transition: "width 0.5s ease",
            boxShadow: `0 0 6px ${color}60`,
          }}
        />
      </div>
    </div>
  );
}

export function MeterDisplay({ dignity, confidence }: MeterDisplayProps) {
  return (
    <div
      style={{
        position: "absolute",
        top: 12,
        left: 12,
        right: 12,
        display: "flex",
        gap: 12,
        zIndex: 10,
        pointerEvents: "none",
      }}
    >
      <MeterBar
        label="존엄 DIGNITY"
        value={dignity}
        color={dignityColor(dignity)}
      />
      <MeterBar
        label="법정 확신도"
        value={confidence}
        color={confidenceColor(confidence)}
      />
    </div>
  );
}
