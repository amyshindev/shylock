from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from shylock_trial.adapter.inbound.api.schemas.tubal_skill_schema import (
    TubalSkillRequest,
    TubalSkillResponse,
)
from shylock_trial.app.dtos.tubal_skill_dto import TubalSkillInputDto
from shylock_trial.app.ports.input.tubal_skill_use_case import TubalSkillUseCase
from shylock_trial.dependencies.tubal_skill_provider import get_tubal_skill_use_case

tubal_skill_router = APIRouter(prefix="/trials", tags=["tubal-skill"])


@tubal_skill_router.post("/{trial_id}/skills/tubal", response_model=TubalSkillResponse)
async def invoke_tubal_skill(
    trial_id: UUID,
    body: TubalSkillRequest,
    use_case: TubalSkillUseCase = Depends(get_tubal_skill_use_case),
) -> TubalSkillResponse:
    try:
        result = await use_case.invoke_tubal(
            TubalSkillInputDto(
                trial_id=trial_id,
                portia_claim=body.portia_claim,
                scene_id=body.scene_id,
            )
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    agent = result.agent
    return TubalSkillResponse(
        trial_id=result.trial_id,
        dp=result.dp,
        shylock_hp=result.shylock_hp,
        portia_hp=result.portia_hp,
        success=agent.success,
        ftln=agent.ftln,
        passage=agent.passage,
        speaker=agent.speaker,
        act_scene=agent.act_scene,
        tubal_comment=agent.tubal_comment,
    )
