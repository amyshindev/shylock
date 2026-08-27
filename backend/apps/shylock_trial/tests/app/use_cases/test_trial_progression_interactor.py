import pytest

from shylock_trial.app.constants.ending_type_map import EndingType
from shylock_trial.app.utils.choice_folger_context import clear_choice_folger_cache


@pytest.fixture(autouse=True)
def _clear_folger_cache() -> None:
    clear_choice_folger_cache()


class FakePortiaUseCase:
    def __init__(self) -> None:
        self.last_prompt = None
        self.scene_dialogue_calls = 0
        self.last_scene_dialogue_prompt = None

    async def generate(self, prompt):
        from shylock_trial.app.dtos.portia_response_dto import PortiaResponseResultDto

        self.last_prompt = prompt
        # 실제 Port 구현체들은 prompt.reactor_speaker/_label을 결과에 그대로
        # 반영한다(portia_response_client.py / ollama_portia_response_
        # client.py 참고) — 테스트가 프롬프트 구성뿐 아니라 submit_choice ->
        # ... -> SubmitChoiceResultDto 전체 배관을 검증하도록 여기서도
        # 똑같이 재현한다.
        return PortiaResponseResultDto(
            text="Portia speaks.",
            fallback_used=False,
            speaker=prompt.reactor_speaker,
            speaker_label=prompt.reactor_speaker_label,
        )

    async def generate_scene_dialogue(self, prompt):
        from shylock_trial.app.constants.scene_catalog import fallback_scene_dialogue
        from shylock_trial.app.dtos.scene_dialogue_dto import SceneDialogueResultDto

        self.scene_dialogue_calls += 1
        self.last_scene_dialogue_prompt = prompt
        return SceneDialogueResultDto(
            content=fallback_scene_dialogue(prompt.scene_index),
            fallback_used=False,
        )


class FakeEvidenceUseCase:
    def __init__(self, scored_lines=()) -> None:
        self.scored_lines = tuple(scored_lines)

    async def search(self, input_dto):
        from shylock_trial.app.dtos.evidence_search_dto import EvidenceSearchResultDto

        return EvidenceSearchResultDto(
            play_lines=tuple(item.play_line for item in self.scored_lines[: input_dto.limit]),
        )

    async def search_scored(self, input_dto):
        from shylock_trial.app.dtos.evidence_search_dto import EvidenceSearchScoredResultDto

        return EvidenceSearchScoredResultDto(
            scored_lines=tuple(self.scored_lines[: input_dto.limit]),
        )

    async def list_curated_evidence(self):
        return []

    async def get_evidence(self, evidence_id: str):
        return None

    async def get_line_context(self, ftln_start: int, ftln_end: int, radius: int = 2):
        return []

    async def get_lines_by_topic(self, topic_id: str):
        return []


class FakeTubalEnhancementClient:
    async def generate_enhanced_choice(
        self,
        passage: str,
        original_choice: str,
        scene_id: str,
        speaker: str,
    ) -> str:
        return original_choice


class FakeDukeVerdictUseCase:
    """기본값은 WIN — 공작 판정자가 생기기 전에 작성된 기존 dp/hp/portia_hp
    assert들이 계속 "선택지에 설계된 ChoiceEffect가 그대로 적용됐다"고
    검증하도록 한다. LOSE 경로는 아래
    test_duke_verdict_lose_zeroes_dp_and_portia_damage 참고."""

    def __init__(self, result: str = "win", line: str = "판결.") -> None:
        self._result = result
        self._line = line
        self.last_prompt = None

    async def judge(self, prompt):
        from shylock_trial.app.dtos.duke_verdict_dto import DukeVerdictResultDto

        self.last_prompt = prompt
        return DukeVerdictResultDto(result=self._result, line=self._line)


class FakeCharacterRelationUseCase:
    """기본값은 빈 그래프로, NullCharacterRelationRepository와 대응된다 —
    여기 있는 대부분의 테스트는 character_context에 신경 쓰지 않고,
    명시적으로 그걸 assert하는 테스트만(test_portia_prompt.py 참고) 노드를
    구성한다."""

    def __init__(
        self,
        nodes: dict[str, object] | None = None,
        relations_by_character: dict[str, list] | None = None,
    ) -> None:
        self._nodes = nodes or {}
        self._relations_by_character = relations_by_character or {}

    async def get_character(self, character_id: str):
        return self._nodes.get(character_id)

    async def list_characters(self):
        return list(self._nodes.values())

    async def get_relations_for(self, character_id: str):
        return list(self._relations_by_character.get(character_id, []))

    async def trace_relationship(self, from_character_id, to_character_id, max_hops=4):
        return []


