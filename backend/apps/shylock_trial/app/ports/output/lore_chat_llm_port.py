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
        character_context: str = "",
    ) -> str:
        """character_context is the pre-formatted "인물 관계 정보" block built
        from the character_relation graph (see lore_chat_prompt.build_character_context_block)
        — empty string when the question didn't mention a known character.
        """
        ...
