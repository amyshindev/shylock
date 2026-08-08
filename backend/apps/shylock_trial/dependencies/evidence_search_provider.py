from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.config import get_settings
from infrastructure.database import get_corpus_db_session
from shylock_trial.adapter.outbound.memory.evidence_search_repository import (
    InMemoryEvidenceSearchRepository,
)
from shylock_trial.adapter.outbound.pg.evidence_search_repository import EvidenceSearchPgRepository
from shylock_trial.adapter.outbound.pg.fallback_evidence_search_repository import (
    FallbackEvidenceSearchRepository,
)
from shylock_trial.adapter.outbound.pg.local_evidence_search_repository import (
    LocalEvidenceSearchPgRepository,
)
from shylock_trial.app.ports.input.evidence_search_use_case import EvidenceSearchUseCase
from shylock_trial.app.ports.output.evidence_search_port import EvidenceSearchPort
from shylock_trial.app.use_cases.evidence_search_interactor import EvidenceSearchInteractor


def get_evidence_search_repository(
    session: Annotated[AsyncSession | None, Depends(get_corpus_db_session)],
) -> EvidenceSearchPort:
    if session is None:
        return InMemoryEvidenceSearchRepository.get_instance()

    cohere = EvidenceSearchPgRepository(session=session)
    # EMBEDDING_PROVIDER=local wraps the local e5 repository with a
    # Cohere fallback (never bare — local_embedding_client.py calls a home-Mac
    # server over a Cloudflare Tunnel, and a home network/Mac can't be relied
    # on to always be reachable, same reasoning as the Ollama fallback).
    # Anything other than "local" (including unset) is the original
    # Cohere-only path, unchanged.
    if get_settings().embedding_provider == "local":
        return FallbackEvidenceSearchRepository(
            primary=LocalEvidenceSearchPgRepository(session=session), fallback=cohere
        )
    return cohere


def get_evidence_search_use_case(
    port: EvidenceSearchPort = Depends(get_evidence_search_repository),
) -> EvidenceSearchUseCase:
    return EvidenceSearchInteractor(port=port)
