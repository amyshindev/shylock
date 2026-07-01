"use client";

import {
  DP_MAX,
  PORTIA_HP_MAX,
  SHYLOCK_HP_MAX,
} from "@/lib/constants/game-balance";
import { theme } from "@/styles/theme";

interface MeterDisplayProps {
  shylockHp: number;
  dp: number;
  portiaHp: number;
}

function MeterBar({
  label,
  value,
  max,
  color,
}: {
  label: string;
  value: number;
  max: number;
  color: string;
}) {
  const clamped = Math.max(0, Math.min(max, value));
  const pct = max > 0 ? (clamped / max) * 100 : 0;

  return (
    <div
      style={{
        background: "rgba(8, 3, 10, 0.75)",
        borderRadius: 3,
        padding: "4px 9px",
        border: "1px solid #2a1020",
      }}
    >
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          fontSize: 9,
          letterSpacing: 0.8,
          marginBottom: 3,
          gap: 6,
        }}
      >
        <span style={{ color: "#5a3a4a", whiteSpace: "nowrap" }}>{label}</span>
        <span style={{ color, fontWeight: 700, fontSize: 9 }}>
          {clamped}/{max}
        </span>
      </div>
      <div
        style={{
          background: "#1a0814",
          height: 4,
          borderRadius: 2,
          overflow: "hidden",
        }}
      >
        <div
          style={{
            width: `${pct}%`,
            height: "100%",
            background: `linear-gradient(90deg, ${color}80, ${color})`,
            borderRadius: 2,
            transition: "width 0.5s ease",
            boxShadow: `0 0 5px ${color}55`,
          }}
        />
      </div>
    </div>
  );
}

function shylockHpColor(value: number): string {
  const ratio = value / SHYLOCK_HP_MAX;
  if (ratio > 0.5) return "#ff6666";
  if (ratio > 0.25) return "#ff4444";
  return "#cc2222";
}

function dpColor(value: number): string {
  if (value > 60) return theme.gold;
  if (value > 30) return "#ffaa44";
  return "#ff8844";
}

function portiaHpColor(value: number): string {
  const ratio = value / PORTIA_HP_MAX;
  if (ratio > 0.5) return "#44aaff";
  if (ratio > 0.25) return "#3388dd";
  return "#2266bb";
}

const LEFT_METER_COLUMN_WIDTH = 336;
const PORTIA_METER_COLUMN_WIDTH = 336;
const LEFT_HUD_INSET = 10;
const LEFT_HUD_TOP = 8;
/** Approx. height of HP + DP bars (used to stack skill panel below). */
const LEFT_METERS_STACK_HEIGHT = 58;

export {
  LEFT_METER_COLUMN_WIDTH,
  PORTIA_METER_COLUMN_WIDTH,
  LEFT_HUD_INSET,
  LEFT_HUD_TOP,
  LEFT_METERS_STACK_HEIGHT,
};

export function MeterDisplay({ shylockHp, dp, portiaHp }: MeterDisplayProps) {
  return (
    <div
      style={{
        position: "absolute",
        top: LEFT_HUD_TOP,
        left: LEFT_HUD_INSET,
        right: 10,
        display: "flex",
        justifyContent: "space-between",
        alignItems: "flex-start",
        gap: 12,
        zIndex: 10,
        pointerEvents: "none",
      }}
    >
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          gap: 5,
          width: LEFT_METER_COLUMN_WIDTH,
          flexShrink: 0,
        }}
      >
        <MeterBar
          label="HP"
          value={shylockHp}
          max={SHYLOCK_HP_MAX}
          color={shylockHpColor(shylockHp)}
        />
        <MeterBar label="존엄 (DP)" value={dp} max={DP_MAX} color={dpColor(dp)} />
      </div>

      <div style={{ width: PORTIA_METER_COLUMN_WIDTH, flexShrink: 0 }}>
        <MeterBar
          label="포샤 HP"
          value={portiaHp}
          max={PORTIA_HP_MAX}
          color={portiaHpColor(portiaHp)}
        />
      </div>
    </div>
  );
}
