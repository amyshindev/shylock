"""Gold-standard eval set for Tubal's evidence search (search_folger / EvidenceSearchPort).

Each case maps one of Portia's per-scene logical flaws (already used to prompt
Tubal — see app/constants/portia_logical_flaws.py) to the ftln of the actual
seeded play_lines row that should surface when searching the Folger corpus
for a rebuttal.

gold_ftln_anchors are NOT taken from CURATED_EVIDENCE.source_ftln_range —
spot-checking against the live play_lines table showed most of those ranges
are wrong (off by 40 to 640+ ftln units; only gaberdine and jessica lined up).
Anchors here were instead found by full-text search of each evidence item's
`quote` against play_lines.text on the deployed corpus. CURATED_EVIDENCE's
ranges should be fixed separately — they may also be wrong wherever the game
uses them outside of this eval.

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

from shylock_trial.app.constants.portia_logical_flaws import PORTIA_LOGICAL_FLAWS

# How many ftln on either side of an anchor still counts as a hit — a quote
# often spans a few consecutive verse lines, but play_lines stores one row
# per line.
CONTEXT_RADIUS = 3


@dataclass(frozen=True)
class EvidenceSearchEvalCase:
    scene_id: str
    query: str
    gold_evidence_ids: tuple[str, ...]
    gold_ftln_anchors: tuple[int, ...]
    confidence: str  # "verified" | "inferred"

    @property
    def gold_ftln_ranges(self) -> tuple[tuple[int, int], ...]:
        return tuple(
            (anchor - CONTEXT_RADIUS, anchor + CONTEXT_RADIUS)
            for anchor in self.gold_ftln_anchors
        )


EVAL_CASES: tuple[EvidenceSearchEvalCase, ...] = (
    EvidenceSearchEvalCase(
        scene_id="portia_opens",
        query=PORTIA_LOGICAL_FLAWS["portia_opens"],
        gold_evidence_ids=("bond",),
        gold_ftln_anchors=(1003162,),  # "...fair flesh, to be cut off and taken" (declared 1003200-1003220 was wrong)
        confidence="verified",  # portia_opens -> bond_double_standard -> bond
    ),
    EvidenceSearchEvalCase(
        scene_id="bassanio_plea",
        query=PORTIA_LOGICAL_FLAWS["bassanio_plea"],
        gold_evidence_ids=("bassanio_gold",),
        gold_ftln_anchors=(4001218,),  # "I will be bound to pay it ten times o'er" (declared 4001100-4001120 was wrong)
        confidence="verified",  # bassanio_plea -> gold_shame_bribe -> bassanio_gold
    ),
    EvidenceSearchEvalCase(
        scene_id="crowd_jeers",
        query=PORTIA_LOGICAL_FLAWS["crowd_jeers"],
        gold_evidence_ids=("gaberdine",),
        gold_ftln_anchors=(1003122,),  # "And spet upon my Jewish gaberdine" (declared range was correct)
        confidence="verified",  # crowd_jeers -> coat_before_dry -> gaberdine
    ),
    EvidenceSearchEvalCase(
        scene_id="jessica_attack",
        query=PORTIA_LOGICAL_FLAWS["jessica_attack"],
        gold_evidence_ids=("jessica",),
        gold_ftln_anchors=(2004036,),  # "What page's suit she hath in readiness" (declared range was correct)
        confidence="verified",  # jessica_attack -> defend_jessica -> jessica
    ),
    EvidenceSearchEvalCase(
        scene_id="hath_not_moment",
        query=PORTIA_LOGICAL_FLAWS["hath_not_moment"],
        gold_evidence_ids=("hath_not",),
        gold_ftln_anchors=(3001058,),  # "a Jew eyes? Hath not a Jew hands..." (declared 3001300-3001330 was wrong)
        confidence="inferred",
    ),
    EvidenceSearchEvalCase(
        scene_id="blood_reveal",
        query=PORTIA_LOGICAL_FLAWS["blood_reveal"],
        gold_evidence_ids=("blood", "bond_wording"),
        gold_ftln_anchors=(4001339, 4001319),  # both declared ranges (4001900s/4001850s) were wrong
        confidence="inferred",  # both evidence items are on-topic for the "no blood" ruling
    ),
    EvidenceSearchEvalCase(
        scene_id="alien_law_reveal",
        query=PORTIA_LOGICAL_FLAWS["alien_law_reveal"],
        gold_evidence_ids=("alien_law",),
        gold_ftln_anchors=(4001363,),  # "It is enacted in the laws of Venice..." (declared 4002000-4002040 was wrong)
        confidence="inferred",
    ),
)
