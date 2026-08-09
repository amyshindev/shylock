from shylock_trial.adapter.outbound.orm.character_relation_orm import (
    CharacterNodeOrm,
    CharacterRelationOrm,
)
from shylock_trial.domain.entities.character_relation_entity import (
    CharacterNode,
    CharacterRelation,
)


def character_node_to_entity(orm: CharacterNodeOrm) -> CharacterNode:
    return CharacterNode(
        character_id=orm.character_id,
        name_ko=orm.name_ko,
        name_en=orm.name_en,
        description=orm.description,
    )


def character_relation_to_entity(orm: CharacterRelationOrm) -> CharacterRelation:
    return CharacterRelation(
        from_character_id=orm.from_character_id,
        relation_type=orm.relation_type,
        to_character_id=orm.to_character_id,
        description=orm.description,
        evidence_ftln_start=orm.evidence_ftln_start,
        evidence_ftln_end=orm.evidence_ftln_end,
    )
