import logging

from shylock_trial.app.dtos.portia_response_dto import (
    PortiaResponsePromptDto,
    PortiaResponseResultDto,
)
from shylock_trial.app.ports.input.portia_response_use_case import PortiaResponseUseCase
from shylock_trial.app.ports.output.portia_response_port import PortiaResponsePort

logger = logging.getLogger(__name__)

FALLBACK_TEXT = "법정에 잠시 정적이 흐른다. 다음 말을 기다리는 중이다."


class PortiaResponseInteractor(PortiaResponseUseCase):
    def __init__(self, port: PortiaResponsePort) -> None:
        self._port = port

    async def generate(self, prompt: PortiaResponsePromptDto) -> PortiaResponseResultDto:
        try:
            return await self._port.generate(prompt)
        except Exception:
            logger.exception("Portia LLM request failed; returning fallback text")
            return PortiaResponseResultDto(text=FALLBACK_TEXT, fallback_used=True)
