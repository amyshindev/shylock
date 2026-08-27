from uuid import uuid4

from shylock_trial.app.constants.portia_prompt import (
    SYSTEM_PROMPT,
    build_scene_dialogue_message,
    build_user_message,
    composure_break_allowed,
)
from shylock_trial.app.dtos.portia_response_dto import PortiaResponsePromptDto
from shylock_trial.app.dtos.scene_dialogue_dto import SceneDialoguePromptDto
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
    # 평범한 씬, 평정심 건강 — 동요 없음.
    assert composure_break_allowed(1, 80) is False
    assert composure_break_allowed(3, 40) is False
    # 평정심이 낮으면 어디서든 동요를 허용.
    assert composure_break_allowed(1, 15) is True
    # 클라이맥스급 씬은 평정심과 무관하게 동요를 허용.
    assert composure_break_allowed(6, 100) is True
    assert composure_break_allowed(7, 100) is True
    assert composure_break_allowed(8, 100) is True


def test_reaction_prompt_restrained_signal_on_ordinary_rebuttal() -> None:
    message = build_user_message(_reaction_prompt(scene_index=1, portia_hp=80))

    assert "평범한 반박 수준" in message
    assert "예외적 순간" not in message


def test_reaction_prompt_allows_crack_on_low_portia_hp() -> None:
    message = build_user_message(_reaction_prompt(scene_index=1, portia_hp=15))

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
    message = build_user_message(_reaction_prompt(portia_hp=30))

    assert "portia_hp=30 (mid" in message
    assert "법조문" in message


def test_reaction_prompt_low_hp_tone() -> None:
    message = build_user_message(_reaction_prompt(portia_hp=15))

    assert "portia_hp=15 (low" in message
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


def test_rescued_ending_instruction_has_no_legal_defeat() -> None:
    # jessica_intervention은 이방인법 판결을 중단시킨다 — 표준적인 "그가
    # 재판에서 진다" 노트를 쓰면 플레이어가 방금 본 것과 정면으로 모순된다.
    message = build_user_message(
        _reaction_prompt(request_type="ending", context="final_ending:rescued_ending")
    )

    assert "halts the alien-law verdict" in message
    assert "Shylock loses the trial per the play" not in message


def test_other_endings_keep_standard_legal_defeat_note() -> None:
    message = build_user_message(
        _reaction_prompt(request_type="ending", context="final_ending:fought_to_end_ending")
    )

    assert "Shylock loses the trial per the play" in message
    assert "halts the alien-law verdict" not in message


def test_reaction_prompt_defaults_to_portia_voice() -> None:
    message = build_user_message(_reaction_prompt())

    assert "포샤 본인의 입으로" in message
    assert "이번 반응은 포샤가 아니라" not in message


def test_reaction_prompt_switches_to_non_portia_reactor() -> None:
    message = build_user_message(
        _reaction_prompt(
            scene_index=2,
            choice_id="gold_refuse_direct",
            context="choice:gold_refuse_direct",
            reactor_speaker="BASSANIO",
            reactor_speaker_label="바사니오",
        )
    )

    assert "이번 반응은 포샤가 아니라 바사니오(BASSANIO)이 말한다" in message
    assert "필사적인 애원조" in message
    # 포샤 전용 장치가 non-Portia 지침 블록으로 새어 들어가면 안 된다.
    assert "판정 회피 원칙" not in message
    assert "포샤 본인의 입으로" not in message


def test_non_portia_reaction_guards_against_wrong_friend_referent() -> None:
    # 로컬 모델이 실제로 "나의 벗"(바사니오 본인의 친구) 대신 "당신의 벗인
    # 안토니오"(안토니오를 샤일록의 친구로)라고 말하는 걸 관측함 — 이
    # 그래프에서 안토니오와 샤일록은 적이므로 거꾸로다.
    message = build_user_message(
        _reaction_prompt(reactor_speaker="BASSANIO", reactor_speaker_label="바사니오")
    )

    assert "나의 벗" in message
    assert "샤일록의 친구가 아니다" in message


def test_non_portia_reaction_drops_composure_gauge() -> None:
    message = build_user_message(
        _reaction_prompt(reactor_speaker="BASSANIO", reactor_speaker_label="바사니오")
    )

    assert "평정심 게이지(portia_hp)는 포샤 전용 장치" in message


