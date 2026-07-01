from abc import ABC, abstractmethod

from shylock_trial.app.dtos.tubal_skill_dto import TubalSkillInputDto, TubalSkillResultDto


class TubalSkillUseCase(ABC):
    @abstractmethod
    async def invoke_tubal(self, input_dto: TubalSkillInputDto) -> TubalSkillResultDto: ...
