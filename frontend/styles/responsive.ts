/**
 * Converts a design-reference px value (every HUD component was tuned by
 * eye at a normal fullscreen desktop width) into a clamp() string so it
 * scales with the viewport instead of staying fixed.
 *
 * REFERENCE_VW is the viewport width where the value renders at exactly its
 * original px — i.e. "what it already looks like today" is the scale=1
 * anchor point, not some new arbitrary size. Below/above that width it
 * scales proportionally down to minPx / up to maxPx (defaults: 60%–160% of
 * the reference, generous enough for real window sizes without letting a
 * tiny or huge viewport push it to something absurd).
 */
const REFERENCE_VW = 1512;

export function vwSize(px: number, minPx = px * 0.6, maxPx = px * 1.6): string {
  const vw = (px / REFERENCE_VW) * 100;
  return `clamp(${minPx}px, ${vw.toFixed(3)}vw, ${maxPx}px)`;
}
