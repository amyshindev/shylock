from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from shylock_trial.adapter.inbound.api.schemas.trial_progression_schema import (
    AdvanceSceneResponse,
    EndingResponse,
    StartTrialResponse,
    SubmitChoiceRequest,
    SubmitChoiceResponse,
    TrialResponse,
)
from shylock_trial.app.dtos.trial_progression_dto import SubmitChoiceInputDto
from shylock_trial.app.ports.input.trial_progression_use_case import TrialProgressionUseCase
from shylock_trial.dependencies.trial_progression_provider import get_trial_progression_use_case

trial_progression_router = APIRouter(prefix="/trials", tags=["trial-progression"])


@trial_progression_router.post(
    "",
    response_model=StartTrialResponse,
    status_code=status.HTTP_201_CREATED,
)
async def start_trial(
    use_case: TrialProgressionUseCase = Depends(get_trial_progression_use_case),
) -> StartTrialResponse:
    result = await use_case.start()
    return StartTrialResponse.model_validate(result, from_attributes=True)


@trial_progression_router.get("/{trial_id}", response_model=TrialResponse)
async def get_trial(
    trial_id: UUID,
    use_case: TrialProgressionUseCase = Depends(get_trial_progression_use_case),
) -> TrialResponse:
    try:
        trial = await use_case.get_trial(trial_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return TrialResponse(
        trial_id=trial.trial_id,
        scene_index=trial.scene_index,
        dignity=trial.dignity.value,
        confidence=trial.confidence.value,
        phase=trial.phase,
        choice_history=trial.choice_history,
        narration_text=trial.narration_text,
    )


@trial_progression_router.post("/{trial_id}/choices", response_model=SubmitChoiceResponse)
async def submit_choice(
    trial_id: UUID,
    body: SubmitChoiceRequest,
    use_case: TrialProgressionUseCase = Depends(get_trial_progression_use_case),
) -> SubmitChoiceResponse:
    try:
        result = await use_case.submit_choice(
            SubmitChoiceInputDto(trial_id=trial_id, choice_id=body.choice_id)
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return SubmitChoiceResponse(
        trial_id=result.trial_id,
        scene_index=result.scene_index,
        dignity=result.dignity,
        confidence=result.confidence,
        phase=result.phase,
        portia_response=result.portia_response,
        ending_type=result.ending_type.value if result.ending_type else None,
        is_ending=result.is_ending,
    )


@trial_progression_router.post("/{trial_id}/advance", response_model=AdvanceSceneResponse)
async def advance_scene(
    trial_id: UUID,
    use_case: TrialProgressionUseCase = Depends(get_trial_progression_use_case),
) -> AdvanceSceneResponse:
    try:
        result = await use_case.advance_scene(trial_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return AdvanceSceneResponse.model_validate(result, from_attributes=True)


@trial_progression_router.get("/{trial_id}/ending", response_model=EndingResponse)
async def generate_ending(
    trial_id: UUID,
    use_case: TrialProgressionUseCase = Depends(get_trial_progression_use_case),
) -> EndingResponse:
    try:
        result = await use_case.generate_ending(trial_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return EndingResponse(
        trial_id=result.trial_id,
        ending_type=result.ending_type.value,
        ending_text=result.ending_text,
        dignity=result.dignity,
        confidence=result.confidence,
    )
