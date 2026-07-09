"use client";

import { useIsMobile } from "@/hooks/use-is-mobile";
import { DP_MAX, HP_MAX, PORTIA_HP_MAX } from "@/lib/constants/game-balance";
import { gameFontSize, hudPanelStyle, hudLabelStyle } from "@/styles/text-box";

interface ShylockMeterDisplayProps {
  dp: number;
  hp: number;
  dpGainFlash?: number | null;
  hpGainFlash?: number | null;
}

interface PortiaMeterDisplayProps {
  portiaHp: number;
}

interface CompactMeterStripProps extends ShylockMeterDisplayProps {
  portiaHp: number;
}

function MeterBar({
  label,
  value,
  max,
  color,
  labelColor = "#e8dce4",
  compact = false,
}: {
  label: string;
  value: number;
  max: number;
  color: string;
  labelColor?: string;
  compact?: boolean;
}) {
  const clamped = Math.max(0, Math.min(max, value));
  const pct = max > 0 ? (clamped / max) * 100 : 0;

  return (
    <div style={compact ? { flex: 1, minWidth: 0 } : hudPanelStyle()}>
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          fontSize: compact ? 10 : gameFontSize.xs,
          letterSpacing: compact ? 0.2 : 0.8,
          marginBottom: compact ? 2 : 5,
          gap: 4,
        }}
      >
        <span
          style={{
            ...hudLabelStyle(labelColor),
            whiteSpace: "nowrap",
            overflow: "hidden",
            textOverflow: "ellipsis",
          }}
        >
          {label}
        </span>
        <span
          style={{
            color,
            fontWeight: 700,
            fontSize: compact ? 10 : gameFontSize.xs,
            textShadow: `0 0 6px ${color}66`,
            flexShrink: 0,
          }}
        >
          {clamped}
        </span>
      </div>
      <div
        style={{
          background: "#120810",
          height: compact ? 3 : 5,
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
  if (ratio > 0.6) return "#e87058";
  if (ratio > 0.3) return "#dd4848";
  return "#c42828";
}

export function portiaHpColor(value: number): string {
  const ratio = value / PORTIA_HP_MAX;
  if (ratio > 0.6) return "#ff6677";
  if (ratio > 0.3) return "#e84455";
  return "#cc2233";
}

const METER_COLUMN_WIDTH = 336;
const METER_COLUMN_WIDTH_MOBILE = 148;
/** Width for skill/item panels in mobile landscape HUD. */
const LANDSCAPE_HUD_RAIL_WIDTH = 132;
/** Width for DP/HP/Portia gauge panels (~1.3× prior compact meter width). */
const LANDSCAPE_METER_WIDTH = 192;
const HUD_INSET = 10;
const HUD_INSET_MOBILE = 8;
const HUD_TOP = 8;
/** Approx. height of DP + HP bars (used to stack skill panel below). */
const LEFT_METERS_STACK_HEIGHT = 72;

export {
  METER_COLUMN_WIDTH as LEFT_METER_COLUMN_WIDTH,
  METER_COLUMN_WIDTH_MOBILE as LEFT_METER_COLUMN_WIDTH_MOBILE,
  LANDSCAPE_HUD_RAIL_WIDTH,
  LANDSCAPE_METER_WIDTH,
  HUD_INSET as LEFT_HUD_INSET,
  HUD_INSET_MOBILE as LEFT_HUD_INSET_MOBILE,
  HUD_TOP as LEFT_HUD_TOP,
  LEFT_METERS_STACK_HEIGHT,
};

/** Landscape left rail: Shylock DP + HP only (Portia sits separately on the top-right). */
export function CompactShylockMeters({
  dp,
  hp,
  dpGainFlash,
  hpGainFlash,
}: ShylockMeterDisplayProps) {
  return (
    <div
      style={{
        ...hudPanelStyle("5px 8px", true),
        display: "flex",
        flexDirection: "column",
        gap: 4,
        flexShrink: 0,
        pointerEvents: "none",
        position: "relative",
        width: LANDSCAPE_METER_WIDTH,
        boxSizing: "border-box",
      }}
    >
      {dpGainFlash != null && (
        <div
          style={{
            position: "absolute",
            top: -2,
            right: 6,
            color: "#88ccff",
            fontSize: 10,
            fontWeight: 700,
            textShadow: "0 0 8px rgba(102, 187, 255, 0.8)",
            animation: "dpGainFlash 1.4s ease-out forwards",
          }}
        >
          +{dpGainFlash}
        </div>
      )}
      <MeterBar
        label="DP"
        value={dp}
        max={DP_MAX}
        color={dpColor(dp)}
        labelColor="#b8dcff"
        compact
      />
      <MeterBar
        label="HP"
        value={hp}
        max={HP_MAX}
        color={hpColor(hp)}
        labelColor="#ffb0a0"
        compact
      />
      {hpGainFlash != null && (
        <div
          style={{
            position: "absolute",
            top: 22,
            right: 6,
            color: "#ff9980",
            fontSize: 10,
            fontWeight: 700,
            textShadow: "0 0 8px rgba(255, 136, 102, 0.8)",
            animation: "dpGainFlash 1.4s ease-out forwards",
          }}
        >
          +{hpGainFlash}
        </div>
      )}
    </div>
  );
}

/** Landscape top-right: Portia HP alone — same width as Shylock meter rail. */
export function CompactPortiaMeter({ portiaHp }: PortiaMeterDisplayProps) {
  return (
    <div
      style={{
        ...hudPanelStyle("5px 8px", true),
        flexShrink: 0,
        pointerEvents: "none",
        width: LANDSCAPE_METER_WIDTH,
        boxSizing: "border-box",
      }}
    >
      <MeterBar
        label="포샤"
        value={portiaHp}
        max={PORTIA_HP_MAX}
        color={portiaHpColor(portiaHp)}
        labelColor="#ffb8c0"
        compact
      />
    </div>
  );
}

/** @deprecated Prefer CompactShylockMeters + CompactPortiaMeter for landscape. */
export function CompactMeterStrip({
  dp,
  hp,
  portiaHp,
  dpGainFlash,
  hpGainFlash,
}: CompactMeterStripProps) {
  return (
    <div
      style={{
        ...hudPanelStyle("5px 8px", true),
        display: "flex",
        gap: 8,
        flexShrink: 0,
        pointerEvents: "none",
        position: "relative",
      }}
    >
      {dpGainFlash != null && (
        <div
          style={{
            position: "absolute",
            top: -2,
            right: 8,
            color: "#88ccff",
            fontSize: 10,
            fontWeight: 700,
            textShadow: "0 0 8px rgba(102, 187, 255, 0.8)",
            animation: "dpGainFlash 1.4s ease-out forwards",
          }}
        >
          +{dpGainFlash}
        </div>
      )}
      <MeterBar
        label="DP"
        value={dp}
        max={DP_MAX}
        color={dpColor(dp)}
        labelColor="#b8dcff"
        compact
      />
      <MeterBar
        label="HP"
        value={hp}
        max={HP_MAX}
        color={hpColor(hp)}
        labelColor="#ffb0a0"
        compact
      />
      <MeterBar
        label="포샤"
        value={portiaHp}
        max={PORTIA_HP_MAX}
        color={portiaHpColor(portiaHp)}
        labelColor="#ffb8c0"
        compact
      />
      {hpGainFlash != null && (
        <div
          style={{
            position: "absolute",
            top: -2,
            left: "38%",
            color: "#ff9980",
            fontSize: 10,
            fontWeight: 700,
            textShadow: "0 0 8px rgba(255, 136, 102, 0.8)",
            animation: "dpGainFlash 1.4s ease-out forwards",
          }}
        >
          +{hpGainFlash}
        </div>
      )}
    </div>
  );
}

export function MeterDisplay({ dp, hp, dpGainFlash, hpGainFlash }: ShylockMeterDisplayProps) {
  const isMobile = useIsMobile();
  const width = isMobile ? METER_COLUMN_WIDTH_MOBILE : METER_COLUMN_WIDTH;
  const inset = isMobile ? HUD_INSET_MOBILE : HUD_INSET;

  return (
    <div
      style={{
        position: "absolute",
        top: HUD_TOP,
        left: inset,
        zIndex: 10,
        pointerEvents: "none",
        width,
        maxWidth: isMobile ? "calc(50vw - 12px)" : undefined,
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
        labelColor="#ffb0a0"
      />
      {hpGainFlash != null && (
        <div
          style={{
            position: "absolute",
            top: 38,
            right: 0,
            color: "#ff9980",
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

export function PortiaMeterDisplay({ portiaHp }: PortiaMeterDisplayProps) {
  const isMobile = useIsMobile();
  const color = portiaHpColor(portiaHp);
  const width = isMobile ? METER_COLUMN_WIDTH_MOBILE : METER_COLUMN_WIDTH;
  const inset = isMobile ? HUD_INSET_MOBILE : HUD_INSET;

  return (
    <div
      style={{
        position: "absolute",
        top: HUD_TOP,
        right: inset,
        zIndex: 10,
        pointerEvents: "none",
        width,
        maxWidth: isMobile ? "calc(50vw - 12px)" : undefined,
      }}
    >
      <MeterBar
        label={isMobile ? "포샤 HP" : "포샤 HP (논리)"}
        value={portiaHp}
        max={PORTIA_HP_MAX}
        color={color}
        labelColor="#ffb8c0"
      />
    </div>
  );
}
