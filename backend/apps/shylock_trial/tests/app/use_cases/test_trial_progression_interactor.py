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


@pytest.mark.asyncio
async def test_launcelot_skill_grants_dp() -> None:
    from shylock_trial.app.constants.game_balance import LAUNCELOT_SKILL_DP_GAIN, SHYLOCK_DP_START
    from shylock_trial.app.use_cases.trial_progression_interactor import TrialProgressionInteractor

    interactor = TrialProgressionInteractor(
        port=InMemoryTrialPort(),
        portia=FakePortiaUseCase(),
        evidence=FakeEvidenceUseCase(),
        tubal_enhancement=FakeTubalEnhancementClient(),
    )
    started = await interactor.start()
    result = await interactor.use_launcelot_skill(started.trial_id)

    assert result.dp == SHYLOCK_DP_START + LAUNCELOT_SKILL_DP_GAIN


@pytest.mark.asyncio
async def test_venice_skill_shields_next_negative_choice() -> None:
    from shylock_trial.app.constants.game_balance import (
        SHYLOCK_DP_START,
        VENICE_CONTRADICTION_SKILL_COST,
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
    skill = await interactor.use_venice_contradiction_skill(started.trial_id)

    assert skill.venice_dp_shield is True
    assert skill.dp == SHYLOCK_DP_START - VENICE_CONTRADICTION_SKILL_COST

    choice = await interactor.submit_choice(
        SubmitChoiceInputDto(trial_id=started.trial_id, choice_id="appeal_mercy"),
    )

    assert choice.dp == skill.dp
    assert choice.venice_dp_shield is False

