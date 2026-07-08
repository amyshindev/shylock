from dataclasses import dataclass

from shylock_trial.app.constants.game_balance import (
    DP_MAX,
    HP_MAX,
    LOW_HP_THRESHOLD,
    PORTIA_DAMAGE_DP_RATIO,
    PORTIA_DAMAGE_MAX,
    PORTIA_DAMAGE_MIN,
    PORTIA_HP_MAX,
)

# Scene progression: see scene_progression.py (indices 0–9).
from shylock_trial.app.constants.scene_progression import (  # noqa: F401
    FINAL_SCENE_INDEX,
    resolve_next_scene_index,
)


@dataclass(frozen=True, slots=True)
class ChoiceEffect:
    dp_delta: int
    hp_cost: int = 0

    @property
    def portia_damage(self) -> int:
        return compute_portia_damage(self.dp_delta)


def compute_portia_damage(dp_delta: int) -> int:
    """Higher DP gains deal more Portia HP damage. Negative DP choices barely scratch Portia."""
    if dp_delta <= 0:
        return 0 if dp_delta <= -5 else 1
    scaled = round(dp_delta * PORTIA_DAMAGE_DP_RATIO)
    return max(PORTIA_DAMAGE_MIN, min(PORTIA_DAMAGE_MAX, scaled))


CHOICE_EFFECTS: dict[str, ChoiceEffect] = {
    "bond_signature": ChoiceEffect(12, 5),
    "bond_double_standard": ChoiceEffect(18, 12),
    "bond_lay_down": ChoiceEffect(5, 3),
    "charter_merchant_trust": ChoiceEffect(16, 8),
    "charter_law_precedent": ChoiceEffect(18, 10),
    "charter_follow_law": ChoiceEffect(10, 4),
    "gold_refuse_direct": ChoiceEffect(13, 6),
    "gold_shame_bribe": ChoiceEffect(18, 12),
    "gold_push_away": ChoiceEffect(6, 3),
    "scales_no_reason": ChoiceEffect(14, 7),
    "scales_humour": ChoiceEffect(18, 11),
    "scales_weigh": ChoiceEffect(8, 4),
    "coat_show_spit": ChoiceEffect(13, 6),
    "coat_before_dry": ChoiceEffect(18, 12),
    "coat_show_silent": ChoiceEffect(6, 3),
    "ghetto_curfew": ChoiceEffect(15, 7),
    "ghetto_who_guilty": ChoiceEffect(18, 11),
    "ghetto_look_silent": ChoiceEffect(8, 4),
    "defend_jessica": ChoiceEffect(15, 12),
    "letter_irrelevant": ChoiceEffect(12, 6),
    "letter_fold_silent": ChoiceEffect(6, 3),
    "ring_leah_gift": ChoiceEffect(18, 12),
    "ring_loss_dignity": ChoiceEffect(15, 8),
    "ring_clutch_silent": ChoiceEffect(8, 4),
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


# All skills convert DP into HP: negative dp_delta spends DP, negative hp_cost heals.
# DP can only be *gained* through scene choices.
SKILL_EFFECTS: dict[str, ChoiceEffect] = {
    "launcelot": ChoiceEffect(-8, -12),
    "tubal": ChoiceEffect(-6, -8),
    "venice_paradox": ChoiceEffect(-14, -20),
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
    "bond_signature": "bond",
    "bond_double_standard": "bond",
    "bond_lay_down": "bond",
    "charter_merchant_trust": "venice_charter",
    "charter_law_precedent": "venice_charter",
    "charter_follow_law": "venice_charter",
    "gold_refuse_direct": "bassanio_gold",
    "gold_shame_bribe": "bassanio_gold",
    "gold_push_away": "bassanio_gold",
    "scales_no_reason": "scales",
    "scales_humour": "scales",
    "scales_weigh": "scales",
    "coat_show_spit": "gaberdine",
    "coat_before_dry": "gaberdine",
    "coat_show_silent": "gaberdine",
    "ghetto_curfew": "ghetto_gate",
    "ghetto_who_guilty": "ghetto_gate",
    "ghetto_look_silent": "ghetto_gate",
    "defend_jessica": "jessica",
    "letter_irrelevant": "jessica",
    "letter_fold_silent": "jessica",
    "ring_leah_gift": "leah_ring",
    "ring_loss_dignity": "leah_ring",
    "ring_clutch_silent": "leah_ring",
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
    portia_hp_before: int = PORTIA_HP_MAX,
    dp_bonus: int = 0,
    venice_dp_shield: bool = False,
) -> tuple[int, int, bool, int]:
    """Return (next_hp, next_dp, shield_consumed, next_portia_hp)."""
    dp_gain, shield_consumed = compute_choice_dp_gain(
        hp_before,
        effect.dp_delta,
        dp_bonus=dp_bonus,
        venice_dp_shield=venice_dp_shield,
    )
    next_hp = max(0, min(HP_MAX, hp_before - effect.hp_cost))
    next_dp = max(0, min(DP_MAX, dp_before + dp_gain))
    next_portia_hp = max(0, min(PORTIA_HP_MAX, portia_hp_before - effect.portia_damage))
    return next_hp, next_dp, shield_consumed, next_portia_hp
