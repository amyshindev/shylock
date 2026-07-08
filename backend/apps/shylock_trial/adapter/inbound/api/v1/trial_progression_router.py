from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from shylock_trial.adapter.inbound.api.schemas.trial_progression_schema import (
    AdvanceSceneResponse,
    EndingResponse,
    LauncelotSkillResponse,
    SceneDialogueLineResponse,
    SceneDialogueResponse,
    StartTrialResponse,
    SubmitChoiceRequest,
    SubmitChoiceResponse,
    TrialResponse,
    VeniceParadoxSkillResponse,
    scene_dialogue_from_trial,
)
from shylock_trial.app.dtos.trial_progression_dto import SubmitChoiceInputDto
from shylock_trial.app.ports.input.trial_progression_use_case import TrialProgressionUseCase
from shylock_trial.dependencies.trial_progression_provider import get_trial_progression_use_case

trial_progression_router = APIRouter(prefix="/trials", tags=["trial-progression"])


def _scene_dialogue_response(content) -> SceneDialogueResponse:
    return SceneDialogueResponse(
        lines=[
            SceneDialogueLineResponse(text=line.text, kind=line.kind.value, speaker=line.speaker)
            for line in content.lines
        ],
        challenge_header=content.challenge_header,
        challenge_text=content.challenge_text,
        choice_texts=content.choice_text_map(),
    )


@trial_progression_router.post(
    "",
    response_model=StartTrialResponse,
    status_code=status.HTTP_201_CREATED,
)
async def start_trial(
    use_case: TrialProgressionUseCase = Depends(get_trial_progression_use_case),
) -> StartTrialResponse:
    result = await use_case.start()
    return StartTrialResponse(
        trial_id=result.trial_id,
        scene_index=result.scene_index,
        dp=result.dp,
        hp=result.hp,
        portia_hp=result.portia_hp,
        phase=result.phase,
        scene_dialogue=_scene_dialogue_response(result.scene_dialogue),
    )


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
        dp=trial.dp.value,
        hp=trial.hp.value,
        portia_hp=trial.portia_hp.value,
        phase=trial.phase,
        choice_history=trial.choice_history,
        narration_text=trial.narration_text,
        scene_dialogue=scene_dialogue_from_trial(trial),
        tubal_enhanced_choices=dict(trial.tubal_enhanced_choices),
        venice_dp_shield=trial.venice_dp_shield,
        venice_paradox_used=trial.venice_paradox_used,
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
        dp=result.dp,
        hp=result.hp,
        portia_hp=result.portia_hp,
        phase=result.phase,
        portia_response=result.portia_response,
        ending_type=result.ending_type.value if result.ending_type else None,
        is_ending=result.is_ending,
        tubal_enhanced_choices=result.tubal_enhanced_choices,
        venice_dp_shield=result.venice_dp_shield,
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
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="다음 장면을 준비하지 못했습니다. 잠시 후 다시 시도해 주세요.",
        ) from exc
    return AdvanceSceneResponse(
        trial_id=result.trial_id,
        scene_index=result.scene_index,
        scene_data=result.scene_data,
        scene_dialogue=_scene_dialogue_response(result.scene_dialogue),
        dp=result.dp,
        hp=result.hp,
        portia_hp=result.portia_hp,
    )


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
        dp=result.dp,
    )


@trial_progression_router.post(
    "/{trial_id}/skills/launcelot",
    response_model=LauncelotSkillResponse,
)
async def use_launcelot_skill(
    trial_id: UUID,
    use_case: TrialProgressionUseCase = Depends(get_trial_progression_use_case),
) -> LauncelotSkillResponse:
    try:
        result = await use_case.use_launcelot_skill(trial_id)
        return LauncelotSkillResponse(
            trial_id=result.trial_id,
            dp=result.dp,
            hp=result.hp,
            launcelot_comment=result.launcelot_comment,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@trial_progression_router.post(
    "/{trial_id}/skills/venice-paradox",
    response_model=VeniceParadoxSkillResponse,
)
async def use_venice_paradox_skill(
    trial_id: UUID,
    use_case: TrialProgressionUseCase = Depends(get_trial_progression_use_case),
) -> VeniceParadoxSkillResponse:
    try:
        result = await use_case.use_venice_paradox_skill(trial_id)
        return VeniceParadoxSkillResponse(
            trial_id=result.trial_id,
            dp=result.dp,
            hp=result.hp,
            venice_paradox_used=result.venice_paradox_used,
            skill_comment=result.skill_comment,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
