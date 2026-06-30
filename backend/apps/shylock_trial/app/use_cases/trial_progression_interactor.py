from uuid import UUID, uuid4

from shylock_trial.app.constants.ending_type_map import resolve_ending_type
from shylock_trial.app.constants.scene_choices import get_choice_effect
from shylock_trial.app.dtos.evidence_search_dto import EvidenceSearchInputDto
from shylock_trial.app.dtos.portia_response_dto import PortiaResponsePromptDto
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
from shylock_trial.domain.value_objects.confidence_score_vo import ConfidenceScore
from shylock_trial.domain.value_objects.dignity_score_vo import DignityScore


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
            dignity=DignityScore(50),
            confidence=ConfidenceScore(40),
            choice_history=[],
            phase=TrialPhase.IN_PROGRESS,
        )
        trial = await self._port.create(trial)

        narration = await self._portia.generate(
            PortiaResponsePromptDto(
                trial_id=trial.trial_id,
                scene_index=trial.scene_index,
                dignity=trial.dignity.value,
                confidence=trial.confidence.value,
                phase=trial.phase,
                choice_history=tuple(trial.choice_history),
                context="scene_1_opening",
                request_type="narration",
            )
        )
        trial.narration_text = narration.text
        trial = await self._port.save(trial)

        return StartTrialResultDto(
            trial_id=trial.trial_id,
            scene_index=trial.scene_index,
            dignity=trial.dignity.value,
            confidence=trial.confidence.value,
            phase=trial.phase,
            narration_text=narration.text,
        )

    async def submit_choice(self, input_dto: SubmitChoiceInputDto) -> SubmitChoiceResultDto:
        trial = await self._require_trial(input_dto.trial_id)

        effect = get_choice_effect(input_dto.choice_id)
        trial.choice_history.append(input_dto.choice_id)
        trial.dignity = trial.dignity.apply_delta(effect.dignity_delta)
        trial.confidence = trial.confidence.apply_delta(effect.confidence_delta)

        await self._evidence.search(
            EvidenceSearchInputDto(query=input_dto.choice_id, limit=3)
        )

        portia = await self._portia.generate(
            PortiaResponsePromptDto(
                trial_id=trial.trial_id,
                scene_index=trial.scene_index,
                dignity=trial.dignity.value,
                confidence=trial.confidence.value,
                phase=trial.phase,
                choice_history=tuple(trial.choice_history),
                context=f"choice:{input_dto.choice_id}",
                request_type="reaction",
            )
        )

        # Ending only via generate_ending; never cut the trial short mid-game.
        is_ending = False

        trial = await self._port.save(trial)

        return SubmitChoiceResultDto(
            trial_id=trial.trial_id,
            scene_index=trial.scene_index,
            dignity=trial.dignity.value,
            confidence=trial.confidence.value,
            phase=trial.phase,
            portia_response=portia.text,
            ending_type=None,
            is_ending=is_ending,
        )

    async def advance_scene(self, trial_id: UUID) -> AdvanceSceneResultDto:
        trial = await self._require_trial(trial_id)
        trial.scene_index += 1
        trial = await self._port.save(trial)

        return AdvanceSceneResultDto(
            trial_id=trial.trial_id,
            scene_index=trial.scene_index,
            scene_data={"scene_index": trial.scene_index},
        )

    async def generate_ending(self, trial_id: UUID) -> GenerateEndingResultDto:
        trial = await self._require_trial(trial_id)
        ending_type = resolve_ending_type(trial.dignity.value)

        ending = await self._portia.generate(
            PortiaResponsePromptDto(
                trial_id=trial.trial_id,
                scene_index=trial.scene_index,
                dignity=trial.dignity.value,
                confidence=trial.confidence.value,
                phase=trial.phase,
                choice_history=tuple(trial.choice_history),
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
            dignity=trial.dignity.value,
            confidence=trial.confidence.value,
        )

    async def get_trial(self, trial_id: UUID) -> Trial:
        return await self._require_trial(trial_id)

    async def _require_trial(self, trial_id: UUID) -> Trial:
        trial = await self._port.find_by_id(trial_id)
        if trial is None:
            raise ValueError(f"Trial not found: {trial_id}")
        return trial
