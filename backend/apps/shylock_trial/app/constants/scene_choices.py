from dataclasses import dataclass

# Must stay in sync with frontend scene-templates (choice stat deltas).
# Scene indices 0–7 (8 scenes).
FINAL_SCENE_INDEX = 7


@dataclass(frozen=True, slots=True)
class ChoiceEffect:
    dp_delta: int
    shylock_hp_delta: int


CHOICE_EFFECTS: dict[str, ChoiceEffect] = {
    "appeal_contract": ChoiceEffect(0, 15),
    "appeal_humanity": ChoiceEffect(20, 5),
    "appeal_mercy": ChoiceEffect(-15, -5),
    "invoke_bond": ChoiceEffect(15, 10),
    "accuse_bassanio": ChoiceEffect(20, -5),
    "cold_silence": ChoiceEffect(-15, 5),
    "show_gaberdine": ChoiceEffect(15, 10),
    "ignore_court": ChoiceEffect(5, 5),
    "rage_at_crowd": ChoiceEffect(-10, -10),
    "defend_jessica": ChoiceEffect(15, 15),
    "reject_private_matter": ChoiceEffect(10, 10),
    "speechless": ChoiceEffect(-20, -15),
    "hath_not_speech": ChoiceEffect(30, 5),
    "bond_only": ChoiceEffect(5, 20),
    "beg_mercy": ChoiceEffect(-20, 0),
    "blood_impossible": ChoiceEffect(15, -10),
    "drop_knife": ChoiceEffect(-10, -20),
    "take_principal_only": ChoiceEffect(5, 10),
    "reject_conversion": ChoiceEffect(25, -20),
    "bow_accept": ChoiceEffect(-25, 15),
    "mock_mercy": ChoiceEffect(15, -5),
}


def get_choice_effect(choice_id: str) -> ChoiceEffect:
    effect = CHOICE_EFFECTS.get(choice_id)
    if effect is None:
        raise ValueError(f"Unknown choice_id: {choice_id}")
    return effect


# Must stay in sync with frontend scene-templates (choice.evidence).
CHOICE_EVIDENCE: dict[str, str] = {
    "appeal_contract": "bond",
    "appeal_humanity": "hath_not",
    "show_gaberdine": "gaberdine",
    "defend_jessica": "jessica",
    "reject_private_matter": "bond",
    "hath_not_speech": "hath_not",
    "bond_only": "bond",
    "blood_impossible": "blood",
    "take_principal_only": "bond",
    "reject_conversion": "alien_law",
    "mock_mercy": "alien_law",
}


def get_choice_evidence_id(choice_id: str) -> str | None:
    return CHOICE_EVIDENCE.get(choice_id)
