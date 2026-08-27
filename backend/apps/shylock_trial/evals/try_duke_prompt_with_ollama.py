"""임시 스크립트: 실제 Duke 판정 파이프라인(judge 호출 + narrate 호출)의
시간을 현재 설정된 모델(DUKE_JUDGE_MODEL / DUKE_NARRATOR_MODEL —
infrastructure/config.py 참고)들로 측정한다.

try_portia_prompt_with_ollama.py와 달리 이 스크립트는 프롬프트를 다시
렌더링하지 않는다 — 실제 프로덕션 어댑터인 OllamaDukeVerdictClient를
직접 호출한다. 이게 실제 submit_choice 호출이 진짜로 무엇을 기다리는지
측정하는 유일한 방법이다 — 파이프라인의 두 단계(think="medium"인 judge
모델의 추론, 그다음 think=false인 narrator 모델)를 모두 포함해서
(ollama_duke_verdict_client.py의 모듈 docstring 참고).

backend/에서 실행 (로컬 Ollama 서버가 떠 있어야 함, 기본 localhost:11434):
    python -m shylock_trial.evals.try_duke_prompt_with_ollama [--repeats 3]
"""

from __future__ import annotations

import argparse
import asyncio
import time
from uuid import uuid4

from shylock_trial.adapter.outbound.client.ollama_duke_verdict_client import (
    OllamaDukeVerdictClient,
)
from shylock_trial.app.dtos.duke_verdict_dto import DukeVerdictPromptDto

# 실제로 judge까지 도달하는 유일한 선택지인 "bold" 선택 몇 가지를 대표로
# (trial_progression_interactor._judge_choice 참고), 서로 다른 stimulus
# 유형과 portia_hp 구간에 걸쳐 뽑아서 타이밍이 우연히 좋은 케이스 하나만
# 반영하지 않도록 했다.
SAMPLE_PROMPTS: list[DukeVerdictPromptDto] = [
    DukeVerdictPromptDto(
        trial_id=uuid4(),
        scene_index=1,
        choice_id="bond_signature",
        choice_brief="Both my signature and Antonio's are on this bond — what is the problem?",
        stimulus="logical",
        dp=55,
        portia_hp=80,
        round_number=1,
    ),
    DukeVerdictPromptDto(
        trial_id=uuid4(),
        scene_index=3,
        choice_id="ring_loss_dignity",
        choice_brief="If you knew what I have lost, you would not dare call it a weakness.",
        stimulus="provocation",
        dp=65,
        portia_hp=40,
        round_number=4,
    ),
]


async def main(repeats: int) -> None:
    client = OllamaDukeVerdictClient()

    for prompt in SAMPLE_PROMPTS:
        print(f"\n{'=' * 70}\n{prompt.choice_id} (stimulus={prompt.stimulus}, portia_hp={prompt.portia_hp})\n{'=' * 70}")
        for i in range(repeats):
            start = time.monotonic()
            result = await client.judge(prompt)
            elapsed = time.monotonic() - start
            print(
                f"  rep {i + 1}/{repeats}: {elapsed:.1f}s — "
                f"result={result.result} fallback_used={result.fallback_used}"
            )
            print(f"    line: {result.line}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--repeats", type=int, default=3)
    args = parser.parse_args()
    asyncio.run(main(args.repeats))
