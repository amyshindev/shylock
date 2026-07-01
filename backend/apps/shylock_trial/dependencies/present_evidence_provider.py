from fastapi import Depends

from shylock_trial.adapter.outbound.client.portia_agent_client import PortiaAgentClient
from shylock_trial.app.ports.input.present_evidence_use_case import PresentEvidenceUseCase
from shylock_trial.app.ports.output.trial_progression_port import TrialProgressionPort
from shylock_trial.app.use_cases.present_evidence_interactor import PresentEvidenceInteractor
from shylock_trial.dependencies.trial_progression_provider import get_trial_progression_repository


def get_portia_agent_client() -> PortiaAgentClient:
    return PortiaAgentClient()


def get_present_evidence_use_case(
    trial_port: TrialProgressionPort = Depends(get_trial_progression_repository),
    portia_agent: PortiaAgentClient = Depends(get_portia_agent_client),
) -> PresentEvidenceUseCase:
    return PresentEvidenceInteractor(trial_port=trial_port, portia_agent=portia_agent)
