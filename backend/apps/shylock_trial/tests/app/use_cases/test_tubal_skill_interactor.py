from uuid import uuid4

import pytest

from shylock_trial.app.dtos.tubal_agent_dto import TubalAgentResult
from shylock_trial.app.dtos.tubal_skill_dto import TubalSkillInputDto
from shylock_trial.app.use_cases.tubal_skill_interactor import TubalSkillInteractor
from shylock_trial.domain.entities.trial_entity import Trial, TrialPhase
from shylock_trial.domain.value_objects.dp_score_vo import DpScore
from shylock_trial.domain.value_objects.hp_score_vo import HpScore
from shylock_trial.domain.value_objects.portia_hp_score_vo import PortiaHpScore

HATH_NOT_MOMENT_SCENE_INDEX = 6
CROWD_JEERS_SCENE_INDEX = 3


class InMemoryTrialPort:
    def __init__(self, trial: Trial) -> None:
        self._store = {trial.trial_id: trial}

    async def save(self, trial):
        self._store[trial.trial_id] = trial
        return trial

    async def find_by_id(self, trial_id):
        return self._store.get(trial_id)


class FakeTubalAgent:
    def __init__(self) -> None:
        self.calls = 0

    async def agentic_loop(self, portia_claim: str, scene_id: str) -> TubalAgentResult:
        self.calls += 1
        return TubalAgentResult(
            success=True,
            ftln=1,
            passage="passage",
            speaker="Shylock",
            act_scene="1.1",
            tubal_comment="found it",
        )


class FakePortiaUseCase:
    async def generate(self, prompt):
        raise AssertionError("should not be called in these tests")

    async def generate_scene_dialogue(self, prompt):
        from shylock_trial.app.constants.scene_catalog import fallback_scene_dialogue
        from shylock_trial.app.dtos.scene_dialogue_dto import SceneDialogueResultDto

        return SceneDialogueResultDto(
            content=fallback_scene_dialogue(prompt.scene_index),
            fallback_used=False,
        )


class FakeTubalEnhancementClient:
    async def generate_enhanced_choice(self, passage, original_choice, scene_id, speaker):
        return original_choice


def _make_trial(scene_index: int) -> Trial:
    return Trial(
        trial_id=uuid4(),
        scene_index=scene_index,
        dp=DpScore(50),
        hp=HpScore(50),
        portia_hp=PortiaHpScore(50),
        choice_history=[],
        phase=TrialPhase.IN_PROGRESS,
    )


@pytest.mark.asyncio
async def test_tubal_blocked_in_hath_not_moment_climax() -> None:
    trial = _make_trial(HATH_NOT_MOMENT_SCENE_INDEX)
    tubal_agent = FakeTubalAgent()
    interactor = TubalSkillInteractor(
        trial_port=InMemoryTrialPort(trial),
        tubal_agent=tubal_agent,
        portia=FakePortiaUseCase(),
        tubal_enhancement=FakeTubalEnhancementClient(),
    )

    result = await interactor.invoke_tubal(TubalSkillInputDto(trial_id=trial.trial_id))

    assert result.agent.success is False
    assert result.agent.tubal_comment == "이건... 그대 혼자 감당해야 할 순간이오, 샤일록."
    assert tubal_agent.calls == 0
    assert result.hp == 50
    assert result.dp == 50


@pytest.mark.asyncio
async def test_tubal_still_works_in_other_scenes() -> None:
    trial = _make_trial(CROWD_JEERS_SCENE_INDEX)
    tubal_agent = FakeTubalAgent()
    interactor = TubalSkillInteractor(
        trial_port=InMemoryTrialPort(trial),
        tubal_agent=tubal_agent,
        portia=FakePortiaUseCase(),
        tubal_enhancement=FakeTubalEnhancementClient(),
    )

    result = await interactor.invoke_tubal(TubalSkillInputDto(trial_id=trial.trial_id))

    assert result.agent.success is True
    assert tubal_agent.calls == 1
