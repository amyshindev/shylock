from uuid import UUID, uuid4
import asyncio

from shylock_trial.adapter.outbound.client.tubal_enhancement_client import TubalEnhancementClient
from shylock_trial.app.constants.ending_type_map import resolve_ending_type
from shylock_trial.app.constants.game_balance import (
    SHYLOCK_DP_START,
    SHYLOCK_HP_START,
)
from shylock_trial.app.constants.scene_catalog import fallback_scene_dialogue
from shylock_trial.app.constants.scene_progression import (
    CROWD_JEERS_SCENE_INDEX,
    resolve_next_scene_index,
)
from shylock_trial.app.constants.scene_choices import (
    apply_skill_resources,
    compute_choice_dp_gain,
    get_choice_effect,
    get_choice_evidence_id,
    get_skill_effect,
)
from shylock_trial.app.constants.tubal_enhancement_map import TUBAL_ENHANCEMENT_DP_BONUS
from shylock_trial.app.dtos.evidence_search_dto import EvidenceSearchInputDto
from shylock_trial.app.dtos.portia_response_dto import PortiaResponsePromptDto
from shylock_trial.app.dtos.scene_dialogue_dto import (
    SceneDialogueContent,
    SceneDialoguePromptDto,
)
from shylock_trial.app.dtos.trial_progression_dto import (
    AdvanceSceneResultDto,
    GenerateEndingResultDto,
    LauncelotSkillResultDto,
    StartTrialResultDto,
    SubmitChoiceInputDto,
    SubmitChoiceResultDto,
    VeniceParadoxSkillResultDto,
)
from shylock_trial.app.ports.input.evidence_search_use_case import EvidenceSearchUseCase
from shylock_trial.app.ports.input.portia_response_use_case import PortiaResponseUseCase
from shylock_trial.app.ports.input.trial_progression_use_case import TrialProgressionUseCase
from shylock_trial.app.ports.output.trial_progression_port import TrialProgressionPort
from shylock_trial.domain.entities.trial_entity import Trial, TrialPhase
from shylock_trial.domain.value_objects.dp_score_vo import DpScore
from shylock_trial.domain.value_objects.hp_score_vo import HpScore
from shylock_trial.app.utils.trial_metadata_store import append_unique


