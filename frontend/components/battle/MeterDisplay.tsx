"use client";

import {
  DP_MAX,
  SHYLOCK_HP_MAX,
} from "@/lib/constants/game-balance";
import { gameFontSize, hudPanelStyle, hudLabelStyle } from "@/styles/text-box";

interface MeterDisplayProps {
  shylockHp: number;
  dp: number;
  hpRecoveryFlash?: number | null;
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

const LEFT_METER_COLUMN_WIDTH = 336;
const LEFT_HUD_INSET = 10;
const LEFT_HUD_TOP = 8;
/** Approx. height of HP + DP bars (used to stack skill panel below). */
const LEFT_METERS_STACK_HEIGHT = 66;

export {
  LEFT_METER_COLUMN_WIDTH,
  LEFT_HUD_INSET,
  LEFT_HUD_TOP,
  LEFT_METERS_STACK_HEIGHT,
};

export function MeterDisplay({ shylockHp, dp, hpRecoveryFlash }: MeterDisplayProps) {
  return (
    <div
      style={{
        position: "absolute",
        top: LEFT_HUD_TOP,
        left: LEFT_HUD_INSET,
        zIndex: 10,
        pointerEvents: "none",
        width: LEFT_METER_COLUMN_WIDTH,
      }}
    >
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          gap: 5,
          position: "relative",
        }}
      >
        {hpRecoveryFlash != null && hpRecoveryFlash > 0 && (
          <div
            className="hp-recovery-flash"
            style={{
              position: "absolute",
              top: -4,
              right: 4,
              zIndex: 12,
              color: "#8dffb0",
              fontSize: gameFontSize.sm,
              fontWeight: 800,
              letterSpacing: 0.6,
              textShadow: "0 0 10px rgba(80, 255, 140, 0.55), 0 2px 4px rgba(0, 0, 0, 0.8)",
            }}
          >
            HP +{hpRecoveryFlash}
          </div>
        )}
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
    </div>
  );
}
