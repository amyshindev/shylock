from shylock_trial.app.constants.curated_evidence import CURATED_EVIDENCE
from shylock_trial.app.dtos.evidence_search_dto import EvidenceSearchInputDto, ScoredPlayLine
from shylock_trial.app.ports.output.evidence_search_port import EvidenceSearchPort
from shylock_trial.domain.entities.evidence_entity import Evidence
from shylock_trial.domain.entities.play_line_entity import PlayLine

_STOPWORDS = frozenset(
    {
        "a",
        "an",
        "the",
        "and",
        "or",
        "to",
        "of",
        "in",
        "on",
        "for",
        "is",
        "it",
        "my",
        "me",
        "you",
        "your",
        "his",
        "her",
        "that",
        "this",
        "with",
        "not",
        "be",
        "as",
        "at",
        "by",
        "if",
        "we",
        "us",
        "do",
        "no",
        "—",
    }
)


def _tokenize(text: str) -> set[str]:
    tokens: set[str] = set()
    for raw in text.lower().replace("/", " ").replace(",", " ").split():
        token = "".join(ch for ch in raw if ch.isalnum())
        if len(token) >= 3 and token not in _STOPWORDS:
            tokens.add(token)
    return tokens


def _evidence_to_play_line(evidence: Evidence) -> PlayLine:
    return PlayLine(
        ftln=evidence.source_ftln_range[0] or 1,
        speaker="(curated)",
        text=evidence.quote,
        act_scene=evidence.act_scene,
    )


def rank_curated_play_lines(query: str, *, limit: int) -> list[ScoredPlayLine]:
    query_tokens = _tokenize(query)
    if not query_tokens:
        return []

    ranked: list[ScoredPlayLine] = []
    for evidence in CURATED_EVIDENCE:
        if not evidence.quote.strip():
            continue
        quote_tokens = _tokenize(evidence.quote)
        overlap = query_tokens & quote_tokens
        if not overlap:
            continue
        distance = max(0.05, 0.5 - (0.08 * len(overlap)))
        ranked.append(
            ScoredPlayLine(
                play_line=_evidence_to_play_line(evidence),
                cosine_distance=distance,
            )
        )

    ranked.sort(key=lambda item: item.cosine_distance)
    return ranked[:limit]


class InMemoryEvidenceSearchRepository(EvidenceSearchPort):
    _instance: "InMemoryEvidenceSearchRepository | None" = None

    @classmethod
    def get_instance(cls) -> "InMemoryEvidenceSearchRepository":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    async def search_similar_play_lines(
        self,
        input_dto: EvidenceSearchInputDto,
    ) -> list[PlayLine]:
        scored = await self.search_similar_play_lines_scored(input_dto)
        return [item.play_line for item in scored]

    async def search_similar_play_lines_scored(
        self,
        input_dto: EvidenceSearchInputDto,
    ) -> list[ScoredPlayLine]:
        if input_dto.evidence_id:
            evidence = next(
                (item for item in CURATED_EVIDENCE if item.evidence_id == input_dto.evidence_id),
                None,
            )
            if evidence is not None and evidence.quote.strip():
                return [
                    ScoredPlayLine(
                        play_line=_evidence_to_play_line(evidence),
                        cosine_distance=0.12,
                    )
                ]

        return rank_curated_play_lines(input_dto.query, limit=input_dto.limit)

    async def list_curated_evidence(self) -> list[Evidence]:
        return list(CURATED_EVIDENCE)

    async def find_evidence_by_id(self, evidence_id: str) -> Evidence | None:
        return next((item for item in CURATED_EVIDENCE if item.evidence_id == evidence_id), None)
