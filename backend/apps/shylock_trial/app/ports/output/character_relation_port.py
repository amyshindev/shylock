from abc import ABC, abstractmethod

from shylock_trial.domain.entities.character_relation_entity import (
    CharacterNode,
    CharacterRelation,
)


class CharacterRelationPort(ABC):
    @abstractmethod
    async def get_node(self, character_id: str) -> CharacterNode | None: ...

    @abstractmethod
    async def list_nodes(self) -> list[CharacterNode]:
        """All character nodes — for callers that need to check which
        characters a piece of free text mentions (lore_chat)."""
        ...

    @abstractmethod
    async def list_relations_for(self, character_id: str) -> list[CharacterRelation]:
        """Every direct relation touching character_id, in either direction
        (symmetric relations like married_to are stored as two rows, one per
        direction, so both show up here)."""
        ...

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
