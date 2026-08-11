/**
 * hath_not_moment pauses mid-scene, right on Shylock's "......" beat, to
 * show a single-item panel (the "유대인의 증언" evidence) — visually the
 * same ItemChoiceList every other item-first scene uses, just with one
 * card. Unlike those scenes, selecting it doesn't open a ChoiceList of
 * sub-options or call submitChoice: it jumps straight to "유대인은 눈이
 * 없소?" This is presentational pacing only — hath_not_moment's dp/hp/
 * portia_hp effect is already fixed server-side
 * (_apply_hath_not_scene_effect, applied in trial_progression_interactor's
 * advance_scene) regardless of this click, so there's nothing to submit.
 *
 * hath_not_moment is in the backend's FIXED_SCRIPT_SCENE_IDS (scene_catalog.py)
 * — its lines are authored verbatim and never LLM-rewritten — so atLineIndex
 * hardcoded to this scene's known line order is safe, not fragile against
 * dialogue regeneration the way a normal scene's line index would be.
 */

export interface SceneItemGate {
  /** 0-indexed line where advance() pauses instead of continuing. */
  atLineIndex: number;
  evidenceId: string;
  /** Line jumped to once the item is selected. */
  targetLineIndex: number;
}

export const SCENE_ITEM_GATE_BY_SCENE_ID: Record<string, SceneItemGate> = {
  hath_not_moment: { atLineIndex: 3, evidenceId: "hath_not", targetLineIndex: 4 },
};
