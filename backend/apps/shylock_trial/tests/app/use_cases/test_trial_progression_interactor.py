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
    )
    result = await interactor.start()

    assert result.scene_dialogue.lines
    assert result.phase.value == "in_progress"

