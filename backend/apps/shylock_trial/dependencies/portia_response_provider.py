from fastapi import Depends

from infrastructure.config import get_settings
from shylock_trial.adapter.outbound.client.fallback_portia_response_client import (
    FallbackPortiaResponseClient,
)
from shylock_trial.adapter.outbound.client.ollama_portia_response_client import (
    OllamaPortiaResponseClient,
)
from shylock_trial.adapter.outbound.client.portia_response_client import PortiaResponseClient
from shylock_trial.app.ports.input.portia_response_use_case import PortiaResponseUseCase
from shylock_trial.app.ports.output.portia_response_port import PortiaResponsePort
from shylock_trial.app.use_cases.portia_response_interactor import PortiaResponseInteractor


def get_portia_response_port() -> PortiaResponsePort:
    claude = PortiaResponseClient()
    # LLM_PROVIDER=local wraps Ollama with a Claude fallback (never bare —
    # a local server isn't guaranteed to be up). Anything other than "local"
    # (including unset) is the original Claude-only path, unchanged — set
    # LLM_PROVIDER back to "claude"/unset it to revert instantly.
    if get_settings().llm_provider == "local":
        return FallbackPortiaResponseClient(primary=OllamaPortiaResponseClient(), fallback=claude)
    return claude


def get_portia_response_use_case(
    port: PortiaResponsePort = Depends(get_portia_response_port),
) -> PortiaResponseUseCase:
    return PortiaResponseInteractor(port=port)
