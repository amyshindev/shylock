from enum import StrEnum

from shylock_trial.app.constants.game_balance import DP_GOOD_ENDING_THRESHOLD


class EndingType(StrEnum):
    DIGNITY = "dignity_ending"
    BAD = "bad_ending"
    HISTORY_CHANGED = "history_changed_ending"
    SURVIVAL = "survival_ending"


SHYLOCK_HP_GOOD_ENDING_THRESHOLD = 40


def resolve_ending_type(dp: int, shylock_hp: int) -> EndingType:
    hp_good = shylock_hp >= SHYLOCK_HP_GOOD_ENDING_THRESHOLD
    dp_good = dp >= DP_GOOD_ENDING_THRESHOLD

    if hp_good and dp_good:
        return EndingType.HISTORY_CHANGED
    if hp_good and not dp_good:
        return EndingType.SURVIVAL
    if not hp_good and dp_good:
        return EndingType.DIGNITY
    return EndingType.BAD
