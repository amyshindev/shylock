from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.config import get_settings
from infrastructure.database import get_optional_db_session
from shylock_trial.adapter.outbound.memory.trial_progression_repository import (
    InMemoryTrialProgressionRepository,
)
from shylock_trial.adapter.outbound.pg.trial_progression_repository import TrialProgressionPgRepository
from shylock_trial.app.ports.input.evidence_search_use_case import EvidenceSearchUseCase
from shylock_trial.app.ports.input.portia_response_use_case import PortiaResponseUseCase
from shylock_trial.app.ports.input.trial_progression_use_case import TrialProgressionUseCase
from shylock_trial.app.ports.output.trial_progression_port import TrialProgressionPort
from shylock_trial.app.use_cases.trial_progression_interactor import TrialProgressionInteractor
from shylock_trial.dependencies.evidence_search_provider import get_evidence_search_use_case
from shylock_trial.dependencies.portia_response_provider import get_portia_response_use_case


def get_trial_progression_repository(
    session: Annotated[AsyncSession | None, Depends(get_optional_db_session)],
) -> TrialProgressionPort:
    if get_settings().use_memory_store:
        return InMemoryTrialProgressionRepository.get_instance()
    if session is None:
        raise RuntimeError("Database session required when USE_MEMORY_STORE is disabled")
    return TrialProgressionPgRepository(session=session)


def get_trial_progression_use_case(
    port: TrialProgressionPort = Depends(get_trial_progression_repository),
    portia: PortiaResponseUseCase = Depends(get_portia_response_use_case),
    evidence: EvidenceSearchUseCase = Depends(get_evidence_search_use_case),
) -> TrialProgressionUseCase:
    return TrialProgressionInteractor(port=port, portia=portia, evidence=evidence)
