"""
One-off batch: Folger Digital Texts API (MV) → PlayLine rows + pgvector embeddings.

Run manually after DB migration:
    python -m shylock_trial.adapter.outbound.seeding.evidence_search_corpus_seeder
"""

from __future__ import annotations

import asyncio
import logging

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_session_factory
from shylock_trial.adapter.outbound.client.evidence_embedding_client import EvidenceEmbeddingClient
from shylock_trial.adapter.outbound.orm.play_line_orm import PlayLineOrm

logger = logging.getLogger(__name__)

FOLGER_TEXT_URL = "https://www.folgerdigitaltexts.org/api/text/MV"


async def fetch_play_lines() -> list[dict]:
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.get(FOLGER_TEXT_URL)
        response.raise_for_status()
        payload = response.json()
    # TODO: normalize Folger API response into ftln/speaker/text/act_scene records
    if not isinstance(payload, list):
        raise ValueError(
            "Unexpected Folger API response shape. "
            "Inspect payload and update the parser before re-running."
        )
    return payload


async def seed_play_lines(session: AsyncSession, records: list[dict]) -> int:
    embedder = EvidenceEmbeddingClient()
    texts = [str(row.get("text", "")) for row in records]
    vectors = await embedder.embed_texts(texts)

    for row, vector in zip(records, vectors, strict=False):
        session.add(
            PlayLineOrm(
                ftln=int(row["ftln"]),
                speaker=str(row.get("speaker", "")),
                text=str(row.get("text", "")),
                act_scene=str(row.get("act_scene", "")),
                embedding=vector,
            )
        )
    await session.commit()
    return len(records)


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    logger.info("Fetching Merchant of Venice corpus from Folger API...")
    records = await fetch_play_lines()
    logger.info("Fetched %s raw records (verify act/scene distribution manually).", len(records))

    session_factory = get_session_factory()
    async with session_factory() as session:
        count = await seed_play_lines(session, records)
    logger.info("Seeded %s play lines.", count)


if __name__ == "__main__":
    asyncio.run(main())
