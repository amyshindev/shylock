/**
 * Shared next/image quality for large decorative illustrations (scene
 * backgrounds, title art, button plaques) — the source PNGs are raw
 * multi-MB exports; routing them through next/image (fill + sizes) lets
 * Next's built-in optimizer resize + re-encode to avif/webp on the fly
 * instead of shipping the original file straight from /public. Kept as one
 * shared constant (rather than a local per-file const) so every caller
 * requests the exact same optimizer variant for a given source — same
 * reasoning BattleScreen.tsx's NextSceneImagePreload relies on to guarantee
 * a cache hit instead of a second, differently-sized fetch.
 */
export const ILLUSTRATION_IMAGE_QUALITY = 75;
