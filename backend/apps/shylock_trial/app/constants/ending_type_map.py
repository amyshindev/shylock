from enum import StrEnum

from shylock_trial.app.constants.game_balance import (
    DP_DIGNITY_ENDING_THRESHOLD,
    DP_FOUGHT_TO_END_THRESHOLD,
    DP_SURVIVAL_ENDING_THRESHOLD,
)


class EndingType(StrEnum):
    RESCUED = "rescued_ending"
    FOUGHT_TO_END = "fought_to_end_ending"
    DIGNITY_KEPT = "dignity_kept_ending"
    SURVIVED = "survived_ending"
    SILENT = "silent_ending"


def resolve_ending_type(*, dp: int, portia_hp: int) -> EndingType:
    """Rescued when Portia's rhetorical HP is depleted; otherwise DP tiers only."""
    if portia_hp <= 0:
        return EndingType.RESCUED
    if dp >= DP_FOUGHT_TO_END_THRESHOLD:
        return EndingType.FOUGHT_TO_END
    if dp >= DP_DIGNITY_ENDING_THRESHOLD:
        return EndingType.DIGNITY_KEPT
    if dp >= DP_SURVIVAL_ENDING_THRESHOLD:
        return EndingType.SURVIVED
    return EndingType.SILENT
