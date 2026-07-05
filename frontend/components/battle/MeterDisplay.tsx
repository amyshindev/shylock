"use client";

import { DP_MAX, HP_MAX } from "@/lib/constants/game-balance";
import { gameFontSize, hudPanelStyle, hudLabelStyle } from "@/styles/text-box";

interface MeterDisplayProps {
  dp: number;
  hp: number;
  dpGainFlash?: number | null;
  hpGainFlash?: number | null;
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

function dpColor(value: number): string {
  const ratio = value / DP_MAX;
  if (ratio > 0.6) return "#66bbff";
  if (ratio > 0.3) return "#4499ee";
  return "#3388dd";
}

function hpColor(value: number): string {
  const ratio = value / HP_MAX;
  if (ratio > 0.6) return "#ee8866";
  if (ratio > 0.3) return "#dd5544";
  return "#cc3333";
}

const LEFT_METER_COLUMN_WIDTH = 336;
const LEFT_HUD_INSET = 10;
const LEFT_HUD_TOP = 8;
/** Approx. height of DP + HP bars (used to stack skill panel below). */
const LEFT_METERS_STACK_HEIGHT = 72;

export {
  LEFT_METER_COLUMN_WIDTH,
  LEFT_HUD_INSET,
  LEFT_HUD_TOP,
  LEFT_METERS_STACK_HEIGHT,
};

export function MeterDisplay({ dp, hp, dpGainFlash, hpGainFlash }: MeterDisplayProps) {
  return (
    <div
      style={{
        position: "absolute",
        top: LEFT_HUD_TOP,
        left: LEFT_HUD_INSET,
        zIndex: 10,
        pointerEvents: "none",
        width: LEFT_METER_COLUMN_WIDTH,
        display: "flex",
        flexDirection: "column",
        gap: 6,
      }}
    >
      {dpGainFlash != null && (
        <div
          style={{
            position: "absolute",
            top: -4,
            right: 0,
            color: "#88ccff",
            fontSize: gameFontSize.sm,
            fontWeight: 700,
            letterSpacing: 1,
            textShadow: "0 0 8px rgba(102, 187, 255, 0.8)",
            animation: "dpGainFlash 1.4s ease-out forwards",
          }}
        >
          +{dpGainFlash} DP
        </div>
      )}
      <MeterBar
        label="DP (존엄)"
        value={dp}
        max={DP_MAX}
        color={dpColor(dp)}
        labelColor="#b8dcff"
      />
      <MeterBar
        label="HP (기력)"
        value={hp}
        max={HP_MAX}
        color={hpColor(hp)}
        labelColor="#ffc8b8"
      />
      {hpGainFlash != null && (
        <div
          style={{
            position: "absolute",
            top: 38,
            right: 0,
            color: "#ffaa88",
            fontSize: gameFontSize.sm,
            fontWeight: 700,
            letterSpacing: 1,
            textShadow: "0 0 8px rgba(255, 136, 102, 0.8)",
            animation: "dpGainFlash 1.4s ease-out forwards",
          }}
        >
          +{hpGainFlash} HP
        </div>
      )}
    </div>
  );
}
