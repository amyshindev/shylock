"""Pure text formatting for the character_relation graph, shared by every
prompt that grounds itself in it. Originally lived inside lore_chat_prompt.py
(lore_chat was the graph's first consumer) — relocated here once
portia_prompt.py needed the same formatting for reaction generation, so
neither stem's constants file has to import from the other's.

Deliberately just formatting: these functions take already-fetched
CharacterNode/CharacterRelation values and never touch CharacterRelationUseCase
themselves — the async DB call and any caller-specific filtering (e.g.
trial_progression_interactor withholding Portia's own married_to edge to
protect her disguise) belong in the interactor, not here.
"""

from shylock_trial.domain.entities.character_relation_entity import (
    CharacterNode,
    CharacterRelation,
)


def format_character(
    node: CharacterNode,
    relations: list[CharacterRelation],
    *,
    include_description: bool = True,
) -> str:
    """Formats one character's node description plus every relation touching
    it, for players asking "who is X" / "how are X and Y connected" (lore_chat)
    or for grounding an in-character reaction in what that character actually
    knows (portia_response). This is the structured counterpart to
    format_passage()/build_context_block() in lore_chat_prompt.py — pgvector
    search over play lines is a poor fit for broad character questions
    (nearest-neighbor line retrieval surfaces vocative/name-mention lines,
    not biography), so this pulls from the curated character_relation graph
    instead.

    include_description=False skips the node's own description line — for
    Portia's own reaction prompt, her description ("재판에서 발타자르로
    변장해 판결을 내린다") would hand the model her disguise secret in plain
    prose; PORTIA_PERSONA already covers her identity safely, so callers pass
    include_description=False and additionally filter out her married_to
    relation before calling this at all (see
    trial_progression_interactor._build_character_context)."""
    lines = [f"[{node.name_ko} ({node.name_en})] {node.description}"] if include_description else []
    lines.extend(f"- {relation.description} ({relation.relation_type})" for relation in relations)
    return "\n".join(lines)


def build_character_context_block(character_blocks: list[str]) -> str:
    if not character_blocks:
        return ""
    joined = "\n\n".join(character_blocks)
    return f"인물 관계 정보:\n{joined}"


def format_relationship_path(path: list[CharacterRelation], name_by_id: dict[str, str]) -> str:
    """Formats a multi-hop chain (see CharacterRelationUseCase.trace_relationship)
    as an explicit "A → B → C" line plus the fact behind each hop. Two
    characters mentioned in the same question rarely have a *direct* relation
    row between them (e.g. Portia/Antonio never interact directly) — the
    actual connection (Portia married_to Bassanio, Bassanio financed_by
    Antonio) only exists as separate rows on each of their individual
    format_character() blocks, and a smaller local model won't reliably
    chain those itself. Spelling the path out here is what makes the
    conflict-of-interest example (the original motivation for this graph)
    actually show up in answers instead of relying on the LLM to notice it."""
    if not path:
        return ""
    node_chain = [name_by_id.get(path[0].from_character_id, path[0].from_character_id)]
    node_chain.extend(name_by_id.get(relation.to_character_id, relation.to_character_id) for relation in path)
    facts = " → ".join(relation.description for relation in path)
    return f"{' → '.join(node_chain)}: {facts}"


def build_relationship_path_block(path_lines: list[str]) -> str:
    if not path_lines:
        return ""
    joined = "\n".join(f"- {line}" for line in path_lines)
    return f"인물 간 연결 관계:\n{joined}"
