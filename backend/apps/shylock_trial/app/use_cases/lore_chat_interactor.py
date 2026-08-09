from __future__ import annotations

from itertools import combinations
from uuid import uuid4

from shylock_trial.app.constants.lore_chat_prompt import (
    build_character_context_block,
    build_relationship_path_block,
    format_character,
    format_relationship_path,
)
from shylock_trial.app.dtos.evidence_search_dto import EvidenceSearchInputDto
from shylock_trial.app.dtos.lore_chat_dto import (
    LoreChatAskInputDto,
    LoreChatResultDto,
    LoreChatSourceDto,
    LoreChatTurnDto,
)
from shylock_trial.app.ports.input.character_relation_use_case import CharacterRelationUseCase
from shylock_trial.app.ports.input.evidence_search_use_case import EvidenceSearchUseCase
from shylock_trial.app.ports.input.lore_chat_use_case import LoreChatUseCase
from shylock_trial.app.ports.output.lore_chat_history_port import LoreChatHistoryPort
from shylock_trial.app.ports.output.lore_chat_llm_port import LoreChatLlmPort

# Bounds how many prior turns are sent to the LLM per call — independent of
# how many turns the history store itself retains (see
# lore_chat_redis_history.py's own trim), same idea as MAX_AGENT_ITERATIONS
# in tubal_agent_client.py: an explicit cost/latency cap, not a correctness
# requirement.
MAX_HISTORY_TURNS_FOR_LLM = 10

EXCERPT_MAX_CHARS = 200


class LoreChatInteractor(LoreChatUseCase):
    def __init__(
        self,
        evidence: EvidenceSearchUseCase,
        llm: LoreChatLlmPort,
        history: LoreChatHistoryPort,
        characters: CharacterRelationUseCase,
    ) -> None:
        self._evidence = evidence
        self._llm = llm
        self._history = history
        self._characters = characters

    async def ask(self, input_dto: LoreChatAskInputDto) -> LoreChatResultDto:
        session_id = input_dto.session_id or str(uuid4())
        message = input_dto.message.strip()

        stored_history = await self._history.get(session_id)
        recent_history = stored_history[-MAX_HISTORY_TURNS_FOR_LLM:]

        search_result = await self._evidence.search(
            EvidenceSearchInputDto(query=message, limit=5)
        )
        character_context = await self._build_character_context(message)

        answer = await self._llm.answer(
            question=message,
            history=recent_history,
            passages=search_result.play_lines,
            character_context=character_context,
        )

        await self._history.append(session_id, LoreChatTurnDto(role="human", content=message))
        await self._history.append(session_id, LoreChatTurnDto(role="ai", content=answer))

        sources = tuple(
            LoreChatSourceDto(
                ftln=line.ftln,
                act_scene=line.act_scene,
                speaker=line.speaker,
                excerpt=line.text[:EXCERPT_MAX_CHARS],
            )
            for line in search_result.play_lines
        )

        return LoreChatResultDto(session_id=session_id, answer=answer, sources=sources)

    async def _build_character_context(self, message: str) -> str:
        """Plain keyword match of the 7 curated character names (ko/en)
        against the raw question — deliberately not a search/embedding
        step, since the candidate set is tiny and fixed. Any character
        mentioned gets its node description plus every relation touching
        it pulled from the character_relation graph (see
        CharacterRelationUseCase), which is what actually fixes lore_chat's
        weak answers to "who is X" / "how are X and Y related" questions —
        pgvector search over play lines can't do that kind of structured,
        guaranteed-relevant lookup (see format_character's docstring).

        When 2+ characters are mentioned, this also traces the shortest
        relation path between every pair (see trace_relationship) and adds
        it as its own explicit block. Verified live against the local
        Ollama model that per-character blocks alone aren't enough — asked
        "포샤와 안토니오는 무슨 관계인가요?" (they never interact directly;
        the real link is Portia married_to Bassanio, Bassanio financed_by
        Antonio) and the model answered "직접적인 연결 고리가 확인되지
        않습니다", i.e. it didn't chain the two separate blocks itself. This
        is exactly the conflict-of-interest case the graph was built for,
        so the connection needs to be spelled out rather than left implicit.
        """
        nodes = await self._characters.list_characters()
        lowered = message.lower()
        mentioned = [
            node for node in nodes if node.name_ko in message or node.name_en.lower() in lowered
        ]
        if not mentioned:
            return ""

        blocks = []
        for node in mentioned:
            relations = await self._characters.get_relations_for(node.character_id)
            blocks.append(format_character(node, relations))
        context = build_character_context_block(blocks)

        if len(mentioned) >= 2:
            name_by_id = {node.character_id: node.name_ko for node in nodes}
            path_lines = []
            for a, b in combinations(mentioned, 2):
                path = await self._characters.trace_relationship(a.character_id, b.character_id)
                if not path:
                    path = await self._characters.trace_relationship(b.character_id, a.character_id)
                if path:
                    path_lines.append(format_relationship_path(path, name_by_id))
            path_block = build_relationship_path_block(path_lines)
            if path_block:
                context = f"{context}\n\n{path_block}"

        return context
