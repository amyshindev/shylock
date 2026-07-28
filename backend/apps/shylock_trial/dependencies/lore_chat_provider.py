from fastapi import Depends

from infrastructure.redis import get_redis_client
from shylock_trial.adapter.outbound.cache.lore_chat_redis_history import LoreChatRedisHistory
from shylock_trial.adapter.outbound.client.lore_chat_client import LoreChatClient
from shylock_trial.app.ports.input.evidence_search_use_case import EvidenceSearchUseCase
from shylock_trial.app.ports.input.lore_chat_use_case import LoreChatUseCase
from shylock_trial.app.ports.output.lore_chat_history_port import LoreChatHistoryPort
from shylock_trial.app.ports.output.lore_chat_llm_port import LoreChatLlmPort
from shylock_trial.app.use_cases.lore_chat_interactor import LoreChatInteractor
from shylock_trial.dependencies.evidence_search_provider import get_evidence_search_use_case


def get_lore_chat_history_port(
    redis_client=Depends(get_redis_client),
) -> LoreChatHistoryPort:
    return LoreChatRedisHistory(redis_client=redis_client)


def get_lore_chat_llm_port() -> LoreChatLlmPort:
    return LoreChatClient()


def get_lore_chat_use_case(
    evidence: EvidenceSearchUseCase = Depends(get_evidence_search_use_case),
    llm: LoreChatLlmPort = Depends(get_lore_chat_llm_port),
    history: LoreChatHistoryPort = Depends(get_lore_chat_history_port),
) -> LoreChatUseCase:
    return LoreChatInteractor(evidence=evidence, llm=llm, history=history)
