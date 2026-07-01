from abc import ABC, abstractmethod

from shylock_trial.app.dtos.portia_response_dto import (
    PortiaResponsePromptDto,
    PortiaResponseResultDto,
)
from shylock_trial.app.dtos.scene_dialogue_dto import (
    SceneDialoguePromptDto,
    SceneDialogueResultDto,
)


class PortiaResponseUseCase(ABC):
    @abstractmethod
    async def generate(self, prompt: PortiaResponsePromptDto) -> PortiaResponseResultDto: ...

    @abstractmethod
    async def generate_scene_dialogue(
        self,
        prompt: SceneDialoguePromptDto,
    ) -> SceneDialogueResultDto: ...
