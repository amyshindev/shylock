from abc import ABC, abstractmethod

from shylock_trial.app.dtos.portia_response_dto import (
    PortiaResponsePromptDto,
    PortiaResponseResultDto,
)


class PortiaResponsePort(ABC):
    @abstractmethod
    async def generate(self, prompt: PortiaResponsePromptDto) -> PortiaResponseResultDto: ...
