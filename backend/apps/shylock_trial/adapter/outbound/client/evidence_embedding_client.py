import cohere

from core.config import get_settings

EMBED_MODEL = "embed-v4.0"


class EvidenceEmbeddingClient:
    """Cohere embed-v4.0 wrapper used inside EvidenceSearchPgRepository."""

    def __init__(self) -> None:
        settings = get_settings()
        self._client = cohere.AsyncClientV2(api_key=settings.cohere_api_key)

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
        vectors = await self.embed_texts([query])
        return vectors[0] if vectors else []
