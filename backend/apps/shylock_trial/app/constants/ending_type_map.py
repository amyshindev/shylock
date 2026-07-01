from enum import StrEnum

from shylock_trial.app.constants.game_balance import DP_GOOD_ENDING_THRESHOLD


class EndingType(StrEnum):
    DIGNITY = "dignity_ending"
    BAD = "bad_ending"
    HISTORY_CHANGED = "history_changed_ending"
    SURVIVAL = "survival_ending"


def resolve_ending_type(dp: int, alien_law_executed: bool) -> EndingType:
    good = dp >= DP_GOOD_ENDING_THRESHOLD
    if alien_law_executed:
        return EndingType.DIGNITY if good else EndingType.BAD
    return EndingType.HISTORY_CHANGED if good else EndingType.SURVIVAL