class InMemoryTrialPort:
    def __init__(self) -> None:
        self._store = {}

    async def create(self, trial):
        self._store[trial.trial_id] = trial
        return trial

    async def save(self, trial):
        self._store[trial.trial_id] = trial
        return trial

    async def find_by_id(self, trial_id):
        return self._store.get(trial_id)

    async def list_by_user_id(self, user_id):
        return [t for t in self._store.values() if t.user_id == user_id]


@pytest.mark.asyncio
async def test_start_trial_returns_scene_dialogue() -> None:
    from shylock_trial.app.constants.game_balance import PORTIA_HP_START
    from shylock_trial.app.use_cases.trial_progression_interactor import TrialProgressionInteractor

    interactor = TrialProgressionInteractor(
        port=InMemoryTrialPort(),
        portia=FakePortiaUseCase(),
        evidence=FakeEvidenceUseCase(),
        tubal_enhancement=FakeTubalEnhancementClient(),
        duke=FakeDukeVerdictUseCase(),
        characters=FakeCharacterRelationUseCase(),
    )
    result = await interactor.start()

    assert result.scene_dialogue.lines
    assert result.phase.value == "in_progress"
    assert result.hp == 100
    assert result.portia_hp == PORTIA_HP_START


@pytest.mark.asyncio
async def test_submit_choice_deducts_hp_and_applies_dp() -> None:
    from shylock_trial.app.constants.game_balance import (
        PORTIA_HP_START,
        SHYLOCK_DP_START,
        SHYLOCK_HP_START,
    )
    from shylock_trial.app.dtos.trial_progression_dto import SubmitChoiceInputDto
    from shylock_trial.app.use_cases.trial_progression_interactor import TrialProgressionInteractor

    interactor = TrialProgressionInteractor(
        port=InMemoryTrialPort(),
        portia=FakePortiaUseCase(),
        evidence=FakeEvidenceUseCase(),
        tubal_enhancement=FakeTubalEnhancementClient(),
        duke=FakeDukeVerdictUseCase(),
        characters=FakeCharacterRelationUseCase(),
    )
    started = await interactor.start()
    choice = await interactor.submit_choice(
        SubmitChoiceInputDto(trial_id=started.trial_id, choice_id="gold_refuse_direct"),
    )

    assert started.hp == SHYLOCK_HP_START
    assert choice.hp == SHYLOCK_HP_START - 9
    assert choice.dp == SHYLOCK_DP_START + 13
    assert started.portia_hp == PORTIA_HP_START
    assert choice.portia_hp == PORTIA_HP_START - 7


@pytest.mark.asyncio
async def test_bassanio_plea_reaction_is_voiced_by_bassanio() -> None:
    from shylock_trial.app.constants.scene_progression import BASSANIO_PLEA_SCENE_INDEX
    from shylock_trial.app.dtos.trial_progression_dto import SubmitChoiceInputDto
    from shylock_trial.app.use_cases.trial_progression_interactor import TrialProgressionInteractor

    portia = FakePortiaUseCase()
    interactor = TrialProgressionInteractor(
        port=InMemoryTrialPort(),
        portia=portia,
        evidence=FakeEvidenceUseCase(),
        tubal_enhancement=FakeTubalEnhancementClient(),
        duke=FakeDukeVerdictUseCase(),
        characters=FakeCharacterRelationUseCase(),
    )
    started = await interactor.start_dev_scene(BASSANIO_PLEA_SCENE_INDEX, 50)
    choice = await interactor.submit_choice(
        SubmitChoiceInputDto(trial_id=started.trial_id, choice_id="gold_refuse_direct"),
    )

    assert portia.last_prompt.reactor_speaker == "BASSANIO"
    assert portia.last_prompt.reactor_speaker_label == "바사니오"
    assert choice.portia_response_speaker == "BASSANIO"
    assert choice.portia_response_speaker_label == "바사니오"


