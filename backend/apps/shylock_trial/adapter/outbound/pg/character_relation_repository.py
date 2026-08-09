from sqlalchemy import or_, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from shylock_trial.adapter.outbound.mappers.character_relation_mapper import (
    character_node_to_entity,
    character_relation_to_entity,
)
from shylock_trial.adapter.outbound.orm.character_relation_orm import (
    CharacterNodeOrm,
    CharacterRelationOrm,
)
from shylock_trial.app.ports.output.character_relation_port import CharacterRelationPort
from shylock_trial.domain.entities.character_relation_entity import (
    CharacterNode,
    CharacterRelation,
)

# Walks character_relations as a graph via a recursive CTE, tracking the
# relation_ids traversed (for the final fetch) and the character_ids visited
# (node_chain, purely for cycle prevention via NOT ... = ANY(...) — a cycle
# is possible even in this small hand-curated graph, e.g. antonio/shylock's
# two enemy_of rows plus their debtor_of/creditor_of row). max_hops bounds
# recursion depth explicitly rather than relying on the cycle check alone.
#
# This only returns the ids of the shortest path — the actual CharacterRelation
# rows are fetched separately (see find_path) via a normal ORM select, same as
# every other repository in this codebase; the recursive part is the one piece
# that genuinely doesn't fit SQLAlchemy Core's query builder cleanly, so it's
# the one place in adapter/outbound/pg/ that uses text() instead of select().
_FIND_PATH_SQL = text(
    """
    WITH RECURSIVE path(from_id, to_id, node_chain, relation_chain, depth) AS (
        SELECT from_character_id, to_character_id,
               ARRAY[from_character_id, to_character_id]::text[],
               ARRAY[relation_id],
               1
        FROM character_relations
        WHERE from_character_id = :from_id

        UNION ALL

        SELECT p.from_id, r.to_character_id,
               p.node_chain || r.to_character_id,
               p.relation_chain || r.relation_id,
               p.depth + 1
        FROM path p
        JOIN character_relations r ON r.from_character_id = p.to_id
        WHERE p.depth < :max_hops
          AND NOT r.to_character_id = ANY(p.node_chain)
    )
    SELECT relation_chain FROM path
    WHERE to_id = :to_id
    ORDER BY depth
    LIMIT 1
    """
)


class CharacterRelationPgRepository(CharacterRelationPort):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_node(self, character_id: str) -> CharacterNode | None:
        orm = await self._session.get(CharacterNodeOrm, character_id)
        return character_node_to_entity(orm) if orm else None

    async def list_nodes(self) -> list[CharacterNode]:
        result = await self._session.execute(select(CharacterNodeOrm))
        return [character_node_to_entity(orm) for orm in result.scalars().all()]

    async def list_relations_for(self, character_id: str) -> list[CharacterRelation]:
        result = await self._session.execute(
            select(CharacterRelationOrm).where(
                or_(
                    CharacterRelationOrm.from_character_id == character_id,
                    CharacterRelationOrm.to_character_id == character_id,
                )
            )
        )
        return [character_relation_to_entity(orm) for orm in result.scalars().all()]

    async def find_path(
        self,
        from_character_id: str,
        to_character_id: str,
        max_hops: int = 4,
    ) -> list[CharacterRelation]:
        if from_character_id == to_character_id:
            return []

        result = await self._session.execute(
            _FIND_PATH_SQL,
            {"from_id": from_character_id, "to_id": to_character_id, "max_hops": max_hops},
        )
        row = result.first()
        if row is None:
            return []
        relation_ids: list[int] = row.relation_chain

        rows = await self._session.execute(
            select(CharacterRelationOrm).where(CharacterRelationOrm.relation_id.in_(relation_ids))
        )
        by_id = {orm.relation_id: orm for orm in rows.scalars().all()}
        # relation_ids is already in traversal order; `IN` doesn't preserve it.
        return [character_relation_to_entity(by_id[rid]) for rid in relation_ids]
