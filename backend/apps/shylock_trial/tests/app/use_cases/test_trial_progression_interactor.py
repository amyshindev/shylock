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

    async def generate(self, prompt):
        from shylock_trial.app.dtos.portia_response_dto import PortiaResponseResultDto

        self.last_prompt = prompt
        # Real Port implementations echo prompt.reactor_speaker/_label into
        # the result (see portia_response_client.py / ollama_portia_response_
        # client.py) — mirroring that here so tests exercise the full
        # submit_choice -> ... -> SubmitChoiceResultDto plumbing, not just
        # prompt construction.
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


class FakeCharacterRelationUseCase:
    """Defaults to an empty graph, matching NullCharacterRelationRepository —
    most tests here don't care about character_context, only the tests that
    explicitly assert on it (see test_portia_prompt.py) construct nodes."""

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
async def test_crowd_jeers_reaction_still_voiced_by_portia() -> None:
    # crowd_jeers isn't in REACTOR_OVERRIDE_SCENES yet — this scene's own
    # speaker (CROWD) must NOT bleed into the reactor override until that's
    # deliberately added, same as every other non-opted-in scene.
    from shylock_trial.app.constants.scene_progression import CROWD_JEERS_SCENE_INDEX
    from shylock_trial.app.dtos.trial_progression_dto import SubmitChoiceInputDto
    from shylock_trial.app.use_cases.trial_progression_interactor import TrialProgressionInteractor

    portia = FakePortiaUseCase()
    interactor = TrialProgressionInteractor(
        port=InMemoryTrialPort(),
        portia=portia,
        evidence=FakeEvidenceUseCase(),
        tubal_enhancement=FakeTubalEnhancementClient(),
        characters=FakeCharacterRelationUseCase(),
    )
    started = await interactor.start_dev_scene(CROWD_JEERS_SCENE_INDEX, 50)
    choice = await interactor.submit_choice(
        SubmitChoiceInputDto(trial_id=started.trial_id, choice_id="coat_show_spit"),
    )

    assert portia.last_prompt.reactor_speaker == "PORTIA"
    assert choice.portia_response_speaker == "PORTIA"
    assert choice.portia_response_speaker_label == "포샤"


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
    # Bassanio has nothing to hide — his own node description is safe to include.
    assert "안토니오의 친구" in portia.last_prompt.character_context


@pytest.mark.asyncio
async def test_portia_character_context_withholds_her_own_disguise_secret() -> None:
    from shylock_trial.app.dtos.trial_progression_dto import SubmitChoiceInputDto
    from shylock_trial.app.use_cases.trial_progression_interactor import TrialProgressionInteractor
    from shylock_trial.domain.entities.character_relation_entity import (
        CharacterNode,
        CharacterRelation,
    )

    portia_node = CharacterNode(
        character_id="portia",
        name_ko="포샤",
        name_en="Portia",
        description="벨몬트의 부유한 상속녀. 재판에서 발타자르로 변장해 판결을 내린다.",
    )
    secret_marriage = CharacterRelation(
        from_character_id="portia",
        relation_type="married_to",
        to_character_id="bassanio",
        description="포샤가 바사니오에게 반지를 주며 아내가 되기로 서약한다.",
        evidence_ftln_start=3002169,
        evidence_ftln_end=3002175,
    )
    safe_fact = CharacterRelation(
        from_character_id="portia",
        relation_type="presides_over",
        to_character_id="shylock",
        description="포샤가 이 재판을 주재한다.",
        evidence_ftln_start=1,
        evidence_ftln_end=2,
    )
    portia = FakePortiaUseCase()
    interactor = TrialProgressionInteractor(
        port=InMemoryTrialPort(),
        portia=portia,
        evidence=FakeEvidenceUseCase(),
        tubal_enhancement=FakeTubalEnhancementClient(),
        characters=FakeCharacterRelationUseCase(
            nodes={"portia": portia_node},
            relations_by_character={"portia": [secret_marriage, safe_fact]},
        ),
    )
    # scene_index=1 (portia_opens) isn't in REACTOR_OVERRIDE_SCENES, so Portia reacts.
    started = await interactor.start_dev_scene(1, 50)
    await interactor.submit_choice(
        SubmitChoiceInputDto(trial_id=started.trial_id, choice_id="bond_signature"),
    )

    context = portia.last_prompt.character_context
    assert "발타자르로 변장" not in context
    assert "married_to" not in context
    assert "아내가 되기로 서약" not in context
    assert "포샤가 이 재판을 주재한다" in context


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
    # Antonio cut closes the scene after Portia's final line.
    assert speakers[-3:] == ["NARRATOR", "ANTONIO", "NARRATOR"]
    # Entering the scene costs nothing — the effect lands when it finishes.
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
        characters=FakeCharacterRelationUseCase(),
    )
    started = await interactor.start_dev_scene(CROWD_JEERS_SCENE_INDEX, 50)
    await interactor.submit_choice(
        SubmitChoiceInputDto(trial_id=started.trial_id, choice_id="coat_show_spit"),
    )

    assert portia.last_prompt is not None
    assert portia.last_prompt.folger_context is not None
    assert "spit upon my Jewish gaberdine" in portia.last_prompt.folger_context
