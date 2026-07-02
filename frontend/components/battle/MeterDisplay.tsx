"use client";

import {
  DP_MAX,
  PORTIA_HP_MAX,
  SHYLOCK_HP_MAX,
} from "@/lib/constants/game-balance";
import { gameFontSize, hudPanelStyle, hudLabelStyle } from "@/styles/text-box";

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
  labelColor = "#e8dce4",
}: {
  label: string;
  value: number;
  max: number;
  color: string;
  labelColor?: string;
}) {
  const clamped = Math.max(0, Math.min(max, value));
  const pct = max > 0 ? (clamped / max) * 100 : 0;

  return (
    <div style={hudPanelStyle()}>
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          fontSize: gameFontSize.xs,
          letterSpacing: 0.8,
          marginBottom: 5,
          gap: 6,
        }}
      >
        <span
          style={{
            ...hudLabelStyle(labelColor),
            whiteSpace: "nowrap",
          }}
        >
          {label}
        </span>
        <span
          style={{
            color,
            fontWeight: 700,
            fontSize: gameFontSize.xs,
            textShadow: `0 0 6px ${color}66`,
          }}
        >
          {clamped}/{max}
        </span>
      </div>
      <div
        style={{
          background: "#120810",
          height: 5,
          borderRadius: 2,
          overflow: "hidden",
          border: "1px solid #2a1828",
        }}
      >
        <div
          style={{
            width: `${pct}%`,
            height: "100%",
            background: `linear-gradient(90deg, ${color}99, ${color})`,
            borderRadius: 2,
            transition: "width 0.5s ease",
            boxShadow: `0 0 6px ${color}88`,
          }}
        />
      </div>
    </div>
  );
}

function shylockHpColor(value: number): string {
  const ratio = value / SHYLOCK_HP_MAX;
  if (ratio > 0.5) return "#ff7777";
  if (ratio > 0.25) return "#ff5555";
  return "#ee3333";
}

function dpColor(value: number): string {
  const ratio = value / DP_MAX;
  if (ratio > 0.6) return "#66bbff";
  if (ratio > 0.3) return "#4499ee";
  return "#3388dd";
}

function portiaHpColor(value: number): string {
  const ratio = value / PORTIA_HP_MAX;
  if (ratio > 0.5) return "#ff6666";
  if (ratio > 0.25) return "#ff4444";
  return "#dd3333";
}

const LEFT_METER_COLUMN_WIDTH = 336;
const PORTIA_METER_COLUMN_WIDTH = 336;
const LEFT_HUD_INSET = 10;
const LEFT_HUD_TOP = 8;
/** Approx. height of HP + DP bars (used to stack skill panel below). */
const LEFT_METERS_STACK_HEIGHT = 66;

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
          labelColor="#ffc8c8"
        />
        <MeterBar
          label="DP (존엄)"
          value={dp}
          max={DP_MAX}
          color={dpColor(dp)}
          labelColor="#b8dcff"
        />
      </div>

      <div style={{ width: PORTIA_METER_COLUMN_WIDTH, flexShrink: 0 }}>
        <MeterBar
          label="포샤 HP"
          value={portiaHp}
          max={PORTIA_HP_MAX}
          color={portiaHpColor(portiaHp)}
          labelColor="#ffb8b8"
        />
      </div>
    </div>
  );
}
