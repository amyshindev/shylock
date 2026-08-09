"""Local embedding client — HTTP client for the e5 embedding server that runs
on the home Mac (backend/embed_main.py), exposed through the same
Cloudflare Tunnel + Access pattern already used for Ollama — see
ollama_portia_response_client.py, which this mirrors almost exactly (base_url
+ CF Access headers + timeout, all from Settings).

Why a network call to a home Mac instead of loading the model in-process on
the EC2 backend (the first version of this file did that): measured directly
on the production EC2 instance, in-process CPU inference was ~20-26x slower
than Cohere's API (mean 7.5s, p95 29s — see
_docs/local-embedding-hosting-options.md), consistent with a burstable
instance running out of CPU credit and throttling. That's not something a
code change fixes. The same doc measured Apple Silicon inference at ~13ms —
~580x faster — so routing to the Mac over the network (the same round trip
already proven out for Ollama) is the actual fix, not in-process serving.

Query-time embedding uses the exact "Instruct: ...\\nQuery: ..." wrapper that
shylock_trial.evals.compare_embedding_models already validated against Cohere
on this corpus (plain, no prefix, on the corpus side — see
adapter/outbound/seeding/backfill_local_embeddings.py, which built the
embedding_e5_1024 columns this client's output gets compared against).
TASK_DESCRIPTION must stay in sync with that eval's LOCAL_TASK_DESCRIPTION —
it was written for the play_chunks/Tubal-rebuttal use case specifically, but
is reused as-is for the more general search_similar_play_lines_scored too,
same simplification compare_embedding_models.py already made ("one
instruction is good enough for a qualitative compare — tune per-query if
chasing precision later").

The server on the other end owns the model choice (embed_main.py
reads Settings.local_embedding_model) — this client doesn't need to know
which model is actually running, same as PortiaResponseClient not needing to
know Ollama's model beyond what it sends in the request.
"""

from __future__ import annotations

import httpx

from infrastructure.config import get_settings

# Must match shylock_trial.evals.compare_embedding_models.LOCAL_TASK_DESCRIPTION —
# that's the exact wording the e5-vs-Cohere quality comparison was run with.
# Changing it here without re-running that comparison is not a no-op.
TASK_DESCRIPTION = (
    "Given a modern-English paraphrase of a courtroom argument, retrieve the "
    "Early Modern English play passage from The Merchant of Venice that it echoes."
)


class LocalEmbeddingClient:
    def __init__(self, http_client: httpx.AsyncClient | None = None) -> None:
        settings = get_settings()
        # Cloudflare Access Service Token headers — no-ops (empty dict) in
        # local dev where LOCAL_EMBEDDING_BASE_URL is plain localhost with no
        # Access policy in front of it. Deliberately its own Service Token
        # (LOCAL_EMBEDDING_CF_ACCESS_CLIENT_ID/SECRET), separate from the
        # Ollama pair (CF_ACCESS_CLIENT_ID/SECRET) even though both tunnel
        # through the same home Mac — a leaked/rotated token then only
        # affects one of the two tunneled services, not both.
        access_headers = (
            {
                "CF-Access-Client-Id": settings.local_embedding_cf_access_client_id,
                "CF-Access-Client-Secret": settings.local_embedding_cf_access_client_secret,
            }
            if settings.local_embedding_cf_access_client_id and settings.local_embedding_cf_access_client_secret
            else {}
        )
        self._client = http_client or httpx.AsyncClient(
            base_url=settings.local_embedding_base_url,
            timeout=settings.local_embedding_timeout_seconds,
            headers=access_headers,
        )

    async def embed_query(self, query: str) -> list[float]:
        if not query:
            return []
        prompted = f"Instruct: {TASK_DESCRIPTION}\nQuery: {query}"
        response = await self._client.post("/embed", json={"text": prompted})
        response.raise_for_status()
        return response.json()["embedding"]
