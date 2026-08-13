"""Standalone e5 embedding server — NOT part of the Dockerized backend/EC2
deployment (no Dockerfile stage, no docker-compose.yaml service, not touched
by scripts/deploy-aliases.sh). Runs directly on the home Mac — the same box
already running Ollama — and is reached from the EC2 backend the same way
Ollama is: a Cloudflare Tunnel + Access Service Auth policy in front of it,
called by shylock_trial.adapter.outbound.client.local_embedding_client.py.

Why this exists instead of loading the model in-process on the EC2 backend:
measured directly on the production EC2 instance, in-process CPU inference
was ~20-26x slower than Cohere's API (mean 7.5s, p95 29s) — see
_docs/local-embedding-hosting-options.md and local_embedding_client.py's
module docstring. Apple Silicon inference measured ~580x faster than that
EC2 CPU number, so this server exists to put the actual inference back on
Apple Silicon and only cross the network for the (small, ~1024-float) result.

Run on the Mac (uses this repo's backend/.venv — sentence-transformers is
already in requirements.prod.txt, no separate install needed). Named
embed_main.py to match the main.py/auth_main.py "one entrypoint file per
running service" convention (see CLAUDE.md), even though — unlike those
two — this one never runs inside Docker/EC2:
    cd backend
    .venv/bin/uvicorn embed_main:app --host 0.0.0.0 --port 8001

Then route a Cloudflare Tunnel to http://localhost:8001, same pattern as the
existing Ollama tunnel (ollama.shylock-trial.xyz) — see how that one's
`cloudflared` config/Access policy was set up and repeat it for this port
with a new hostname (LOCAL_EMBEDDING_BASE_URL, e.g. embed.shylock-trial.xyz).
This server has no authentication of its own — same trust model as Ollama's
/api/chat, relies entirely on Cloudflare Access in front of it. Don't expose
port 8001 directly (router port-forward, public IP) without that in place.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from pydantic import BaseModel

from infrastructure.config import get_settings

_model = None  # loaded once at startup — see lifespan() below


def _load_model():
    global _model
    from sentence_transformers import SentenceTransformer

    _model = SentenceTransformer(get_settings().local_embedding_model)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    # Load at process startup, not on first request — this server's only job
    # is to always be warm, unlike the EC2 backend where lazy-loading would
    # have made sense if it were ever going to hold the model at all.
    _load_model()
    yield


app = FastAPI(
    title="Shylock Local Embedding Server",
    description="Home-Mac e5 embedding endpoint for shylock_trial's local-embedding fallback chain.",
    lifespan=lifespan,
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)


class EmbedRequest(BaseModel):
    text: str


class EmbedResponse(BaseModel):
    embedding: list[float]


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "model": get_settings().local_embedding_model}


@app.post("/embed", response_model=EmbedResponse)
async def embed(req: EmbedRequest) -> EmbedResponse:
    # Deliberately dumb: caller (local_embedding_client.py) decides whether
    # the text needs the e5-instruct "Instruct: ...\nQuery: ..." wrapper —
    # this endpoint just embeds whatever string it's given, same division of
    # responsibility as Ollama's /api/chat not knowing about Portia prompts.
    vector = _model.encode([req.text], normalize_embeddings=True)[0]
    return EmbedResponse(embedding=vector.tolist())
