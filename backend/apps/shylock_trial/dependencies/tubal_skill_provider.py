from fastapi import Depends

from shylock_trial.adapter.outbound.client.tubal_agent_client import TubalAgentClient
from shylock_trial.app.ports.input.tubal_skill_use_case import TubalSkillUseCase
from shylock_trial.app.ports.output.trial_progression_port import TrialProgressionPort
from shylock_trial.app.use_cases.tubal_skill_interactor import TubalSkillInteractor
from shylock_trial.app.ports.input.portia_response_use_case import PortiaResponseUseCase
from shylock_trial.adapter.outbound.client.tubal_enhancement_client import TubalEnhancementClient
from shylock_trial.dependencies.portia_response_provider import get_portia_response_use_case
from shylock_trial.dependencies.trial_progression_provider import get_trial_progression_repository
from shylock_trial.dependencies.tubal_agent_provider import get_tubal_agent_client
from shylock_trial.dependencies.tubal_enhancement_provider import get_tubal_enhancement_client


def get_tubal_skill_use_case(
    trial_port: TrialProgressionPort = Depends(get_trial_progression_repository),
    tubal_agent: TubalAgentClient = Depends(get_tubal_agent_client),
    portia: PortiaResponseUseCase = Depends(get_portia_response_use_case),
    tubal_enhancement: TubalEnhancementClient = Depends(get_tubal_enhancement_client),
) -> TubalSkillUseCase:
    return TubalSkillInteractor(
        trial_port=trial_port,
        tubal_agent=tubal_agent,
        portia=portia,
        tubal_enhancement=tubal_enhancement,
    )
