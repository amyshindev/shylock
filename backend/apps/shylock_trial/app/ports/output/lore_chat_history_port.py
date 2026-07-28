from abc import ABC, abstractmethod

from shylock_trial.app.dtos.lore_chat_dto import LoreChatTurnDto


class LoreChatHistoryPort(ABC):
    @abstractmethod
    async def get(self, session_id: str) -> tuple[LoreChatTurnDto, ...]: ...

    @abstractmethod
    async def append(self, session_id: str, turn: LoreChatTurnDto) -> None: ...
