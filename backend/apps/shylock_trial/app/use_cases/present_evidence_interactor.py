from uuid import UUID

from shylock_trial.adapter.outbound.client.portia_agent_client import PortiaAgentClient
from shylock_trial.app.constants.press_present_config import PRESS_PRESENT_BY_SCENE_ID
from shylock_trial.app.constants.scene_catalog import get_scene_template
from shylock_trial.app.dtos.present_evidence_dto import PresentEvidenceInputDto, PresentEvidenceResultDto
from shylock_trial.app.ports.input.present_evidence_use_case import PresentEvidenceUseCase
from shylock_trial.app.ports.output.trial_progression_port import TrialProgressionPort
from shylock_trial.domain.entities.trial_entity import Trial


class PresentEvidenceInteractor(PresentEvidenceUseCase):
    def __init__(
        self,
        trial_port: TrialProgressionPort,
        portia_agent: PortiaAgentClient,
    ) -> None:
        self._trial_port = trial_port
        self._portia_agent = portia_agent

    async def present_evidence(
        self,
        input_dto: PresentEvidenceInputDto,
    ) -> PresentEvidenceResultDto:
        trial = await self._require_trial(input_dto.trial_id)
        config = PRESS_PRESENT_BY_SCENE_ID.get(input_dto.scene_id)
        if config is None:
            raise ValueError(f"Scene does not support present-evidence: {input_dto.scene_id}")

        template = get_scene_template(trial.scene_index)
        if template.scene_id != input_dto.scene_id:
            raise ValueError(
                f"Trial is on scene {template.scene_id}, not {input_dto.scene_id}"
            )

        statement = next(
            (t for t in config.testimony if t.statement_id == config.contradiction.statement_id),
            None,
        )
        if statement is None:
            raise ValueError("Press/Present contradiction statement not configured")

        evidence_text = input_dto.evidence_text.strip()
        if not evidence_text:
            raise ValueError("evidence_text is required")

        agent_result = await self._portia_agent.agentic_loop(
            scene_id=input_dto.scene_id,
            statement_id=config.contradiction.statement_id,
            statement_text=statement.text,
            evidence_id=input_dto.evidence_id,
            evidence_text=evidence_text,
        )

        trial.portia_hp = trial.portia_hp.apply_delta(agent_result.portia_hp_change)
        trial = await self._trial_port.save(trial)

        return PresentEvidenceResultDto(
            trial_id=trial.trial_id,
            shylock_hp=trial.shylock_hp.value,
            dp=trial.dp.value,
            portia_hp=trial.portia_hp.value,
            contradiction_valid=agent_result.contradiction_valid,
            portia_response=agent_result.portia_response,
            portia_hp_change=agent_result.portia_hp_change,
        )

    async def _require_trial(self, trial_id: UUID) -> Trial:
        trial = await self._trial_port.find_by_id(trial_id)
        if trial is None:
            raise ValueError(f"Trial not found: {trial_id}")
        return trial
