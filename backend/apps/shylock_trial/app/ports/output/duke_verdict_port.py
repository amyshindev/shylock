from abc import ABC, abstractmethod

from shylock_trial.app.dtos.duke_verdict_dto import DukeVerdictPromptDto, DukeVerdictResultDto


class DukeVerdictPort(ABC):
    @abstractmethod
    async def judge(self, prompt: DukeVerdictPromptDto) -> DukeVerdictResultDto: ...
