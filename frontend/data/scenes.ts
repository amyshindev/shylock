export type { ChoiceOption, Scene, Speaker } from "@/data/scene-types";

import { SCENE_TEMPLATES } from "@/data/scene-templates";
import { buildFallbackScene } from "@/lib/build-scene";

export { SCENE_TEMPLATES } from "@/data/scene-templates";

/** Fallback-only scenes for tests or offline use. */
export const SCENES = SCENE_TEMPLATES.map(buildFallbackScene);

export const HATH_NOT_QUOTE = `"Hath not a Jew eyes?
Hath not a Jew hands, organs, dimensions,
senses, affections, passions?

If you prick us, do we not bleed?
If you tickle us, do we not laugh?
If you poison us, do we not die?
And if you wrong us, shall we not revenge?"`;

export const TIMING = {
  evidenceModalMs: 2200,
  choiceSequenceMs: 2200,
} as const;
