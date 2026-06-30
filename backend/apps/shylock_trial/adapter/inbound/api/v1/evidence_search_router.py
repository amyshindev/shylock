from fastapi import APIRouter, Depends, HTTPException, status

from shylock_trial.adapter.inbound.api.schemas.evidence_search_schema import (
    EvidenceResponse,
    PlayLineResponse,
    RelatedPlayLinesResponse,
)
from shylock_trial.app.dtos.evidence_search_dto import EvidenceSearchInputDto
from shylock_trial.app.ports.input.evidence_search_use_case import EvidenceSearchUseCase
from shylock_trial.dependencies.evidence_search_provider import get_evidence_search_use_case

evidence_search_router = APIRouter(prefix="/evidence", tags=["evidence-search"])


@evidence_search_router.get("", response_model=list[EvidenceResponse])
async def list_evidence(
    use_case: EvidenceSearchUseCase = Depends(get_evidence_search_use_case),
) -> list[EvidenceResponse]:
    items = await use_case.list_curated_evidence()
    return [
        EvidenceResponse(
            evidence_id=item.evidence_id,
            quote=item.quote,
            act_scene=item.act_scene,
            icon=item.icon,
            description=item.description,
            source_ftln_start=item.source_ftln_range[0],
            source_ftln_end=item.source_ftln_range[1],
        )
        for item in items
    ]


@evidence_search_router.get("/{evidence_id}", response_model=EvidenceResponse)
async def get_evidence(
    evidence_id: str,
    use_case: EvidenceSearchUseCase = Depends(get_evidence_search_use_case),
) -> EvidenceResponse:
    item = await use_case.get_evidence(evidence_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evidence not found")
    return EvidenceResponse(
        evidence_id=item.evidence_id,
        quote=item.quote,
        act_scene=item.act_scene,
        icon=item.icon,
        description=item.description,
        source_ftln_start=item.source_ftln_range[0],
        source_ftln_end=item.source_ftln_range[1],
    )


@evidence_search_router.get("/{evidence_id}/related", response_model=RelatedPlayLinesResponse)
async def related_play_lines(
    evidence_id: str,
    use_case: EvidenceSearchUseCase = Depends(get_evidence_search_use_case),
) -> RelatedPlayLinesResponse:
    evidence = await use_case.get_evidence(evidence_id)
    if evidence is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evidence not found")

    result = await use_case.search(
        EvidenceSearchInputDto(query=evidence.quote, evidence_id=evidence_id, limit=5)
    )
    return RelatedPlayLinesResponse(
        evidence_id=evidence_id,
        play_lines=[PlayLineResponse.model_validate(line, from_attributes=True) for line in result.play_lines],
    )
