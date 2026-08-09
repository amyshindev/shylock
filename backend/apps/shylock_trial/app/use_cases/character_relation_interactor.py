from shylock_trial.app.ports.input.character_relation_use_case import CharacterRelationUseCase
from shylock_trial.app.ports.output.character_relation_port import CharacterRelationPort
from shylock_trial.domain.entities.character_relation_entity import (
    CharacterNode,
    CharacterRelation,
)


class CharacterRelationInteractor(CharacterRelationUseCase):
    def __init__(self, port: CharacterRelationPort) -> None:
        self._port = port

    async def get_character(self, character_id: str) -> CharacterNode | None:
        return await self._port.get_node(character_id)

    async def trace_relationship(
        self,
        from_character_id: str,
        to_character_id: str,
        max_hops: int = 4,
    ) -> list[CharacterRelation]:
        return await self._port.find_path(from_character_id, to_character_id, max_hops)
