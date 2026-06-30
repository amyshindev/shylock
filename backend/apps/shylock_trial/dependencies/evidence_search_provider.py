from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import get_settings
from core.database import get_optional_db_session
from shylock_trial.adapter.outbound.memory.evidence_search_repository import (
    InMemoryEvidenceSearchRepository,
)
from shylock_trial.adapter.outbound.memory.trial_progression_repository import (
    InMemoryTrialProgressionRepository,
)
from shylock_trial.adapter.outbound.pg.evidence_search_repository import EvidenceSearchPgRepository
from shylock_trial.app.ports.input.evidence_search_use_case import EvidenceSearchUseCase
from shylock_trial.app.ports.output.evidence_search_port import EvidenceSearchPort
from shylock_trial.app.use_cases.evidence_search_interactor import EvidenceSearchInteractor


def get_evidence_search_repository(
    session: Annotated[AsyncSession | None, Depends(get_optional_db_session)],
) -> EvidenceSearchPort:
    if get_settings().use_memory_store:
        return InMemoryEvidenceSearchRepository.get_instance()
    if session is None:
        raise RuntimeError("Database session required when USE_MEMORY_STORE is disabled")
    return EvidenceSearchPgRepository(session=session)


def get_evidence_search_use_case(
    port: EvidenceSearchPort = Depends(get_evidence_search_repository),
) -> EvidenceSearchUseCase:
    return EvidenceSearchInteractor(port=port)
