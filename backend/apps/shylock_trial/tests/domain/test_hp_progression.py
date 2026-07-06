import pytest

from shylock_trial.app.constants.scene_choices import (
    apply_choice_resources,
    apply_skill_resources,
    compute_choice_dp_gain,
    compute_portia_damage,
    get_choice_effect,
    get_skill_effect,
)
from shylock_trial.domain.value_objects.hp_score_vo import HpScore
from shylock_trial.domain.value_objects.portia_hp_score_vo import PortiaHpScore


def test_hp_score_apply_delta() -> None:
    assert HpScore(50).apply_delta(-20).value == 30
    assert HpScore(10).apply_delta(-20).value == 0


def test_portia_hp_score_apply_delta() -> None:
    assert PortiaHpScore(50).apply_delta(-20).value == 30
    assert PortiaHpScore(10).apply_delta(-20).value == 0


@pytest.mark.parametrize(
    ("hp_before", "dp_delta", "expected_gain"),
    [
        (50, 20, 20),
        (30, 20, 10),
        (25, 21, 10),
        (30, -15, -15),
    ],
)
def test_compute_choice_dp_gain_low_hp_penalty(
    hp_before: int,
    dp_delta: int,
    expected_gain: int,
) -> None:
    gain, shield_consumed = compute_choice_dp_gain(hp_before, dp_delta)
    assert gain == expected_gain
    assert shield_consumed is False


def test_compute_choice_dp_gain_venice_shield() -> None:
    gain, shield_consumed = compute_choice_dp_gain(50, -15, venice_dp_shield=True)
    assert gain == 0
    assert shield_consumed is True


def test_compute_portia_damage_scales_with_dp() -> None:
    assert compute_portia_damage(-25) == 0
    assert compute_portia_damage(-10) == 0
    assert compute_portia_damage(-3) == 1
    assert compute_portia_damage(5) == 3
    assert compute_portia_damage(13) == 7
    assert compute_portia_damage(18) == 10
    assert compute_portia_damage(30) == 14


def test_apply_choice_resources_deducts_hp_and_portia_hp() -> None:
    effect = get_choice_effect("gold_refuse_direct")
    next_hp, next_dp, _, next_portia_hp = apply_choice_resources(
        hp_before=100,
        dp_before=50,
        effect=effect,
        portia_hp_before=100,
    )
    assert next_hp == 94
    assert next_dp == 63
    assert next_portia_hp == 93


def test_apply_skill_resources_launcelot_spends_dp_heals_hp() -> None:
    launcelot = get_skill_effect("launcelot")
    next_hp, next_dp = apply_skill_resources(80, 50, launcelot)
    assert next_hp == 92
    assert next_dp == 42


def test_apply_skill_resources_tubal() -> None:
    tubal = get_skill_effect("tubal")
    next_hp, next_dp = apply_skill_resources(80, 50, tubal)
    assert next_hp == 88
    assert next_dp == 44


def test_apply_skill_resources_venice_paradox() -> None:
    venice = get_skill_effect("venice_paradox")
    next_hp, next_dp = apply_skill_resources(70, 50, venice)
    assert next_hp == 90
    assert next_dp == 36


def test_apply_choice_resources_low_hp_halves_gain() -> None:
    effect = get_choice_effect("hath_not_speech")
    next_hp, next_dp, _, next_portia_hp = apply_choice_resources(
        hp_before=25,
        dp_before=50,
        effect=effect,
        portia_hp_before=100,
    )
    assert next_hp == 5
    assert next_dp == 65
    assert next_portia_hp == 86
