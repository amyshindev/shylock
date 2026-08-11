"""Gold-standard eval set for Tubal's evidence search (search_folger / EvidenceSearchPort).

Each case maps one of Portia's per-scene logical flaws (already used to prompt
Tubal — see app/constants/portia_logical_flaws.py) to the curated evidence
item(s) that should surface when searching the Folger corpus for a rebuttal.
Gold ftln ranges come straight from CURATED_EVIDENCE.source_ftln_range,
which has been spot-checked against the live play_lines table.

confidence:
- "verified": the scene->evidence link is asserted by game logic itself
  (TUBAL_ENHANCEMENT_MAP -> CHOICE_EVIDENCE), i.e. the designers' own
  ground truth, not a guess.
- "inferred": TUBAL_ENHANCEMENT_MAP[scene_id] is None (no in-game link);
  the evidence_id here was matched by quote/topic content and should be
  sanity-checked by a human before being trusted for scoring.
"""

from __future__ import annotations

from dataclasses import dataclass

from shylock_trial.app.constants.curated_evidence import CURATED_EVIDENCE_BY_ID
from shylock_trial.app.constants.portia_logical_flaws import PORTIA_LOGICAL_FLAWS


@dataclass(frozen=True)
class EvidenceSearchEvalCase:
    scene_id: str
    query: str
    gold_evidence_ids: tuple[str, ...]
    confidence: str  # "verified" | "inferred"

    @property
    def gold_ftln_ranges(self) -> tuple[tuple[int, int], ...]:
        return tuple(
            CURATED_EVIDENCE_BY_ID[evidence_id].source_ftln_range
            for evidence_id in self.gold_evidence_ids
        )


EVAL_CASES: tuple[EvidenceSearchEvalCase, ...] = (
    EvidenceSearchEvalCase(
        scene_id="portia_opens",
        query=PORTIA_LOGICAL_FLAWS["portia_opens"],
        gold_evidence_ids=("bond",),
        confidence="verified",  # portia_opens -> bond_double_standard -> bond
    ),
    EvidenceSearchEvalCase(
        scene_id="bassanio_plea",
        query=PORTIA_LOGICAL_FLAWS["bassanio_plea"],
        gold_evidence_ids=("bassanio_gold",),
        confidence="verified",  # bassanio_plea -> gold_shame_bribe -> bassanio_gold
    ),
    EvidenceSearchEvalCase(
        scene_id="crowd_jeers",
        query=PORTIA_LOGICAL_FLAWS["crowd_jeers"],
        gold_evidence_ids=("gaberdine",),
        confidence="verified",  # crowd_jeers -> coat_before_dry -> gaberdine
    ),
    EvidenceSearchEvalCase(
        scene_id="jessica_attack",
        query=PORTIA_LOGICAL_FLAWS["jessica_attack"],
        gold_evidence_ids=("jessica",),
        confidence="verified",  # jessica_attack -> defend_jessica -> jessica
    ),
    EvidenceSearchEvalCase(
        scene_id="hath_not_moment",
        query=PORTIA_LOGICAL_FLAWS["hath_not_moment"],
        gold_evidence_ids=("hath_not",),
        confidence="inferred",
    ),
    EvidenceSearchEvalCase(
        scene_id="blood_reveal",
        query=PORTIA_LOGICAL_FLAWS["blood_reveal"],
        gold_evidence_ids=("blood", "bond_wording"),
        confidence="inferred",  # both evidence items are on-topic for the "no blood" ruling
    ),
)
