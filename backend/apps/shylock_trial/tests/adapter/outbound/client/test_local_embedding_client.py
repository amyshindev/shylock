import json

import httpx
import pytest

from shylock_trial.adapter.outbound.client.local_embedding_client import (
    TASK_DESCRIPTION,
    LocalEmbeddingClient,
)


def _client_returning(embedding: list[float]) -> LocalEmbeddingClient:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/embed"
        body = json.loads(request.content)
        assert body["text"] == f"Instruct: {TASK_DESCRIPTION}\nQuery: 테스트 쿼리"
        return httpx.Response(200, json={"embedding": embedding})

    http_client = httpx.AsyncClient(transport=httpx.MockTransport(handler), base_url="http://test-embed")
    return LocalEmbeddingClient(http_client=http_client)


@pytest.mark.asyncio
async def test_embed_query_wraps_with_instruct_prefix_and_returns_vector() -> None:
    client = _client_returning([0.1, 0.2, 0.3])

    vector = await client.embed_query("테스트 쿼리")

    assert vector == [0.1, 0.2, 0.3]


@pytest.mark.asyncio
async def test_embed_query_empty_string_short_circuits_without_a_request() -> None:
    def handler(_request: httpx.Request) -> httpx.Response:
        raise AssertionError("should not make a request for an empty query")

    http_client = httpx.AsyncClient(transport=httpx.MockTransport(handler), base_url="http://test-embed")
    client = LocalEmbeddingClient(http_client=http_client)

    assert await client.embed_query("") == []


@pytest.mark.asyncio
async def test_embed_query_raises_on_server_error() -> None:
    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, json={"detail": "model not loaded"})

    http_client = httpx.AsyncClient(transport=httpx.MockTransport(handler), base_url="http://test-embed")
    client = LocalEmbeddingClient(http_client=http_client)

    with pytest.raises(httpx.HTTPStatusError):
        await client.embed_query("테스트 쿼리")
