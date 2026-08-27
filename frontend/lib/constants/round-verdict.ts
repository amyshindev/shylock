/**
 * Duke's per-choice round verdict — a stylized "did this exchange land"
 * ruling, deliberately separate from the trial's actual legal outcome. The
 * backend's resolve_ending_type is still the sole authority on how the game
 * ends (see _docs/ending.md); nothing here can change that.
 *
 * result/line are not computed client-side — they come straight from
 * SubmitChoiceResponse.duke_verdict_result/_line, an LLM judge call the
 * backend makes before applying dp/portia_hp (see
 * trial_progression_interactor._judge_choice). dp/portia_hp on that same
 * response already reflect the verdict; buildRoundVerdict here only decides
 * *whether this scene gets a Duke line at all* — it does no win/lose math.
 *
 * The Duke's line renders as a real dialogue-box reply (speaker tag
 * "DUKE"/"공작", typed like Portia's) ahead of her own reaction — see
 * use-trial-progression.ts's dukeVerdict state / dismissDukeVerdict and
 * BattleScreen.tsx's handlePortiaComplete.
 *
 * Only scenes where the dp delta can actually vary by what the player did
 * are included. That excludes: opening (intro, nothing to judge yet),
 * jessica_intervention (rescue climax, already has its own resolution
 * beat), and — per trial_progression_interactor.advance_scene — jessica_duet
 * and alien_law_reveal, neither of which applies any server-side dp change
 * on advance (only hath_not_moment does, via _apply_hath_not_scene_effect;
 * the "fixed scenes... apply stat effects" framing that once covered
 * jessica_duet too was stale). hath_not_moment stays out too: it has no
 * player-facing choice UI (submit_choice is never called for it, so there's
 * no duke_verdict to show), and its scripted +20 dp already reads as an
 * unambiguous win beat on its own.
 */

export type RoundVerdictResult = "win" | "lose";

export interface RoundVerdict {
  result: RoundVerdictResult;
  line: string;
}

const SCENES_WITH_DUKE_VERDICT = new Set([
  "portia_opens",
  "bassanio_plea",
  "crowd_jeers",
  "jessica_attack",
  "hath_not_moment",
  "blood_reveal",
]);

/** null when sceneId isn't one of the scenes the Duke rules on (see module
 * docstring) — callers should skip straight to Portia's reply in that case. */
export function buildRoundVerdict(
  sceneId: string,
  result: RoundVerdictResult,
  line: string,
): RoundVerdict | null {
  if (!SCENES_WITH_DUKE_VERDICT.has(sceneId)) return null;
  return { result, line };
}
