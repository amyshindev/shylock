from fastapi import APIRouter, Depends

from shylock_trial.adapter.inbound.api.schemas.lore_chat_schema import (
    LoreChatAskRequest,
    LoreChatAskResponse,
    LoreChatSourceResponse,
)
from shylock_trial.app.dtos.lore_chat_dto import LoreChatAskInputDto
from shylock_trial.app.ports.input.lore_chat_use_case import LoreChatUseCase
from shylock_trial.dependencies.lore_chat_provider import get_lore_chat_use_case

lore_chat_router = APIRouter(prefix="/lore-chat", tags=["lore-chat"])


@lore_chat_router.post("/ask", response_model=LoreChatAskResponse)
async def ask_lore_chat(
    request: LoreChatAskRequest,
    use_case: LoreChatUseCase = Depends(get_lore_chat_use_case),
) -> LoreChatAskResponse:
    result = await use_case.ask(
        LoreChatAskInputDto(message=request.message, session_id=request.session_id)
    )
    return LoreChatAskResponse(
        session_id=result.session_id,
        answer=result.answer,
        sources=[
            LoreChatSourceResponse(
                ftln=source.ftln,
                act_scene=source.act_scene,
                speaker=source.speaker,
                excerpt=source.excerpt,
            )
            for source in result.sources
        ],
    )
