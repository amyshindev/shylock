"""
One-off batch: Folger MV.xml → PlayLine rows + pgvector embeddings.

Run from backend/ after DB migration:
    python seed_play_lines.py

Requires: DATABASE_URL, COHERE_API_KEY in .env / backend/.env
"""

from __future__ import annotations

import logging
import xml.etree.ElementTree as ET
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.asyncio_compat import run_async
from infrastructure.database import get_session_factory
from shylock_trial.adapter.outbound.client.evidence_embedding_client import EvidenceEmbeddingClient
from shylock_trial.adapter.outbound.orm.play_line_orm import PlayLineOrm

logger = logging.getLogger(__name__)

FOLGER_XML_PATH = Path(__file__).parent / "MV.xml"
TEI_NS = "http://www.tei-c.org/ns/1.0"
TEI = f"{{{TEI_NS}}}"


def _ftln_ref_to_int(ftln_ref: str) -> int | None:
    """Map Folger act.scene.line (e.g. 1.1.1) to a stable integer primary key."""
    parts = ftln_ref.strip().split(".")
    if len(parts) != 3:
        return None
    try:
        act, scene, line = (int(p) for p in parts)
    except ValueError:
        return None
    return act * 1_000_000 + scene * 1_000 + line


def _speaker_from_sp(sp: ET.Element) -> str:
    who = sp.get("who", "")
    if who.startswith("#") and who.endswith("_MV"):
        return who[1:-3]
    speaker_el = sp.find(f"{TEI}speaker")
    if speaker_el is not None:
        return "".join(speaker_el.itertext()).strip()
    return ""


def _line_text_from_milestone(parent: ET.Element, start_idx: int) -> tuple[str, int]:
    """Collect word/punctuation text after an ftln milestone until the next one."""
    parts: list[str] = []
    i = start_idx + 1
    children = list(parent)
    while i < len(children):
        child = children[i]
        if child.tag == f"{TEI}milestone" and child.get("unit") == "ftln":
            break
        if child.tag in (f"{TEI}w", f"{TEI}pc"):
            if child.text:
                parts.append(child.text)
        elif child.tag == f"{TEI}c" and child.text:
            parts.append(child.text)
        i += 1
    return "".join(parts).strip(), i


def parse_play_lines() -> list[dict]:
    if not FOLGER_XML_PATH.is_file():
        raise FileNotFoundError(f"Folger XML not found: {FOLGER_XML_PATH}")

    tree = ET.parse(FOLGER_XML_PATH)
    root = tree.getroot()
    body = root.find(f".//{TEI}body")
    if body is None:
        raise ValueError("No <body> element in Folger XML")

    records: list[dict] = []
    seen_ftln: set[int] = set()

    for sp in body.iter(f"{TEI}sp"):
        speaker = _speaker_from_sp(sp)
        for block in sp.iter(f"{TEI}ab"):
            children = list(block)
            i = 0
            while i < len(children):
                el = children[i]
                if el.tag != f"{TEI}milestone" or el.get("unit") != "ftln":
                    i += 1
                    continue

                ftln_ref = el.get("n", "").strip()
                ftln = _ftln_ref_to_int(ftln_ref)
                if ftln is None or ftln in seen_ftln:
                    i += 1
                    continue

                text, next_i = _line_text_from_milestone(block, i)
                i = next_i
                if not text:
                    continue

                act_scene = ".".join(ftln_ref.split(".")[:2]) if ftln_ref else ""
                seen_ftln.add(ftln)
                records.append({
                    "ftln": ftln,
                    "speaker": speaker,
                    "text": text,
                    "act_scene": act_scene,
                })

    records.sort(key=lambda row: row["ftln"])
    return records


EMBED_BATCH_SIZE = 90  # Cohere limit 96 with margin


async def seed_play_lines(session: AsyncSession, records: list[dict]) -> int:
    embedder = EvidenceEmbeddingClient()
    all_vectors: list[list[float]] = []

    for i in range(0, len(records), EMBED_BATCH_SIZE):
        batch = records[i : i + EMBED_BATCH_SIZE]
        texts = [str(row.get("text", "")) for row in batch]
        vectors = await embedder.embed_texts(texts)
        all_vectors.extend(vectors)
        logger.info(
            "Embedded %d / %d lines...",
            min(i + EMBED_BATCH_SIZE, len(records)),
            len(records),
        )

    for row, vector in zip(records, all_vectors, strict=True):
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
    logger.info("Parsing Merchant of Venice corpus from %s", FOLGER_XML_PATH)
    records = parse_play_lines()
    if not records:
        raise RuntimeError(
            "Parsed 0 lines — check MV.xml format or parser logic."
        )
    logger.info("Parsed %s lines.", len(records))

    session_factory = get_session_factory()
    async with session_factory() as session:
        count = await seed_play_lines(session, records)
    logger.info("Seeded %s play lines.", count)


if __name__ == "__main__":
    run_async(main())


def run() -> None:
    """Console script entry point (after pip install -e .)."""
    run_async(main())
