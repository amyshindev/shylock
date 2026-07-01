from uuid import UUID

from shylock_trial.adapter.outbound.client.tubal_agent_client import TubalAgentClient
from shylock_trial.app.constants.game_balance import SKILL_TUBAL_COST
from shylock_trial.app.constants.scene_catalog import get_scene_template
from shylock_trial.app.dtos.scene_dialogue_dto import DialogueLineKind
from shylock_trial.app.dtos.tubal_skill_dto import TubalSkillInputDto, TubalSkillResultDto
from shylock_trial.app.ports.input.tubal_skill_use_case import TubalSkillUseCase
from shylock_trial.app.ports.output.trial_progression_port import TrialProgressionPort
from shylock_trial.domain.entities.trial_entity import Trial


class TubalSkillInteractor(TubalSkillUseCase):
    def __init__(
        self,
        trial_port: TrialProgressionPort,
        tubal_agent: TubalAgentClient,
    ) -> None:
        self._trial_port = trial_port
        self._tubal_agent = tubal_agent

    async def invoke_tubal(self, input_dto: TubalSkillInputDto) -> TubalSkillResultDto:
        trial = await self._require_trial(input_dto.trial_id)

        if trial.dp.value <= SKILL_TUBAL_COST:
            raise ValueError(
                f"Insufficient DP for Tubal skill (need > {SKILL_TUBAL_COST}, have {trial.dp.value})"
            )

        trial.dp = trial.dp.apply_delta(-SKILL_TUBAL_COST)

        scene_id, portia_claim = self._resolve_scene_context(trial, input_dto)
        agent_result = await self._tubal_agent.agentic_loop(
            portia_claim=portia_claim,
            scene_id=scene_id,
        )

        trial = await self._trial_port.save(trial)

        return TubalSkillResultDto(
            trial_id=trial.trial_id,
            dp=trial.dp.value,
            shylock_hp=trial.shylock_hp.value,
            portia_hp=trial.portia_hp.value,
            agent=agent_result,
        )

    def _resolve_scene_context(
        self,
        trial: Trial,
        input_dto: TubalSkillInputDto,
    ) -> tuple[str, str]:
        template = get_scene_template(trial.scene_index)
        scene_id = input_dto.scene_id or template.scene_id

        if input_dto.portia_claim and input_dto.portia_claim.strip():
            return scene_id, input_dto.portia_claim.strip()

        cached = trial.scene_dialogues.get(trial.scene_index)
        if cached and cached.challenge_text:
            return scene_id, cached.challenge_text

        if template.canonical_challenge_text:
            return scene_id, template.canonical_challenge_text

        if cached and cached.lines:
            portia_lines = [
                line.text
                for line in cached.lines
                if line.kind == DialogueLineKind.SPEECH
            ]
            if portia_lines:
                return scene_id, portia_lines[-1]

        return scene_id, template.brief

    async def _require_trial(self, trial_id: UUID) -> Trial:
        trial = await self._trial_port.find_by_id(trial_id)
        if trial is None:
            raise ValueError(f"Trial not found: {trial_id}")
        return trial