def test_non_portia_reaction_still_carries_folger_context() -> None:
    folger_context = "## 원작 맥락 (Folger MV RAG)\n[1.3] BASSANIO: I owe the most in money and in love"
    message = build_user_message(
        _reaction_prompt(
            reactor_speaker="BASSANIO",
            reactor_speaker_label="바사니오",
            folger_context=folger_context,
        )
    )

    assert "I owe the most in money and in love" in message


def test_reaction_prompt_includes_character_context() -> None:
    character_context = "인물 관계 정보:\n- 안토니오가 자신의 재산과 목숨을 바사니오를 위해 내놓는다. (guarantor_for)"
    message = build_user_message(_reaction_prompt(character_context=character_context))

    assert "guarantor_for" in message
    assert "자연스럽게 녹여" in message


def test_non_portia_reaction_includes_character_context() -> None:
    character_context = "인물 관계 정보:\n[바사니오 (Bassanio)] 안토니오의 친구."
    message = build_user_message(
        _reaction_prompt(
            reactor_speaker="BASSANIO",
            reactor_speaker_label="바사니오",
            character_context=character_context,
        )
    )

    assert "안토니오의 친구" in message


def test_reaction_prompt_switches_to_duke_reactor() -> None:
    # trial_progression_interactor._resolve_reactor 참고: REACTOR_OVERRIDE_SCENES
    # (bassanio_plea)가 아닌 모든 씬의 reaction 기본 화자가 이제 공작이다 —
    # BASSANIO와는 별도의 _duke_reaction_instruction 경로를 탄다.
    message = build_user_message(
        _reaction_prompt(reactor_speaker="DUKE", reactor_speaker_label="공작")
    )

    assert "이번 반응은 포샤가 아니라 공작(DUKE)이 말한다" in message
    assert "duke_prompt.py의 공작과 같은" in message
    # 포샤 전용 판정 회피 원칙("그대가 틀렸소" 문구)이 non-Portia 지침
    # 블록으로 새어 들어가면 안 된다 — 공작에게는 별도로 쓴 문구가 있다.
    assert "그대가 틀렸소" not in message
    assert "포샤 본인의 입으로" not in message


def test_duke_reaction_may_use_legal_procedural_reasoning() -> None:
    # BASSANIO 등 애원하는 reactor에게는 "너는 판사가 아니니 법 절차로
    # 근거대지 마라"고 금지하지만, 공작은 실제로 이 법정의 재판장이므로
    # 그 금지가 정확히 거꾸로 적용돼야 한다.
    message = build_user_message(
        _reaction_prompt(reactor_speaker="DUKE", reactor_speaker_label="공작")
    )

    assert "판사가 아니다" not in message
    assert "법 절차·계약 문언·법정의 권위를 근거로 삼는 것이 정확히 공작다운 화법이다" in message


def test_duke_reaction_still_carries_folger_and_character_context() -> None:
    folger_context = "## 원작 맥락 (Folger MV RAG)\n[4.1] DUKE: What, is Antonio here?"
    character_context = "인물 관계 정보:\n[공작 (Duke)] 베네치아 법정을 주재한다."
    message = build_user_message(
        _reaction_prompt(
            reactor_speaker="DUKE",
            reactor_speaker_label="공작",
            folger_context=folger_context,
            character_context=character_context,
        )
    )

    assert "What, is Antonio here?" in message
    assert "베네치아 법정을 주재한다" in message


def test_scene_dialogue_message_includes_shylock_character_context() -> None:
    character_context = (
        "인물 관계 정보:\n[샤일록 (Shylock)] 베니스의 유대인 대금업자. "
        "안토니오에게 살 1파운드를 담보로 돈을 빌려준다.\n"
        "- 샤일록이 안토니오에게 살 1파운드를 담보로 돈을 빌려준다. (creditor_of)"
    )
    message = build_scene_dialogue_message(
        SceneDialoguePromptDto(
            trial_id=uuid4(),
            scene_index=1,
            dp=50,
            choice_history=(),
            character_context=character_context,
        )
    )

    assert "creditor_of" in message
    assert "choice_texts" in message and "샤일록 자신에 대한 참고 인물 관계 정보" in message


def test_scene_dialogue_message_omits_character_context_block_when_empty() -> None:
    message = build_scene_dialogue_message(
        SceneDialoguePromptDto(trial_id=uuid4(), scene_index=1, dp=50, choice_history=())
    )

    assert "샤일록 자신에 대한 참고 인물 관계 정보" not in message


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
