from fastapi import Depends

from infrastructure.config import get_settings
from infrastructure.redis import get_redis_client
from shylock_trial.adapter.outbound.cache.lore_chat_redis_history import LoreChatRedisHistory
from shylock_trial.adapter.outbound.client.fallback_lore_chat_client import FallbackLoreChatClient
from shylock_trial.adapter.outbound.client.lore_chat_client import LoreChatClient
from shylock_trial.adapter.outbound.client.ollama_lore_chat_client import OllamaLoreChatClient
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
    claude = LoreChatClient()
    # LORE_CHAT_PROVIDER=local wraps Ollama with a Claude fallback (never
    # bare — see FallbackLoreChatClient / config.py). Anything other than
    # "local" (including unset) is the original Claude-only path, unchanged.
    if get_settings().lore_chat_provider == "local":
        return FallbackLoreChatClient(primary=OllamaLoreChatClient(), fallback=claude)
    return claude


def get_lore_chat_use_case(
    evidence: EvidenceSearchUseCase = Depends(get_evidence_search_use_case),
    llm: LoreChatLlmPort = Depends(get_lore_chat_llm_port),
    history: LoreChatHistoryPort = Depends(get_lore_chat_history_port),
) -> LoreChatUseCase:
    return LoreChatInteractor(evidence=evidence, llm=llm, history=history)
