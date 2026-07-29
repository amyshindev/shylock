"""One-off batch: play_lines -> play_chunks.

Groups play_lines into consecutive-same-speaker chunks, asks Haiku to
paraphrase each chunk into plain modern English, embeds the paraphrase (not
the archaic original) with Cohere, and inserts into play_chunks.

search_folger compares a modern-English query (Portia's logical flaw, also
modern English) against this paraphrase embedding — not the Early Modern
English original, which rarely embeds close enough to a modern query to
surface in the top-k. See tubal_agent_client.py for the read side.

Run from backend/ (needs DATABASE_URL, ANTHROPIC_API_KEY, COHERE_API_KEY):
    python -m shylock_trial.adapter.outbound.seeding.seed_play_chunks
"""

from __future__ import annotations

import asyncio
import logging

import anthropic
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.asyncio_compat import run_async
from infrastructure.config import get_settings
from infrastructure.database import get_session_factory
from shylock_trial.adapter.outbound.client.evidence_embedding_client import EvidenceEmbeddingClient
from shylock_trial.adapter.outbound.orm.play_line_orm import PlayChunkOrm, PlayLineOrm

logger = logging.getLogger(__name__)

PARAPHRASE_MODEL_ID = "claude-haiku-4-5-20251001"
PARAPHRASE_CONCURRENCY = 8
EMBED_BATCH_SIZE = 90

PARAPHRASE_SYSTEM_PROMPT = """\
Paraphrase the following line(s) from Shakespeare's The Merchant of Venice \
into concise, plain modern English. Preserve the speaker's meaning and \
intent exactly — don't add interpretation, analysis, or commentary. Output \
only the paraphrase itself, one to two sentences, no preamble."""


class _Chunk:
    __slots__ = ("ftln_start", "ftln_end", "speaker", "act_scene", "text")

    def __init__(self, ftln_start: int, speaker: str, act_scene: str) -> None:
        self.ftln_start = ftln_start
        self.ftln_end = ftln_start
        self.speaker = speaker
        self.act_scene = act_scene
        self.text = ""


async def _fetch_lines(session: AsyncSession) -> list[PlayLineOrm]:
    result = await session.execute(select(PlayLineOrm).order_by(PlayLineOrm.ftln))
    return list(result.scalars().all())


def _group_into_chunks(lines: list[PlayLineOrm]) -> list[_Chunk]:
    chunks: list[_Chunk] = []
    current: _Chunk | None = None
    for line in lines:
        if current is None or line.speaker != current.speaker:
            if current is not None:
                chunks.append(current)
            current = _Chunk(line.ftln, line.speaker, line.act_scene)
            current.text = line.text
        else:
            current.ftln_end = line.ftln
            current.text = f"{current.text} {line.text}"
    if current is not None:
        chunks.append(current)
    return chunks


async def _paraphrase_all(chunks: list[_Chunk]) -> list[str]:
    settings = get_settings()
    client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key_plain())
    semaphore = asyncio.Semaphore(PARAPHRASE_CONCURRENCY)
    done = 0

    async def paraphrase_one(chunk: _Chunk) -> str:
        nonlocal done
        async with semaphore:
            response = await client.messages.create(
                model=PARAPHRASE_MODEL_ID,
                max_tokens=200,
                system=PARAPHRASE_SYSTEM_PROMPT,
                messages=[{"role": "user", "content": f"{chunk.speaker}: {chunk.text}"}],
            )
            done += 1
            if done % 50 == 0:
                logger.info("Paraphrased %d / %d chunks...", done, len(chunks))
            return "".join(block.text for block in response.content if block.type == "text").strip()

    return await asyncio.gather(*(paraphrase_one(chunk) for chunk in chunks))


async def _embed_all(paraphrases: list[str]) -> list[list[float]]:
    embedder = EvidenceEmbeddingClient()
    vectors: list[list[float]] = []
    for i in range(0, len(paraphrases), EMBED_BATCH_SIZE):
        batch = paraphrases[i : i + EMBED_BATCH_SIZE]
        vectors.extend(await embedder.embed_texts(batch))
        logger.info("Embedded %d / %d paraphrases...", min(i + EMBED_BATCH_SIZE, len(paraphrases)), len(paraphrases))
    return vectors


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    session_factory = get_session_factory()

    async with session_factory() as session:
        lines = await _fetch_lines(session)
        if not lines:
            raise RuntimeError("play_lines is empty — seed the base corpus first.")
        chunks = _group_into_chunks(lines)
        logger.info("Grouped %d lines into %d chunks.", len(lines), len(chunks))

        paraphrases = await _paraphrase_all(chunks)
        vectors = await _embed_all(paraphrases)

        for chunk, paraphrase, vector in zip(chunks, paraphrases, vectors, strict=True):
            session.add(
                PlayChunkOrm(
                    ftln_start=chunk.ftln_start,
                    ftln_end=chunk.ftln_end,
                    speaker=chunk.speaker,
                    act_scene=chunk.act_scene,
                    text=chunk.text,
                    paraphrase=paraphrase,
                    embedding=vector,
                )
            )
        await session.commit()
    logger.info("Seeded %d play chunks.", len(chunks))


if __name__ == "__main__":
    run_async(main())
