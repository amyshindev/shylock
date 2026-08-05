"""Tunable combat / trial balance constants."""

SHYLOCK_DP_START = 25
DP_MAX = 100

SHYLOCK_HP_START = 100
HP_MAX = 100
LOW_HP_THRESHOLD = 40

# Lowered from 100 — the max achievable cumulative portia_damage across a full
# playthrough is 70 (see _docs/rebalancing.md / _docs/portia-hp-fix.md). At 70
# the "portia_hp <= 0" rescue branch (jessica_intervention) required literally
# every single choice to be the scene-max one — zero room for error. 65 leaves
# 5 points of slack — a small margin, not a forgiving one: the run only zeroes
# Portia out at the very last choice-scene (blood_reveal's blood_impossible),
# and only one *small* scene slip is recoverable.
PORTIA_HP_START = 65
PORTIA_HP_MAX = 65

# Composure-tone tiers as ratios of PORTIA_HP_MAX (not absolute numbers) so they
# keep the same *proportional* shape — top third composed, bottom third
# fraying — no matter how PORTIA_HP_MAX gets retuned later. Ratios preserved
# from the original 100-scale design (67/100, 34/100).
PORTIA_HP_HIGH_RATIO = 0.67  # composed strategist — aphoristic, unhurried
PORTIA_HP_LOW_RATIO = 0.34  # below: authority/procedure only, composure fraying
PORTIA_HP_HIGH_THRESHOLD = round(PORTIA_HP_MAX * PORTIA_HP_HIGH_RATIO)
PORTIA_HP_LOW_THRESHOLD = round(PORTIA_HP_MAX * PORTIA_HP_LOW_RATIO)

# Portia damage scales with DP gained on a choice (keep in sync with frontend computePortiaDamage).
PORTIA_DAMAGE_DP_RATIO = 0.55
PORTIA_DAMAGE_MIN = 2
PORTIA_DAMAGE_MAX = 14

# hath_not_moment is a fixed climax scene (no choices) — flat effects applied server-side
# when the scene finishes playing (frontend reads them off the advance response).
# Portia damage sits above the per-choice cap (14): the speech silences the court
# not by argument but by existence.
HATH_NOT_SCENE_DP_GAIN = 20
HATH_NOT_SCENE_HP_COST = 26
HATH_NOT_SCENE_PORTIA_DAMAGE = 20

DP_FOUGHT_TO_END_THRESHOLD = 80
DP_DIGNITY_ENDING_THRESHOLD = 60
DP_SURVIVAL_ENDING_THRESHOLD = 40

SKILL_CROWD_COST = 40

