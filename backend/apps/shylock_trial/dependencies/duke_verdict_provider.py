from fastapi import Depends

from infrastructure.config import get_settings
from shylock_trial.adapter.outbound.client.duke_verdict_client import DukeVerdictClient
from shylock_trial.adapter.outbound.client.gemma_duke_verdict_client import GemmaDukeVerdictClient
from shylock_trial.app.ports.input.duke_verdict_use_case import DukeVerdictUseCase
from shylock_trial.app.ports.output.duke_verdict_port import DukeVerdictPort
from shylock_trial.app.use_cases.duke_verdict_interactor import DukeVerdictInteractor

# muse-glimmer의 2단계 파이프라인(judge think="medium" + 별도 narrate 호출
# — ollama_duke_verdict_client.py 참고)은 지금 여기에 연결돼 있지 않다.
# judge 호출 한 번에 130초 이상 걸리는 걸 실측했다(2026-08-12) — 플레이어
# 입장에서는 "느리다" 정도가 아니라 서버가 죽은 것처럼 느껴진다. Ollama의
# muse-glimmer 런타임 지원이 더 빠르고 안정적이 되면, OllamaDukeVerdictClient
# 와 FallbackDukeVerdictClient를 import해서 아래 "local" 분기를 다시
# FallbackDukeVerdictClient(primary=OllamaDukeVerdictClient(), fallback=GemmaDukeVerdictClient())
# 로 되돌려 복구하면 된다. muse 클라이언트 자체는 손대지 않았다 —
# _docs/투발_로컬모델_muse-glimmer_테스트.md 참고.


def get_duke_verdict_port() -> DukeVerdictPort:
    # duke_verdict_provider(기본값 "local")는 LLM_PROVIDER와 별개로, 의도적으로
    # 자기만의 독립된 스위치다 — infrastructure/config.py의 해당 주석 참고.
    #
    # "local"은 (muse도, Fallback 래퍼도 없이) GemmaDukeVerdictClient를
    # 곧바로 쓴다 — 2026-08-12 실측 기준 15/15 파싱 성공, 호출당 0.8-1.5초,
    # bias guide를 잘 따르는 판정(logical → win, provocation → win,
    # low-portia_hp일 때 감정적 호소가 먹힘). 래퍼가 필요 없는 이유:
    # DukeVerdictInteractor 자체의 try/except가 이미 어떤 실패에도 WIN을
    # 기본값으로 주고, 다른 유일한 폴백 후보인 Claude는 지금 그 자체로
    # 불안정하다(아래 "claude" 분기 자체의 주석 참고).
    if get_settings().duke_verdict_provider == "local":
        return GemmaDukeVerdictClient()
    # ANTHROPIC_API_KEY가 세션 도중 크레딧이 소진됨(2026-08-12) — judge()
    # 호출마다 400 에러가 난다. 즉시 되돌릴 수 있는 값으로 남겨둠; 이 분기를
    # 다시 쓰려면 먼저 결제 문제를 해결할 것.
    return DukeVerdictClient()


def get_duke_verdict_use_case(
    port: DukeVerdictPort = Depends(get_duke_verdict_port),
) -> DukeVerdictUseCase:
    return DukeVerdictInteractor(port=port)
