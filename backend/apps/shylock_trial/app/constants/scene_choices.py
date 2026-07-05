from dataclasses import dataclass

from shylock_trial.app.constants.game_balance import DP_MAX, HP_MAX, LOW_HP_THRESHOLD

# Scene progression: see scene_progression.py (indices 0–9).
from shylock_trial.app.constants.scene_progression import (  # noqa: F401
    FINAL_SCENE_INDEX,
    resolve_next_scene_index,
)


@dataclass(frozen=True, slots=True)
class ChoiceEffect:
    dp_delta: int
    hp_cost: int = 0


CHOICE_EFFECTS: dict[str, ChoiceEffect] = {
    "appeal_contract": ChoiceEffect(0, 5),
    "appeal_humanity": ChoiceEffect(20, 15),
    "appeal_mercy": ChoiceEffect(-15, 0),
    "invoke_bond": ChoiceEffect(15, 8),
    "accuse_bassanio": ChoiceEffect(20, 15),
    "cold_silence": ChoiceEffect(-15, 0),
    "show_gaberdine": ChoiceEffect(15, 10),
    "ignore_court": ChoiceEffect(5, 3),
    "rage_at_crowd": ChoiceEffect(-10, 18),
    "defend_jessica": ChoiceEffect(15, 12),
    "reject_private_matter": ChoiceEffect(10, 6),
    "speechless": ChoiceEffect(-20, 0),
    "hath_not_speech": ChoiceEffect(30, 20),
    "bond_only": ChoiceEffect(5, 4),
    "beg_mercy": ChoiceEffect(-20, 5),
    "blood_impossible": ChoiceEffect(15, 10),
    "drop_knife": ChoiceEffect(-10, 0),
    "take_principal_only": ChoiceEffect(5, 3),
    "plead_for_principal": ChoiceEffect(5, 3),
    "reject_conversion": ChoiceEffect(25, 18),
    "bow_accept": ChoiceEffect(-25, 0),
    "mock_mercy": ChoiceEffect(15, 12),
}


SKILL_EFFECTS: dict[str, ChoiceEffect] = {
    "launcelot": ChoiceEffect(-6, -10),
    "tubal": ChoiceEffect(14, 2),
    "venice_paradox": ChoiceEffect(16, 6),
}


def get_skill_effect(skill_id: str) -> ChoiceEffect:
    effect = SKILL_EFFECTS.get(skill_id)
    if effect is None:
        raise ValueError(f"Unknown skill_id: {skill_id}")
    return effect


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
    "plead_for_principal": "bond",
    "reject_conversion": "alien_law",
    "mock_mercy": "alien_law",
}


def get_choice_evidence_id(choice_id: str) -> str | None:
    return CHOICE_EVIDENCE.get(choice_id)


def compute_choice_dp_gain(
    hp_before: int,
    dp_delta: int,
    *,
    dp_bonus: int = 0,
    venice_dp_shield: bool = False,
) -> tuple[int, bool]:
    """Return (dp_gain, shield_consumed). Low HP halves positive gains only."""
    adjusted_delta = dp_delta
    shield_consumed = False
    if venice_dp_shield:
        if adjusted_delta < 0:
            adjusted_delta = 0
        shield_consumed = True

    dp_gain = adjusted_delta + dp_bonus
    if hp_before <= LOW_HP_THRESHOLD and dp_gain > 0:
        dp_gain //= 2
    return dp_gain, shield_consumed


def apply_skill_resources(
    hp_before: int,
    dp_before: int,
    effect: ChoiceEffect,
) -> tuple[int, int]:
    """Return (next_hp, next_dp). Negative hp_cost restores HP."""
    dp_gain, _ = compute_choice_dp_gain(
        hp_before,
        effect.dp_delta,
        venice_dp_shield=False,
    )
    next_hp = max(0, min(HP_MAX, hp_before - effect.hp_cost))
    next_dp = max(0, min(DP_MAX, dp_before + dp_gain))
    return next_hp, next_dp


def apply_choice_resources(
    hp_before: int,
    dp_before: int,
    effect: ChoiceEffect,
    *,
    dp_bonus: int = 0,
    venice_dp_shield: bool = False,
) -> tuple[int, int, bool]:
    """Return (next_hp, next_dp, shield_consumed)."""
    dp_gain, shield_consumed = compute_choice_dp_gain(
        hp_before,
        effect.dp_delta,
        dp_bonus=dp_bonus,
        venice_dp_shield=venice_dp_shield,
    )
    next_hp = max(0, min(HP_MAX, hp_before - effect.hp_cost))
    next_dp = max(0, min(DP_MAX, dp_before + dp_gain))
    return next_hp, next_dp, shield_consumed
