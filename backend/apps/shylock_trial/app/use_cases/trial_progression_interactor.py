from uuid import UUID, uuid4
import asyncio

from shylock_trial.app.constants.ending_type_map import resolve_ending_type
from shylock_trial.app.constants.game_balance import (
    PORTIA_HP_MAX,
    SHYLOCK_DP_START,
    SHYLOCK_HP_MAX,
)
from shylock_trial.app.constants.scene_catalog import fallback_scene_dialogue
from shylock_trial.app.constants.scene_choices import (
    FINAL_SCENE_INDEX,
    get_choice_effect,
    get_choice_evidence_id,
)
from shylock_trial.app.dtos.evidence_search_dto import EvidenceSearchInputDto
from shylock_trial.app.dtos.portia_response_dto import PortiaResponsePromptDto
from shylock_trial.app.dtos.scene_dialogue_dto import (
    SceneDialogueContent,
    SceneDialoguePromptDto,
)
from shylock_trial.app.dtos.trial_progression_dto import (
    AdvanceSceneResultDto,
    GenerateEndingResultDto,
    StartTrialResultDto,
    SubmitChoiceInputDto,
    SubmitChoiceResultDto,
)
from shylock_trial.app.ports.input.evidence_search_use_case import EvidenceSearchUseCase
from shylock_trial.app.ports.input.portia_response_use_case import PortiaResponseUseCase
from shylock_trial.app.ports.input.trial_progression_use_case import TrialProgressionUseCase
from shylock_trial.app.ports.output.trial_progression_port import TrialProgressionPort
from shylock_trial.domain.entities.trial_entity import Trial, TrialPhase
from shylock_trial.domain.value_objects.dp_score_vo import DpScore
from shylock_trial.domain.value_objects.portia_hp_score_vo import PortiaHpScore
from shylock_trial.domain.value_objects.shylock_hp_score_vo import ShylockHpScore
from shylock_trial.app.utils.trial_metadata_store import append_unique


class TrialProgressionInteractor(TrialProgressionUseCase):
    def __init__(
        self,
        port: TrialProgressionPort,
        portia: PortiaResponseUseCase,
        evidence: EvidenceSearchUseCase,
    ) -> None:
        self._port = port
        self._portia = portia
        self._evidence = evidence

    async def start(self) -> StartTrialResultDto:
        trial = Trial(
            trial_id=uuid4(),
            scene_index=0,
            shylock_hp=ShylockHpScore(SHYLOCK_HP_MAX),
            dp=DpScore(SHYLOCK_DP_START),
            portia_hp=PortiaHpScore(PORTIA_HP_MAX),
            alien_law_executed=True,
            choice_history=[],
            phase=TrialPhase.IN_PROGRESS,
        )
        trial = await self._port.create(trial)
        scene_dialogue = await self._ensure_scene_dialogue(trial, 0)
        trial = await self._port.save(trial)

        return StartTrialResultDto(
            trial_id=trial.trial_id,
            scene_index=trial.scene_index,
            shylock_hp=trial.shylock_hp.value,
            dp=trial.dp.value,
            portia_hp=trial.portia_hp.value,
            alien_law_executed=trial.alien_law_executed,
            phase=trial.phase,
            scene_dialogue=scene_dialogue,
        )

    async def submit_choice(self, input_dto: SubmitChoiceInputDto) -> SubmitChoiceResultDto:
        trial = await self._require_trial(input_dto.trial_id)

        effect = get_choice_effect(input_dto.choice_id)
        trial.choice_history.append(input_dto.choice_id)
        trial.dp = trial.dp.apply_delta(effect.dp_delta)
        trial.shylock_hp = trial.shylock_hp.apply_delta(effect.shylock_hp_delta)

        evidence_id = get_choice_evidence_id(input_dto.choice_id)
        if evidence_id:
            trial.presented_evidence = append_unique(trial.presented_evidence, evidence_id)

        portia_prompt = self._build_portia_prompt(
            trial,
            context=f"choice:{input_dto.choice_id}",
            request_type="reaction",
        )
        next_scene_index = trial.scene_index + 1
        if next_scene_index <= FINAL_SCENE_INDEX:
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
            shylock_hp=trial.shylock_hp.value,
            dp=trial.dp.value,
            portia_hp=trial.portia_hp.value,
            alien_law_executed=trial.alien_law_executed,
            phase=trial.phase,
            portia_response=portia.text,
            ending_type=None,
            is_ending=is_ending,
        )

    async def advance_scene(self, trial_id: UUID) -> AdvanceSceneResultDto:
        trial = await self._require_trial(trial_id)
        trial.scene_index += 1
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
        ending_type = resolve_ending_type(trial.dp.value, trial.alien_law_executed)

        ending = await self._portia.generate(
            self._build_portia_prompt(
                trial,
                context="final_ending",
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
            shylock_hp=trial.shylock_hp.value,
            dp=trial.dp.value,
            portia_hp=trial.portia_hp.value,
            alien_law_executed=trial.alien_law_executed,
        )

    async def get_trial(self, trial_id: UUID) -> Trial:
        trial = await self._require_trial(trial_id)
        if not trial.is_ended():
            await self._ensure_scene_dialogue(trial, trial.scene_index)
            trial = await self._port.save(trial)
        return trial

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
                    shylock_hp=trial.shylock_hp.value,
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
            shylock_hp=trial.shylock_hp.value,
            alien_law_executed=trial.alien_law_executed,
            phase=trial.phase,
            choice_history=tuple(trial.choice_history),
            context=context,
            request_type=request_type,
            tubal_used_scenes=trial.tubal_used_scenes,
            presented_evidence=trial.presented_evidence,
        )
