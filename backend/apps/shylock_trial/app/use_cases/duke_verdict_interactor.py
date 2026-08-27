import logging

from shylock_trial.app.dtos.duke_verdict_dto import DukeVerdictPromptDto, DukeVerdictResultDto
from shylock_trial.app.ports.input.duke_verdict_use_case import DukeVerdictUseCase
from shylock_trial.app.ports.output.duke_verdict_port import DukeVerdictPort

logger = logging.getLogger(__name__)

# 두 LLM 프로바이더가 모두 죽었을 때의 안전한 기본값: WIN — 즉 선택지에
# 설계된 ChoiceEffect가 저작된 그대로 적용된다. 공작 판정자가 생기기 전에
# 게임이 주던 것과 같은 결과다. 판정자가 고장 났을 때는 예전의 결정론적
# 동작으로 낮춰지는 게 맞지, 플레이어가 "더 낫게" 고를 방법도 없었던
# 선택지에 임의로 LOSE를 매기면 불공평하게 느껴질 것이다.
FALLBACK_LINE = "법정은 오늘 그 주장을 인정하오."


class DukeVerdictInteractor(DukeVerdictUseCase):
    def __init__(self, port: DukeVerdictPort) -> None:
        self._port = port

    async def judge(self, prompt: DukeVerdictPromptDto) -> DukeVerdictResultDto:
        try:
            return await self._port.judge(prompt)
        except Exception:
            logger.exception(
                "Duke verdict LLM request failed for choice_id=%s; defaulting to WIN",
                prompt.choice_id,
            )
            return DukeVerdictResultDto(result="win", line=FALLBACK_LINE, fallback_used=True)
