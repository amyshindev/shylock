"""Tunable combat / trial balance constants."""

SHYLOCK_DP_START = 50
DP_MAX = 100

SHYLOCK_HP_START = 100
HP_MAX = 100
LOW_HP_THRESHOLD = 30

PORTIA_HP_START = 100
PORTIA_HP_MAX = 100
PORTIA_HP_HIGH_THRESHOLD = 67  # composed strategist — aphoristic, unhurried
PORTIA_HP_LOW_THRESHOLD = 34  # below: authority/procedure only, composure fraying

# Portia damage scales with DP gained on a choice (keep in sync with frontend computePortiaDamage).
PORTIA_DAMAGE_DP_RATIO = 0.55
PORTIA_DAMAGE_MIN = 2
PORTIA_DAMAGE_MAX = 14

# hath_not_moment is a fixed climax scene (no choices) — flat effects applied server-side
# when the scene finishes playing (frontend reads them off the advance response).
# Portia damage sits above the per-choice cap (14): the speech silences the court
# not by argument but by existence.
HATH_NOT_SCENE_DP_GAIN = 30
HATH_NOT_SCENE_HP_COST = 20
HATH_NOT_SCENE_PORTIA_DAMAGE = 20

DP_FOUGHT_TO_END_THRESHOLD = 80
DP_DIGNITY_ENDING_THRESHOLD = 60
DP_SURVIVAL_ENDING_THRESHOLD = 40

SKILL_CROWD_COST = 40

