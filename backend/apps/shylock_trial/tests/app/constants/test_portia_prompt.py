from uuid import uuid4

from shylock_trial.app.constants.portia_prompt import (
    SYSTEM_PROMPT,
    build_user_message,
    composure_break_allowed,
)
from shylock_trial.app.dtos.portia_response_dto import PortiaResponsePromptDto
from shylock_trial.domain.entities.trial_entity import TrialPhase


def _reaction_prompt(**overrides) -> PortiaResponsePromptDto:
    defaults = {
        "trial_id": uuid4(),
        "scene_index": 1,
        "dp": 55,
        "phase": TrialPhase.IN_PROGRESS,
        "choice_history": ("bond_signature",),
        "context": "choice:bond_signature",
        "request_type": "reaction",
        "portia_hp": 80,
        "choice_id": "bond_signature",
        "previous_portia_reactions": (),
    }
    defaults.update(overrides)
    return PortiaResponsePromptDto(**defaults)


def test_reaction_prompt_includes_stimulus_and_hp_tone() -> None:
    message = build_user_message(_reaction_prompt())

    assert "Stimulus type: logical" in message
    assert "portia_hp=80 (high" in message
    assert "Anti-pattern: do NOT conclude with '자비를 베풀라'" in message


def test_reaction_prompt_keeps_verdict_avoidance_principle() -> None:
    message = build_user_message(_reaction_prompt())

    assert "판정 회피 원칙" in message
    assert "그대가 틀렸소" in message


def test_reaction_prompt_no_longer_requests_stance_tagging() -> None:
    message = build_user_message(_reaction_prompt())

    assert '"stance"' not in message
    assert "수사적 태도" not in message
    assert 'single "text" field' in message


def test_narration_prompt_keeps_text_only_format() -> None:
    message = build_user_message(
        _reaction_prompt(request_type="narration", context="opening")
    )

    assert '"stance"' not in message
    assert 'single "text" field' in message


def test_system_prompt_carries_portia_persona() -> None:
    assert "noblewoman of Belmont" in SYSTEM_PROMPT
    assert "NEVER mention blood" in SYSTEM_PROMPT
    assert "흠흠" in SYSTEM_PROMPT
    assert "NEVER use it every turn" in SYSTEM_PROMPT


def test_composure_break_allowed_gating() -> None:
    # Ordinary scene, healthy composure — no cracks.
    assert composure_break_allowed(1, 80) is False
    assert composure_break_allowed(3, 40) is False
    # Low composure allows a crack anywhere.
    assert composure_break_allowed(1, 20) is True
    # Climax-weight scenes allow a crack regardless of composure.
    assert composure_break_allowed(6, 100) is True
    assert composure_break_allowed(7, 100) is True
    assert composure_break_allowed(8, 100) is True


def test_reaction_prompt_restrained_signal_on_ordinary_rebuttal() -> None:
    message = build_user_message(_reaction_prompt(scene_index=1, portia_hp=80))

    assert "평범한 반박 수준" in message
    assert "예외적 순간" not in message


def test_reaction_prompt_allows_crack_on_low_portia_hp() -> None:
    message = build_user_message(_reaction_prompt(scene_index=1, portia_hp=20))

    assert "절제가 시험받는 예외적 순간" in message
    assert "평범한 반박 수준" not in message


def test_reaction_prompt_allows_crack_on_climax_scene() -> None:
    message = build_user_message(
        _reaction_prompt(
            scene_index=7,
            portia_hp=80,
            choice_id="wording_letter_turned",
            context="choice:wording_letter_turned",
        )
    )

    assert "절제가 시험받는 예외적 순간" in message


def test_reaction_prompt_includes_previous_reactions() -> None:
    message = build_user_message(
        _reaction_prompt(
            previous_portia_reactions=("법정은 침묵 위에 서 있노라.",),
        )
    )

    assert "do NOT reuse" in message
    assert "법정은 침묵 위에 서 있노라." in message


def test_reaction_prompt_mid_hp_tone() -> None:
    message = build_user_message(_reaction_prompt(portia_hp=50))

    assert "portia_hp=50 (mid" in message
    assert "법조문" in message


def test_reaction_prompt_low_hp_tone() -> None:
    message = build_user_message(_reaction_prompt(portia_hp=20))

    assert "portia_hp=20 (low" in message
    assert "권위" in message


def test_reaction_prompt_silence_stimulus() -> None:
    message = build_user_message(
        _reaction_prompt(
            choice_id="bond_lay_down",
            context="choice:bond_lay_down",
        )
    )

    assert "Stimulus type: silence" in message
    assert "procedural pressure" in message


def test_reaction_prompt_provocation_stimulus() -> None:
    message = build_user_message(
        _reaction_prompt(
            choice_id="gold_shame_bribe",
            context="choice:gold_shame_bribe",
        )
    )

    assert "Stimulus type: provocation" in message


def test_reaction_prompt_includes_folger_context() -> None:
    folger_context = (
        "## 원작 맥락 (Folger MV RAG)\n"
        "[1.3] ANTONIO: spit upon my Jewish gaberdine"
    )
    message = build_user_message(
        _reaction_prompt(
            choice_id="coat_show_spit",
            context="choice:coat_show_spit",
            folger_context=folger_context,
        )
    )

    assert "spit upon my Jewish gaberdine" in message
    assert "원작 맥락" in message
