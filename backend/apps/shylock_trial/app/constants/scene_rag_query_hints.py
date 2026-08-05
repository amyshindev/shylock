"""Richer English retrieval queries for Tubal's evidence search — appended to
PORTIA_LOGICAL_FLAWS[scene_id] when building the search query, never shown to
the LLM as the flaw explanation itself (that stays exactly as PORTIA_LOGICAL_FLAWS
reads). Same idea as CHOICE_RAG_QUERY_OVERRIDES in choice_folger_context.py: the
abstract flaw description alone doesn't share enough vocabulary with the archaic
or paraphrased passage that actually rebuts it, so this adds concrete
keywords/phrasing close to the target passage's own wording.

Added after compare_embedding_models.py showed all 7 scenes' bare flaw text
missed >half the time (see _docs/compare-embedding-models-result.md) — most
misses were "right theme, wrong wording", not a bad candidate scene.
"""

SCENE_RAG_QUERY_HINTS: dict[str, str] = {
    "portia_opens": (
        "the original bond's exact terms: an equal pound of Antonio's fair "
        "flesh forfeit if not repaid by the appointed day"
    ),
    "bassanio_plea": (
        "Bassanio offers to pay ten times the sum, or Portia herself offers "
        "thrice the money and to tear up the bond"
    ),
    "crowd_jeers": (
        "Antonio spat upon Shylock's Jewish gaberdine coat and called him "
        "misbeliever, cut-throat dog"
    ),
    "jessica_attack": (
        "Lorenzo's letter describing Jessica's plan to elope: the gold and "
        "jewels she readied, the page's disguise she prepared"
    ),
    "hath_not_moment": (
        "Hath not a Jew eyes, hands, organs, senses — if you prick us do we "
        "not bleed, if you wrong us shall we not revenge"
    ),
    "blood_reveal": (
        "the bond gives no jot of blood — cutting the flesh without shedding "
        "one drop of Christian blood"
    ),
    "alien_law_reveal": (
        "the alien law: a foreigner who seeks a citizen's life forfeits half "
        "his goods, and his own life lies in the Duke's mercy"
    ),
}