@pytest.mark.asyncio
async def test_crowd_jeers_reaction_still_voiced_by_duke() -> None:
    # crowd_jeers는 아직 REACTOR_OVERRIDE_SCENES에 없다 — 의도적으로 추가되기
    # 전까지는 다른 opt-in되지 않은 씬들과 마찬가지로 이 씬 자체의 화자(CROWD)
    # 가 reactor override로 새어 들어가면 안 되고, reaction의 기본 화자인
    # 공작(DUKE) 그대로 나가야 한다 — bassanio_plea만 예외.
    from shylock_trial.app.constants.scene_progression import CROWD_JEERS_SCENE_INDEX
    from shylock_trial.app.dtos.trial_progression_dto import SubmitChoiceInputDto
    from shylock_trial.app.use_cases.trial_progression_interactor import TrialProgressionInteractor

    portia = FakePortiaUseCase()
    interactor = TrialProgressionInteractor(
        port=InMemoryTrialPort(),
        portia=portia,
        evidence=FakeEvidenceUseCase(),
        tubal_enhancement=FakeTubalEnhancementClient(),
        duke=FakeDukeVerdictUseCase(),
        characters=FakeCharacterRelationUseCase(),
    )
    started = await interactor.start_dev_scene(CROWD_JEERS_SCENE_INDEX, 50)
    choice = await interactor.submit_choice(
        SubmitChoiceInputDto(trial_id=started.trial_id, choice_id="coat_show_spit"),
    )

    assert portia.last_prompt.reactor_speaker == "DUKE"
    assert choice.portia_response_speaker == "DUKE"
    assert choice.portia_response_speaker_label == "공작"


@pytest.mark.asyncio
async def test_bassanio_plea_character_context_includes_his_relations() -> None:
    from shylock_trial.app.constants.scene_progression import BASSANIO_PLEA_SCENE_INDEX
    from shylock_trial.app.dtos.trial_progression_dto import SubmitChoiceInputDto
    from shylock_trial.app.use_cases.trial_progression_interactor import TrialProgressionInteractor
    from shylock_trial.domain.entities.character_relation_entity import (
        CharacterNode,
        CharacterRelation,
    )

    bassanio_node = CharacterNode(
        character_id="bassanio",
        name_ko="바사니오",
        name_en="Bassanio",
        description="안토니오의 친구. 포샤에게 구혼하기 위해 안토니오의 돈이 필요하다.",
    )
    friendship = CharacterRelation(
        from_character_id="bassanio",
        relation_type="financed_by",
        to_character_id="antonio",
        description="바사니오가 안토니오에게 갚아야 할 빚이 있음을 인정한다.",
        evidence_ftln_start=1001138,
        evidence_ftln_end=1001141,
    )
    portia = FakePortiaUseCase()
    interactor = TrialProgressionInteractor(
        port=InMemoryTrialPort(),
        portia=portia,
        evidence=FakeEvidenceUseCase(),
        tubal_enhancement=FakeTubalEnhancementClient(),
        duke=FakeDukeVerdictUseCase(),
        characters=FakeCharacterRelationUseCase(
            nodes={"bassanio": bassanio_node},
            relations_by_character={"bassanio": [friendship]},
        ),
    )
    started = await interactor.start_dev_scene(BASSANIO_PLEA_SCENE_INDEX, 50)
    await interactor.submit_choice(
        SubmitChoiceInputDto(trial_id=started.trial_id, choice_id="gold_refuse_direct"),
    )

    assert "바사니오가 안토니오에게 갚아야 할 빚이 있음을 인정한다" in portia.last_prompt.character_context
    # 바사니오는 숨길 게 없다 — 자기 자신의 노드 설명을 포함해도 안전하다.
    assert "안토니오의 친구" in portia.last_prompt.character_context


