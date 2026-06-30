from dataclasses import dataclass

# Must stay in sync with frontend/data/scenes.ts (from shylock-trial.jsx)
FINAL_SCENE_INDEX = 5


@dataclass(frozen=True, slots=True)
class ChoiceEffect:
    dignity_delta: int
    confidence_delta: int


CHOICE_EFFECTS: dict[str, ChoiceEffect] = {
    "appeal_contract": ChoiceEffect(0, 15),
    "appeal_humanity": ChoiceEffect(20, 5),
    "appeal_mercy": ChoiceEffect(-15, -5),
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
}


def get_choice_effect(choice_id: str) -> ChoiceEffect:
    effect = CHOICE_EFFECTS.get(choice_id)
    if effect is None:
        raise ValueError(f"Unknown choice_id: {choice_id}")
    return effect
