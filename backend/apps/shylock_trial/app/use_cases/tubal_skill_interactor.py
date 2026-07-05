from uuid import UUID

from shylock_trial.adapter.outbound.client.tubal_agent_client import TubalAgentClient
from shylock_trial.adapter.outbound.client.tubal_enhancement_client import TubalEnhancementClient
from shylock_trial.app.constants.scene_catalog import fallback_scene_dialogue, get_scene_template
from shylock_trial.app.constants.scene_choices import (
    ChoiceEffect,
    apply_skill_resources,
    get_skill_effect,
)
from shylock_trial.app.constants.scene_progression import resolve_next_scene_index
from shylock_trial.app.constants.tubal_enhancement_map import TUBAL_ENHANCEMENT_MAP
from shylock_trial.app.dtos.scene_dialogue_dto import DialogueLineKind, SceneDialoguePromptDto
from shylock_trial.app.dtos.tubal_agent_dto import TubalAgentResult
from shylock_trial.app.dtos.tubal_skill_dto import TubalSkillInputDto, TubalSkillResultDto
from shylock_trial.app.ports.input.portia_response_use_case import PortiaResponseUseCase
from shylock_trial.app.ports.input.tubal_skill_use_case import TubalSkillUseCase
from shylock_trial.app.ports.output.trial_progression_port import TrialProgressionPort
from shylock_trial.app.utils.trial_metadata_store import append_unique
from shylock_trial.domain.entities.trial_entity import Trial
from shylock_trial.domain.value_objects.dp_score_vo import DpScore
from shylock_trial.domain.value_objects.hp_score_vo import HpScore


class TubalSkillInteractor(TubalSkillUseCase):
    def __init__(
        self,
        trial_port: TrialProgressionPort,
        tubal_agent: TubalAgentClient,
        portia: PortiaResponseUseCase,
        tubal_enhancement: TubalEnhancementClient,
    ) -> None:
        self._trial_port = trial_port
        self._tubal_agent = tubal_agent
        self._portia = portia
        self._tubal_enhancement = tubal_enhancement

    async def invoke_tubal(self, input_dto: TubalSkillInputDto) -> TubalSkillResultDto:
        trial = await self._require_trial(input_dto.trial_id)

        tubal_effect = get_skill_effect("tubal")
        next_hp, next_dp = apply_skill_resources(
            trial.hp.value,
            trial.dp.value,
            tubal_effect,
        )
        trial.hp = HpScore(next_hp)
        trial.dp = DpScore(next_dp)

        scene_id, portia_claim = self._resolve_scene_context(trial, input_dto)
        agent_result = await self._tubal_agent.agentic_loop(
            portia_claim=portia_claim,
            scene_id=scene_id,
        )

        if not agent_result.success:
            revert_hp, revert_dp = apply_skill_resources(
                trial.hp.value,
                trial.dp.value,
                ChoiceEffect(-tubal_effect.dp_delta, -tubal_effect.hp_cost),
            )
            trial.hp = HpScore(revert_hp)
            trial.dp = DpScore(revert_dp)
        else:
            trial.tubal_used_scenes = append_unique(trial.tubal_used_scenes, scene_id)
            await self._apply_tubal_enhancement(trial, scene_id, agent_result)

        trial = await self._trial_port.save(trial)
        trial = await self._prefetch_next_scene_dialogue(trial)

        return TubalSkillResultDto(
            trial_id=trial.trial_id,
            dp=trial.dp.value,
            hp=trial.hp.value,
            agent=agent_result,
            tubal_enhanced_choices=dict(trial.tubal_enhanced_choices),
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

    async def _apply_tubal_enhancement(
        self,
        trial: Trial,
        scene_id: str,
        agent_result: TubalAgentResult,
    ) -> None:
        target_choice_id = TUBAL_ENHANCEMENT_MAP.get(scene_id)
        if not target_choice_id or not agent_result.passage:
            return

        template = get_scene_template(trial.scene_index)
        original_choice = template.canonical_choice_texts.get(target_choice_id)
        if not original_choice:
            return

        try:
            enhanced = await self._tubal_enhancement.generate_enhanced_choice(
                passage=agent_result.passage,
                original_choice=original_choice,
                scene_id=scene_id,
                speaker=agent_result.speaker or "",
            )
            trial.tubal_enhanced_choices[target_choice_id] = enhanced
        except Exception:
            return

    async def _require_trial(self, trial_id: UUID) -> Trial:
        trial = await self._trial_port.find_by_id(trial_id)
        if trial is None:
            raise ValueError(f"Trial not found: {trial_id}")
        return trial

    async def _prefetch_next_scene_dialogue(self, trial: Trial) -> Trial:
        next_index = resolve_next_scene_index(trial.scene_index, trial.dp.value)
        if next_index is None or next_index in trial.scene_dialogues:
            return trial

        try:
            result = await self._portia.generate_scene_dialogue(
                SceneDialoguePromptDto(
                    trial_id=trial.trial_id,
                    scene_index=next_index,
                    dp=trial.dp.value,
                    choice_history=tuple(trial.choice_history),
                )
            )
            content = result.content
        except Exception:
            content = fallback_scene_dialogue(next_index)

        trial.scene_dialogues[next_index] = content
        return await self._trial_port.save(trial)
