from abc import ABC, abstractmethod

from shylock_trial.app.dtos.lore_chat_dto import LoreChatAskInputDto, LoreChatResultDto


class LoreChatUseCase(ABC):
    @abstractmethod
    async def ask(self, input_dto: LoreChatAskInputDto) -> LoreChatResultDto: ...
