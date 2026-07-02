from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from shylock_trial.adapter.inbound.api.schemas.present_evidence_schema import (
    PresentEvidenceRequest,
    PresentEvidenceResponse,
)
from shylock_trial.app.dtos.present_evidence_dto import PresentEvidenceInputDto
from shylock_trial.app.ports.input.present_evidence_use_case import PresentEvidenceUseCase
from shylock_trial.dependencies.present_evidence_provider import get_present_evidence_use_case

present_evidence_router = APIRouter(prefix="/trials", tags=["present-evidence"])


@present_evidence_router.post(
    "/{trial_id}/present-evidence",
    response_model=PresentEvidenceResponse,
)
async def present_evidence(
    trial_id: UUID,
    body: PresentEvidenceRequest,
    use_case: PresentEvidenceUseCase = Depends(get_present_evidence_use_case),
) -> PresentEvidenceResponse:
    try:
        result = await use_case.present_evidence(
            PresentEvidenceInputDto(
                trial_id=trial_id,
                scene_id=body.scene_id,
                evidence_id=body.evidence_id,
                evidence_text=body.evidence_text,
            )
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return PresentEvidenceResponse(
        trial_id=result.trial_id,
        shylock_hp=result.shylock_hp,
        dp=result.dp,
        contradiction_valid=result.contradiction_valid,
        portia_response=result.portia_response,
    )
