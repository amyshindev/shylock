"""
Seed Folger MV.xml play lines + Cohere embeddings into Postgres.

From backend/:
    python seed_play_lines.py

Requires DATABASE_URL and COHERE_API_KEY in .env or backend/.env.
Run alembic migrations first.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "apps"))
sys.path.insert(0, str(ROOT))

from infrastructure.asyncio_compat import run_async
from shylock_trial.adapter.outbound.seeding.evidence_search_corpus_seeder import main

if __name__ == "__main__":
    run_async(main())
