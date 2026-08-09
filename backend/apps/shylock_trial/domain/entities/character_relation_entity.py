from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CharacterNode:
    character_id: str
    name_ko: str
    name_en: str
    description: str


@dataclass(frozen=True, slots=True)
class CharacterRelation:
    from_character_id: str
    relation_type: str
    to_character_id: str
    description: str
    evidence_ftln_start: int
    evidence_ftln_end: int
