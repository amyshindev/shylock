from abc import ABC, abstractmethod

from shylock_trial.domain.entities.character_relation_entity import (
    CharacterNode,
    CharacterRelation,
)


class CharacterRelationPort(ABC):
    @abstractmethod
    async def get_node(self, character_id: str) -> CharacterNode | None: ...

    @abstractmethod
    async def find_path(
        self,
        from_character_id: str,
        to_character_id: str,
        max_hops: int = 4,
    ) -> list[CharacterRelation]:
        """Shortest relation chain from_character_id -> to_character_id, in
        traversal order. Empty list if no path exists within max_hops."""
        ...
