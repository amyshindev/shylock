from fastapi import Depends

from shylock_trial.adapter.outbound.client.tubal_agent_client import TubalAgentClient
from shylock_trial.app.ports.input.evidence_search_use_case import EvidenceSearchUseCase
from shylock_trial.dependencies.evidence_search_provider import get_evidence_search_use_case


def get_tubal_agent_client(
    evidence_search: EvidenceSearchUseCase = Depends(get_evidence_search_use_case),
) -> TubalAgentClient:
    return TubalAgentClient(evidence_search=evidence_search)