@pytest.mark.asyncio
async def test_scene_dialogue_generation_includes_shylock_character_context() -> None:
    """choice_texts는 샤일록 본인의 말이라, 씬 대사 생성 프롬프트에도 그의
    character_relation 그래프 컨텍스트가 실려야 한다 — "이 증서는 내게
    생사가 걸린 약속"처럼 이해관계 당사자를 뒤바꿔 지어내는 걸 막기 위한
    grounding(portia_prompt.py의 _shylock_character_context_instruction
    참고)."""
    from shylock_trial.app.use_cases.trial_progression_interactor import TrialProgressionInteractor
    from shylock_trial.domain.entities.character_relation_entity import (
        CharacterNode,
        CharacterRelation,
    )

    shylock_node = CharacterNode(
        character_id="shylock",
        name_ko="샤일록",
        name_en="Shylock",
        description="베니스의 유대인 대금업자. 안토니오에게 살 1파운드를 담보로 돈을 빌려준다.",
    )
    creditor_relation = CharacterRelation(
        from_character_id="shylock",
        relation_type="creditor_of",
        to_character_id="antonio",
        description="샤일록이 안토니오에게 살 1파운드를 담보로 돈을 빌려준다.",
        evidence_ftln_start=1003158,
        evidence_ftln_end=1003165,
    )
    portia = FakePortiaUseCase()
    interactor = TrialProgressionInteractor(
        port=InMemoryTrialPort(),
        portia=portia,
        evidence=FakeEvidenceUseCase(),
        tubal_enhancement=FakeTubalEnhancementClient(),
        duke=FakeDukeVerdictUseCase(),
        characters=FakeCharacterRelationUseCase(
            nodes={"shylock": shylock_node},
            relations_by_character={"shylock": [creditor_relation]},
        ),
    )

    await interactor.start()

    assert portia.last_scene_dialogue_prompt is not None
    assert "안토니오에게 살 1파운드를 담보로 돈을 빌려준다" in portia.last_scene_dialogue_prompt.character_context


# 포샤 자신의 married_to 관계 숨김 필터링 테스트는
# tests/app/utils/test_character_context.py로 옮겨감 — reaction의 기본
# 화자가 공작으로 바뀌면서(_resolve_reactor 참고) submit_choice로는 더 이상
# 포샤를 reaction의 reactor로 부를 수 없어서, build_character_context를
# 직접 검증하는 게 더 정확해졌다.


@pytest.mark.asyncio
async def test_launcelot_skill_applies_dp_and_hp() -> None:
    from shylock_trial.app.constants.game_balance import (
        HP_MAX,
        SHYLOCK_DP_START,
        SHYLOCK_HP_START,
    )
    from shylock_trial.app.constants.scene_choices import get_skill_effect
    from shylock_trial.app.use_cases.trial_progression_interactor import TrialProgressionInteractor

    effect = get_skill_effect("launcelot")
    interactor = TrialProgressionInteractor(
        port=InMemoryTrialPort(),
        portia=FakePortiaUseCase(),
        evidence=FakeEvidenceUseCase(),
        tubal_enhancement=FakeTubalEnhancementClient(),
        duke=FakeDukeVerdictUseCase(),
        characters=FakeCharacterRelationUseCase(),
    )
    started = await interactor.start()
    result = await interactor.use_launcelot_skill(started.trial_id)

    assert result.dp == SHYLOCK_DP_START + effect.dp_delta
    assert result.hp == min(HP_MAX, SHYLOCK_HP_START - effect.hp_cost)


@pytest.mark.asyncio
async def test_venice_paradox_skill_after_crowd_jeers() -> None:
    from shylock_trial.app.constants.game_balance import (
        HP_MAX,
        SHYLOCK_DP_START,
        SHYLOCK_HP_START,
    )
    from shylock_trial.app.constants.scene_progression import CROWD_JEERS_SCENE_INDEX
    from shylock_trial.app.constants.scene_choices import get_skill_effect
    from shylock_trial.app.use_cases.trial_progression_interactor import TrialProgressionInteractor

    effect = get_skill_effect("venice_paradox")
    interactor = TrialProgressionInteractor(
        port=InMemoryTrialPort(),
        portia=FakePortiaUseCase(),
        evidence=FakeEvidenceUseCase(),
        tubal_enhancement=FakeTubalEnhancementClient(),
        duke=FakeDukeVerdictUseCase(),
        characters=FakeCharacterRelationUseCase(),
    )
    started = await interactor.start_dev_scene(CROWD_JEERS_SCENE_INDEX + 1, SHYLOCK_DP_START)
    skill = await interactor.use_venice_paradox_skill(started.trial_id)

    assert skill.venice_paradox_used is True
    assert skill.dp == SHYLOCK_DP_START + effect.dp_delta
    assert skill.hp == min(HP_MAX, SHYLOCK_HP_START - effect.hp_cost)


