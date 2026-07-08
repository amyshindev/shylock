import cohere

from infrastructure.config import get_settings

EMBED_MODEL = "embed-v4.0"
EMBED_DIMENSION = 1536


class EvidenceEmbeddingClient:
    """Cohere embed-v4.0 wrapper used inside EvidenceSearchPgRepository."""

    def __init__(self) -> None:
        settings = get_settings()
        self._client = cohere.AsyncClientV2(api_key=settings.cohere_api_key_plain())

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        response = await self._client.embed(
            texts=texts,
            model=EMBED_MODEL,
            input_type="search_document",
            embedding_types=["float"],
        )
        return [list(vec) for vec in response.embeddings.float_]

    async def embed_query(self, query: str) -> list[float]:
        if not query:
            return []
        response = await self._client.embed(
            texts=[query],
            model=EMBED_MODEL,
            input_type="search_query",
            embedding_types=["float"],
        )
        vectors = response.embeddings.float_
        return list(vectors[0]) if vectors else []
