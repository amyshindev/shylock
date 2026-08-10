"""No-op CharacterRelationPort for local dev without Postgres (USE_MEMORY_STORE
or no DATABASE_URL at all). Unlike InMemoryEvidenceSearchRepository, this
isn't a real in-memory mirror of the graph — the curated node/edge data only
exists as a one-time Alembic migration payload (alembic/versions/031_add_
character_relation_graph.py), not a reusable Python constant, so duplicating
it here would just be another copy to keep in sync for a stem with no router
of its own.

Every method returns empty, which is exactly the right degrade-gracefully
behavior for its only two consumers: LoreChatInteractor treats an empty
character list as "no character mentioned" (skips the context block), and
TrialProgressionInteractor treats it as "no character context available"
(reaction prompts just proceed without it) — both already designed to work
fine with zero graph data, so this never needs to raise the way
get_character_relation_repository used to when no session was available.
"""

from shylock_trial.app.ports.output.character_relation_port import CharacterRelationPort
from shylock_trial.domain.entities.character_relation_entity import (
    CharacterNode,
    CharacterRelation,
)


class NullCharacterRelationRepository(CharacterRelationPort):
    async def get_node(self, character_id: str) -> CharacterNode | None:
        return None

    async def list_nodes(self) -> list[CharacterNode]:
        return []

    async def list_relations_for(self, character_id: str) -> list[CharacterRelation]:
        return []

    async def find_path(
        self,
        from_character_id: str,
        to_character_id: str,
        max_hops: int = 4,
    ) -> list[CharacterRelation]:
        return []