@pytest.mark.asyncio
async def test_venice_paradox_skill_rejects_before_crowd_jeers() -> None:
    from shylock_trial.app.constants.scene_progression import CROWD_JEERS_SCENE_INDEX
    from shylock_trial.app.use_cases.trial_progression_interactor import TrialProgressionInteractor

    interactor = TrialProgressionInteractor(
        port=InMemoryTrialPort(),
        portia=FakePortiaUseCase(),
        evidence=FakeEvidenceUseCase(),
        tubal_enhancement=FakeTubalEnhancementClient(),
        duke=FakeDukeVerdictUseCase(),
        characters=FakeCharacterRelationUseCase(),
    )
    started = await interactor.start_dev_scene(CROWD_JEERS_SCENE_INDEX, 50)

    with pytest.raises(ValueError, match="skill_unavailable"):
        await interactor.use_venice_paradox_skill(started.trial_id)


@pytest.mark.asyncio
async def test_venice_paradox_skill_is_one_time() -> None:
    from shylock_trial.app.constants.scene_progression import CROWD_JEERS_SCENE_INDEX
    from shylock_trial.app.use_cases.trial_progression_interactor import TrialProgressionInteractor

    interactor = TrialProgressionInteractor(
        port=InMemoryTrialPort(),
        portia=FakePortiaUseCase(),
        evidence=FakeEvidenceUseCase(),
        tubal_enhancement=FakeTubalEnhancementClient(),
        duke=FakeDukeVerdictUseCase(),
        characters=FakeCharacterRelationUseCase(),
    )
    started = await interactor.start_dev_scene(CROWD_JEERS_SCENE_INDEX + 1, 50)
    await interactor.use_venice_paradox_skill(started.trial_id)

    with pytest.raises(ValueError, match="skill_unavailable"):
        await interactor.use_venice_paradox_skill(started.trial_id)


@pytest.mark.asyncio
async def test_jessica_duet_scene_uses_fixed_script_without_llm() -> None:
    from shylock_trial.app.constants.scene_progression import JESSICA_DUET_SCENE_INDEX
    from shylock_trial.app.use_cases.trial_progression_interactor import TrialProgressionInteractor

    portia = FakePortiaUseCase()
    interactor = TrialProgressionInteractor(
        port=InMemoryTrialPort(),
        portia=portia,
        evidence=FakeEvidenceUseCase(),
        tubal_enhancement=FakeTubalEnhancementClient(),
        duke=FakeDukeVerdictUseCase(),
        characters=FakeCharacterRelationUseCase(),
    )
    started = await interactor.start_dev_scene(JESSICA_DUET_SCENE_INDEX - 1, 50)
    result = await interactor.advance_scene(started.trial_id)

    assert result.scene_index == JESSICA_DUET_SCENE_INDEX
    assert portia.scene_dialogue_calls == 0
    speeches = [line.text for line in result.scene_dialogue.lines]
    assert "악사들을 불러 음악을 청하지. 그럼 마음이 좀 놓일 거야." in speeches
    assert result.scene_dialogue.challenge_text is None
    assert result.scene_dialogue.choice_text_map() == {}
    speakers = [line.speaker for line in result.scene_dialogue.lines]
    assert speakers[0] == "NARRATOR"
    assert "LORENZO" in speakers
    assert "JESSICA" in speakers


@pytest.mark.asyncio
async def test_hath_not_scene_uses_fixed_script_without_llm() -> None:
    from shylock_trial.app.constants.scene_progression import (
        HATH_NOT_SCENE_INDEX,
        JESSICA_DUET_SCENE_INDEX,
    )
    from shylock_trial.app.constants.game_balance import PORTIA_HP_START
    from shylock_trial.app.use_cases.trial_progression_interactor import TrialProgressionInteractor

    portia = FakePortiaUseCase()
    interactor = TrialProgressionInteractor(
        port=InMemoryTrialPort(),
        portia=portia,
        evidence=FakeEvidenceUseCase(),
        tubal_enhancement=FakeTubalEnhancementClient(),
        duke=FakeDukeVerdictUseCase(),
        characters=FakeCharacterRelationUseCase(),
    )
    started = await interactor.start_dev_scene(JESSICA_DUET_SCENE_INDEX, 50)
    result = await interactor.advance_scene(started.trial_id)

    assert result.scene_index == HATH_NOT_SCENE_INDEX
    assert portia.scene_dialogue_calls == 0
    speeches = [line.text for line in result.scene_dialogue.lines]
    assert "유대인은 눈이 없소?" in speeches
    assert "...그때, 저 사람은 아무 소리도 내지 않았었지." in speeches
    assert result.scene_dialogue.challenge_text is None
    assert result.scene_dialogue.choice_text_map() == {}
    speakers = [line.speaker for line in result.scene_dialogue.lines]
    assert speakers[0] == "PORTIA"
    assert "SHYLOCK" in speakers
    # 안토니오 컷이 포샤의 마지막 대사 뒤 씬을 마무리한다.
    assert speakers[-3:] == ["NARRATOR", "ANTONIO", "NARRATOR"]
    # 씬에 진입하는 것 자체는 비용이 없다 — 효과는 씬이 끝날 때 적용된다.
    assert result.dp == 50
    assert result.hp == 100
    assert result.portia_hp == PORTIA_HP_START