class TrialProgressionInteractor(TrialProgressionUseCase):
    def __init__(
        self,
        port: TrialProgressionPort,
        portia: PortiaResponseUseCase,
        evidence: EvidenceSearchUseCase,
        tubal_enhancement: TubalEnhancementClient,
    ) -> None:
        self._port = port
        self._portia = portia
        self._evidence = evidence
        self._tubal_enhancement = tubal_enhancement

    async def start(self) -> StartTrialResultDto:
        trial = Trial(
            trial_id=uuid4(),
            scene_index=0,
            dp=DpScore(SHYLOCK_DP_START),
            hp=HpScore(SHYLOCK_HP_START),
            choice_history=[],
            phase=TrialPhase.IN_PROGRESS,
        )
        trial = await self._port.create(trial)
        scene_dialogue = await self._ensure_scene_dialogue(trial, 0)
        trial = await self._port.save(trial)

        return StartTrialResultDto(
            trial_id=trial.trial_id,
            scene_index=trial.scene_index,
            dp=trial.dp.value,
            hp=trial.hp.value,
            phase=trial.phase,
            scene_dialogue=scene_dialogue,
        )

    async def submit_choice(self, input_dto: SubmitChoiceInputDto) -> SubmitChoiceResultDto:
        trial = await self._require_trial(input_dto.trial_id)

        effect = get_choice_effect(input_dto.choice_id)
        was_enhanced = input_dto.choice_id in trial.tubal_enhanced_choices
        dp_bonus = TUBAL_ENHANCEMENT_DP_BONUS if was_enhanced else 0
        if was_enhanced:
            del trial.tubal_enhanced_choices[input_dto.choice_id]

        dp_gain, shield_consumed = compute_choice_dp_gain(
            trial.hp.value,
            effect.dp_delta,
            dp_bonus=dp_bonus,
            venice_dp_shield=trial.venice_dp_shield,
        )
        if shield_consumed:
            trial.venice_dp_shield = False

        trial.choice_history.append(input_dto.choice_id)
        trial.dp = trial.dp.apply_delta(dp_gain)
        trial.hp = trial.hp.apply_delta(-effect.hp_cost)

        evidence_id = get_choice_evidence_id(input_dto.choice_id)
        if evidence_id:
            trial.presented_evidence = append_unique(trial.presented_evidence, evidence_id)

        portia_prompt = self._build_portia_prompt(
            trial,
            context=f"choice:{input_dto.choice_id}",
            request_type="reaction",
        )
        next_scene_index = resolve_next_scene_index(trial.scene_index, trial.dp.value)
        if next_scene_index is not None:
            portia, _ = await asyncio.gather(
                self._portia.generate(portia_prompt),
                self._ensure_scene_dialogue(trial, next_scene_index),
            )
        else:
            portia = await self._portia.generate(portia_prompt)

        is_ending = False

        trial = await self._port.save(trial)

        return SubmitChoiceResultDto(
            trial_id=trial.trial_id,
            scene_index=trial.scene_index,
            dp=trial.dp.value,
            hp=trial.hp.value,
            phase=trial.phase,
            portia_response=portia.text,
            ending_type=None,
            is_ending=is_ending,
            tubal_enhanced_choices=dict(trial.tubal_enhanced_choices),
            venice_dp_shield=trial.venice_dp_shield,
        )

    async def advance_scene(self, trial_id: UUID) -> AdvanceSceneResultDto:
        trial = await self._require_trial(trial_id)
        next_index = resolve_next_scene_index(trial.scene_index, trial.dp.value)
        if next_index is None:
            raise ValueError("No further scenes to advance")
        trial.scene_index = next_index
        scene_dialogue = await self._ensure_scene_dialogue(trial, trial.scene_index)
        trial = await self._port.save(trial)

        return AdvanceSceneResultDto(
            trial_id=trial.trial_id,
            scene_index=trial.scene_index,
            scene_data={"scene_index": trial.scene_index},
            scene_dialogue=scene_dialogue,
        )

    async def generate_ending(self, trial_id: UUID) -> GenerateEndingResultDto:
        trial = await self._require_trial(trial_id)
        ending_type = resolve_ending_type(dp=trial.dp.value)

        ending = await self._portia.generate(
            self._build_portia_prompt(
                trial,
                context=f"final_ending:{ending_type.value}",
                request_type="ending",
            )
        )

        trial.phase = TrialPhase.ENDED
        trial.narration_text = ending.text
        trial = await self._port.save(trial)

        return GenerateEndingResultDto(
            trial_id=trial.trial_id,
            ending_type=ending_type,
            ending_text=ending.text,
            dp=trial.dp.value,
        )

    async def get_trial(self, trial_id: UUID) -> Trial:
        trial = await self._require_trial(trial_id)
        if not trial.is_ended():
            await self._ensure_scene_dialogue(trial, trial.scene_index)
            trial = await self._port.save(trial)
        return trial

    async def use_launcelot_skill(self, trial_id: UUID) -> LauncelotSkillResultDto:
        trial = await self._require_trial(trial_id)

        effect = get_skill_effect("launcelot")
        next_hp, next_dp = apply_skill_resources(
            trial.hp.value,
            trial.dp.value,
            effect,
        )
        trial.hp = HpScore(next_hp)
        trial.dp = DpScore(next_dp)
        trial = await self._port.save(trial)

        return LauncelotSkillResultDto(
            trial_id=trial.trial_id,
            dp=trial.dp.value,
            hp=trial.hp.value,
        )

    async def use_venice_paradox_skill(
        self,
        trial_id: UUID,
    ) -> VeniceParadoxSkillResultDto:
        trial = await self._require_trial(trial_id)

        if trial.venice_paradox_used:
            raise ValueError("skill_unavailable")
        if trial.scene_index <= CROWD_JEERS_SCENE_INDEX:
            raise ValueError("skill_unavailable")

        effect = get_skill_effect("venice_paradox")
        next_hp, next_dp = apply_skill_resources(
            trial.hp.value,
            trial.dp.value,
            effect,
        )
        trial.hp = HpScore(next_hp)
        trial.dp = DpScore(next_dp)
        trial.venice_paradox_used = True
        trial = await self._port.save(trial)

        return VeniceParadoxSkillResultDto(
            trial_id=trial.trial_id,
            dp=trial.dp.value,
            hp=trial.hp.value,
            venice_paradox_used=trial.venice_paradox_used,
        )

    async def start_dev_scene(self, scene_index: int, dp: int) -> StartTrialResultDto:
        trial = Trial(
            trial_id=uuid4(),
            scene_index=scene_index,
            dp=DpScore(dp),
            hp=HpScore(SHYLOCK_HP_START),
            choice_history=[],
            phase=TrialPhase.IN_PROGRESS,
        )
        trial = await self._port.create(trial)
        scene_dialogue = fallback_scene_dialogue(scene_index)
        trial.scene_dialogues[scene_index] = scene_dialogue
        trial = await self._port.save(trial)

        return StartTrialResultDto(
            trial_id=trial.trial_id,
            scene_index=trial.scene_index,
            dp=trial.dp.value,
            hp=trial.hp.value,
            phase=trial.phase,
            scene_dialogue=scene_dialogue,
        )

    async def _ensure_scene_dialogue(
        self,
        trial: Trial,
        scene_index: int,
    ) -> SceneDialogueContent:
        cached = trial.scene_dialogues.get(scene_index)
        if cached is not None:
            return cached

        try:
            result = await self._portia.generate_scene_dialogue(
                SceneDialoguePromptDto(
                    trial_id=trial.trial_id,
                    scene_index=scene_index,
                    dp=trial.dp.value,
                    choice_history=tuple(trial.choice_history),
                )
            )
            content = result.content
        except Exception:
            content = fallback_scene_dialogue(scene_index)

        trial.scene_dialogues[scene_index] = content
        return content

    async def _require_trial(self, trial_id: UUID) -> Trial:
        trial = await self._port.find_by_id(trial_id)
        if trial is None:
            raise ValueError(f"Trial not found: {trial_id}")
        return trial

    def _build_portia_prompt(
        self,
        trial: Trial,
        *,
        context: str,
        request_type: str,
    ) -> PortiaResponsePromptDto:
        return PortiaResponsePromptDto(
            trial_id=trial.trial_id,
            scene_index=trial.scene_index,
            dp=trial.dp.value,
            phase=trial.phase,
            choice_history=tuple(trial.choice_history),
            context=context,
            request_type=request_type,
            tubal_used_scenes=trial.tubal_used_scenes,
            presented_evidence=trial.presented_evidence,
        )
