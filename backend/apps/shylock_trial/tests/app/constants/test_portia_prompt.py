from uuid import uuid4

from shylock_trial.app.constants.portia_prompt import build_user_message
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
    assert "NEVER mention blood" in message
    assert "Anti-pattern: do NOT conclude with '자비를 베풀라'" in message


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
