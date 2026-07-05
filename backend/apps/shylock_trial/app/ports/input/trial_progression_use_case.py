from abc import ABC, abstractmethod
from uuid import UUID

from shylock_trial.app.dtos.trial_progression_dto import (
    AdvanceSceneResultDto,
    GenerateEndingResultDto,
    LauncelotSkillResultDto,
    StartTrialResultDto,
    SubmitChoiceInputDto,
    SubmitChoiceResultDto,
    VeniceParadoxSkillResultDto,
)
from shylock_trial.domain.entities.trial_entity import Trial


class TrialProgressionUseCase(ABC):
    @abstractmethod
    async def start(self) -> StartTrialResultDto: ...

    @abstractmethod
    async def submit_choice(self, input_dto: SubmitChoiceInputDto) -> SubmitChoiceResultDto: ...

    @abstractmethod
    async def advance_scene(self, trial_id: UUID) -> AdvanceSceneResultDto: ...

    @abstractmethod
    async def generate_ending(self, trial_id: UUID) -> GenerateEndingResultDto: ...

    @abstractmethod
    async def get_trial(self, trial_id: UUID) -> Trial: ...

    @abstractmethod
    async def use_launcelot_skill(self, trial_id: UUID) -> LauncelotSkillResultDto: ...

    @abstractmethod
    async def use_venice_paradox_skill(
        self,
        trial_id: UUID,
    ) -> VeniceParadoxSkillResultDto: ...

    @abstractmethod
    async def start_dev_scene(self, scene_index: int, dp: int) -> StartTrialResultDto: ...
