from abc import ABC, abstractmethod

from shylock_trial.app.dtos.lore_chat_dto import LoreChatTurnDto
from shylock_trial.domain.entities.play_line_entity import PlayLine


class LoreChatLlmPort(ABC):
    @abstractmethod
    async def answer(
        self,
        question: str,
        history: tuple[LoreChatTurnDto, ...],
        passages: tuple[PlayLine, ...],
    ) -> str: ...