@pytest.mark.asyncio
async def test_advancing_past_hath_not_scene_applies_fixed_effect() -> None:
    from shylock_trial.app.constants.game_balance import (
        HATH_NOT_SCENE_DP_GAIN,
        HATH_NOT_SCENE_HP_COST,
        HATH_NOT_SCENE_PORTIA_DAMAGE,
        PORTIA_HP_START,
    )
    from shylock_trial.app.constants.scene_progression import HATH_NOT_SCENE_INDEX
    from shylock_trial.app.use_cases.trial_progression_interactor import TrialProgressionInteractor

    port = InMemoryTrialPort()
    interactor = TrialProgressionInteractor(
        port=port,
        portia=FakePortiaUseCase(),
        evidence=FakeEvidenceUseCase(),
        tubal_enhancement=FakeTubalEnhancementClient(),
        duke=FakeDukeVerdictUseCase(),
        characters=FakeCharacterRelationUseCase(),
    )
    started = await interactor.start_dev_scene(HATH_NOT_SCENE_INDEX, 50)
    result = await interactor.advance_scene(started.trial_id)

    assert result.scene_index == HATH_NOT_SCENE_INDEX + 1
    assert result.dp == 50 + HATH_NOT_SCENE_DP_GAIN
    assert result.hp == 100 - HATH_NOT_SCENE_HP_COST
    assert result.portia_hp == PORTIA_HP_START - HATH_NOT_SCENE_PORTIA_DAMAGE
    trial = await port.find_by_id(started.trial_id)
    assert "hath_not" in trial.presented_evidence


@pytest.mark.asyncio
async def test_submit_choice_passes_reaction_history_to_next_prompt() -> None:
    from shylock_trial.app.dtos.trial_progression_dto import SubmitChoiceInputDto
    from shylock_trial.app.use_cases.trial_progression_interactor import TrialProgressionInteractor

    portia = FakePortiaUseCase()
    port = InMemoryTrialPort()
    interactor = TrialProgressionInteractor(
        port=port,
        portia=portia,
        evidence=FakeEvidenceUseCase(),
        tubal_enhancement=FakeTubalEnhancementClient(),
        duke=FakeDukeVerdictUseCase(),
        characters=FakeCharacterRelationUseCase(),
    )
    started = await interactor.start()
    await interactor.submit_choice(
        SubmitChoiceInputDto(trial_id=started.trial_id, choice_id="gold_refuse_direct"),
    )

    assert portia.last_prompt.previous_portia_reactions == ()

    await interactor.submit_choice(
        SubmitChoiceInputDto(trial_id=started.trial_id, choice_id="bond_signature"),
    )

    assert portia.last_prompt.previous_portia_reactions == ("Portia speaks.",)
    trial = await port.find_by_id(started.trial_id)
    assert trial.portia_reactions == ["Portia speaks.", "Portia speaks."]


