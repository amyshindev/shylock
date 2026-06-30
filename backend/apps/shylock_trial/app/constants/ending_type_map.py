from enum import StrEnum


class EndingType(StrEnum):
    VICTORY = "victory"
    STANDARD_DEFEAT = "standard_defeat"
    SILENT_DEFEAT = "silent_defeat"


VICTORY_DIGNITY_THRESHOLD = 70
STANDARD_DEFEAT_DIGNITY_THRESHOLD = 40


def resolve_ending_type(dignity: int) -> EndingType:
    if dignity >= VICTORY_DIGNITY_THRESHOLD:
        return EndingType.VICTORY
    if dignity >= STANDARD_DEFEAT_DIGNITY_THRESHOLD:
        return EndingType.STANDARD_DEFEAT
    return EndingType.SILENT_DEFEAT
