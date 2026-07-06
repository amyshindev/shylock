import pytest

from shylock_trial.app.constants.ending_type_map import EndingType


class FakePortiaUseCase:
    async def generate(self, prompt):
        from shylock_trial.app.dtos.portia_response_dto import PortiaResponseResultDto

        return PortiaResponseResultDto(text="Portia speaks.", fallback_used=False)

    async def generate_scene_dialogue(self, prompt):
        from shylock_trial.app.constants.scene_catalog import fallback_scene_dialogue
        from shylock_trial.app.dtos.scene_dialogue_dto import SceneDialogueResultDto

        return SceneDialogueResultDto(
            content=fallback_scene_dialogue(prompt.scene_index),
            fallback_used=False,
        )


class FakeEvidenceUseCase:
    async def search(self, input_dto):
        from shylock_trial.app.dtos.evidence_search_dto import EvidenceSearchResultDto

        return EvidenceSearchResultDto(play_lines=())

    async def list_curated_evidence(self):
        return []

    async def get_evidence(self, evidence_id: str):
        return None


class FakeTubalEnhancementClient:
    async def generate_enhanced_choice(
        self,
        passage: str,
        original_choice: str,
        scene_id: str,
        speaker: str,
    ) -> str:
        return original_choice


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


@pytest.mark.asyncio
async def test_start_trial_returns_scene_dialogue() -> None:
    from shylock_trial.app.constants.game_balance import PORTIA_HP_START
    from shylock_trial.app.use_cases.trial_progression_interactor import TrialProgressionInteractor

    interactor = TrialProgressionInteractor(
        port=InMemoryTrialPort(),
        portia=FakePortiaUseCase(),
        evidence=FakeEvidenceUseCase(),
        tubal_enhancement=FakeTubalEnhancementClient(),
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
    )
    started = await interactor.start()
    choice = await interactor.submit_choice(
        SubmitChoiceInputDto(trial_id=started.trial_id, choice_id="gold_refuse_direct"),
    )

    assert started.hp == SHYLOCK_HP_START
    assert choice.hp == SHYLOCK_HP_START - 6
    assert choice.dp == SHYLOCK_DP_START + 13
    assert started.portia_hp == PORTIA_HP_START
    assert choice.portia_hp == PORTIA_HP_START - 7


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
    )
    started = await interactor.start_dev_scene(CROWD_JEERS_SCENE_INDEX + 1, 50)
    await interactor.use_venice_paradox_skill(started.trial_id)

    with pytest.raises(ValueError, match="skill_unavailable"):
        await interactor.use_venice_paradox_skill(started.trial_id)