@pytest.mark.asyncio
async def test_duke_verdict_lose_zeroes_dp_and_portia_damage() -> None:
    """bold 선택지에 대한 LOSE는 그 선택지가 원래 주기로 설계된 이득과 포샤
    피해를 0으로 만든다 — 하지만 hp_cost는 그대로 적용된다(submit_choice의
    is_bold/landed 주석 참고: 논쟁은 먹히지 않아도 샤일록에게 대가를
    치르게 한다)."""
    from shylock_trial.app.constants.game_balance import (
        PORTIA_HP_START,
        SHYLOCK_DP_START,
        SHYLOCK_HP_START,
    )
    from shylock_trial.app.dtos.trial_progression_dto import SubmitChoiceInputDto
    from shylock_trial.app.use_cases.trial_progression_interactor import TrialProgressionInteractor

    interactor = TrialProgressionInteractor(
        port=InMemoryTrialPort(),
        portia=FakePortiaUseCase(),
        evidence=FakeEvidenceUseCase(),
        tubal_enhancement=FakeTubalEnhancementClient(),
        duke=FakeDukeVerdictUseCase(result="lose", line="기각하오."),
        characters=FakeCharacterRelationUseCase(),
    )
    started = await interactor.start()
    choice = await interactor.submit_choice(
        SubmitChoiceInputDto(trial_id=started.trial_id, choice_id="gold_refuse_direct"),
    )

    assert choice.dp == SHYLOCK_DP_START  # dp_delta (13) zeroed by the LOSE
    assert choice.hp == SHYLOCK_HP_START - 9  # hp_cost still paid
    assert choice.portia_hp == PORTIA_HP_START  # portia_damage (7) zeroed by the LOSE
    assert choice.duke_verdict_result == "lose"
    assert choice.duke_verdict_line == "기각하오."


@pytest.mark.asyncio
async def test_concede_choice_skips_duke_judge_but_still_applies_penalty() -> None:
    """dp_delta <= 0인 선택지(concede/silent)는 LLM 판정자를 거치지 않는다 —
    _judge_choice가 여기서 short-circuit된다 — 하지만 (음수) 효과는 그대로
    전부 적용되며, 이때 받는 결정론적 "lose" 판정은 배너 표시용일 뿐이다."""
    from shylock_trial.app.constants.duke_prompt import CONCEDE_LOSE_LINE
    from shylock_trial.app.constants.game_balance import SHYLOCK_DP_START, SHYLOCK_HP_START
    from shylock_trial.app.dtos.trial_progression_dto import SubmitChoiceInputDto
    from shylock_trial.app.use_cases.trial_progression_interactor import TrialProgressionInteractor

    duke = FakeDukeVerdictUseCase()
    interactor = TrialProgressionInteractor(
        port=InMemoryTrialPort(),
        portia=FakePortiaUseCase(),
        evidence=FakeEvidenceUseCase(),
        tubal_enhancement=FakeTubalEnhancementClient(),
        duke=duke,
        characters=FakeCharacterRelationUseCase(),
    )
    started = await interactor.start()
    choice = await interactor.submit_choice(
        SubmitChoiceInputDto(trial_id=started.trial_id, choice_id="bond_lay_down"),
    )

    assert duke.last_prompt is None  # judge() never called
    assert choice.dp == SHYLOCK_DP_START - 8
    assert choice.hp == SHYLOCK_HP_START
    assert choice.duke_verdict_result == "lose"
    assert choice.duke_verdict_line == CONCEDE_LOSE_LINE


@pytest.mark.asyncio
async def test_submit_choice_passes_folger_context_to_portia() -> None:
    from shylock_trial.app.constants.scene_progression import CROWD_JEERS_SCENE_INDEX
    from shylock_trial.app.dtos.evidence_search_dto import ScoredPlayLine
    from shylock_trial.app.dtos.trial_progression_dto import SubmitChoiceInputDto
    from shylock_trial.app.use_cases.trial_progression_interactor import TrialProgressionInteractor
    from shylock_trial.domain.entities.play_line_entity import PlayLine

    portia = FakePortiaUseCase()
    gaberdine_line = PlayLine(
        ftln=1003120,
        speaker="ANTONIO",
        text="You call me misbeliever, cut-throat dog, / And spit upon my Jewish gaberdine.",
        act_scene="1.3",
    )
    evidence = FakeEvidenceUseCase(
        scored_lines=(ScoredPlayLine(play_line=gaberdine_line, cosine_distance=0.18),),
    )
    interactor = TrialProgressionInteractor(
        port=InMemoryTrialPort(),
        portia=portia,
        evidence=evidence,
        tubal_enhancement=FakeTubalEnhancementClient(),
        duke=FakeDukeVerdictUseCase(),
        characters=FakeCharacterRelationUseCase(),
    )
    started = await interactor.start_dev_scene(CROWD_JEERS_SCENE_INDEX, 50)
    await interactor.submit_choice(
        SubmitChoiceInputDto(trial_id=started.trial_id, choice_id="coat_show_spit"),
    )

    assert portia.last_prompt is not None
    assert portia.last_prompt.folger_context is not None
    assert "spit upon my Jewish gaberdine" in portia.last_prompt.folger_context
