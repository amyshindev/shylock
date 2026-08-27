"""공작(Duke)의 라운드별 판결을 위한 LLM 프롬프트 — dp/portia_hp가 적용되기
전에, 샤일록이 방금 제출한 주장이 실제로 먹히는지를 판정한다.
trial_progression_interactor.submit_choice 참고: "bold" 선택지
(ChoiceEffect.dp_delta > 0)에만 호출되며, concede/silent 선택지는 결과가
이미 정해진 것이나 마찬가지라 이 판정을 거치지 않는다.

portia_prompt.py보다 의도적으로 훨씬 작다 — 공작은 호출당 할 일이 하나뿐이고
(이분법적 판결 + 법정 발언 한 줄), 지속되는 캐릭터 아크가 없으므로 여기엔
persona/composure 장치가 없다.

이 모듈은 두 가지 호출 형태를 함께 담고 있다:
- SYSTEM_PROMPT / build_user_message: 한 번의 호출로 win/lose 판정과 대사
  작성을 함께 처리. duke_verdict_client.py(Claude)가 사용 — 강한 단일
  모델이라면 판정과 작문을 굳이 분리할 필요가 없다.
- JUDGE_SYSTEM_PROMPT+build_judge_message /
  NARRATE_SYSTEM_PROMPT+build_narrate_message: 두 번의 개별 호출로,
  ollama_duke_verdict_client.py가 사용 — win/lose 판정과 한국어 법정 대사를
  각각 그 일에 실제로 더 나은 로컬 모델에 맡길 수 있게 한다
  (infrastructure/config.py의 DUKE_JUDGE_MODEL / DUKE_NARRATOR_MODEL 참고)
  — 예를 들어 추론에 튜닝된 모델이 판정을 내리고, 서술에 튜닝된 모델은
  판정자가 이미 결정한 내용을 대사로 쓰기만 한다."""

from shylock_trial.app.constants.game_balance import (
    PORTIA_HP_HIGH_THRESHOLD,
    PORTIA_HP_LOW_THRESHOLD,
)
from shylock_trial.app.dtos.duke_verdict_dto import DukeVerdictPromptDto

_BIAS_GUIDE = """\
Bias guide (this is not a coin flip — weigh it):
- Default toward WIN when the argument is logically sound (stimulus=logical)
  or well-grounded emotionally with real stakes — Shylock only reaches this
  judge with arguments the game already considers his strong moves.
- Lean toward LOSE when the argument is pure provocation/defiance that could
  read as contempt of court rather than persuasion — a sharp tongue can lose
  the room even when the underlying point is fair.
- portia_hp tracks how worn down the court's presiding legal officer already
  is: high (>= {high}) means composure is fully intact and arguments must
  clear a high bar; low (<= {low}) means the court's resistance is already
  frayed and a well-aimed argument is more likely to land. Use this to shade
  the odds, not to decide alone.
""".format(high=PORTIA_HP_HIGH_THRESHOLD, low=PORTIA_HP_LOW_THRESHOLD)

_CASE_FACTS = """\
Round {round_number} — rule on Shylock's argument.

Shylock's argument ({choice_id}): {choice_brief}
Stimulus type: {stimulus}
dp so far: {dp} (max 100)
portia_hp: {portia_hp} (max 100 — lower means the court's composure is already worn down)"""


def _case_facts(prompt: DukeVerdictPromptDto) -> str:
    return _CASE_FACTS.format(
        round_number=prompt.round_number,
        choice_id=prompt.choice_id,
        choice_brief=prompt.choice_brief,
        stimulus=prompt.stimulus,
        dp=prompt.dp,
        portia_hp=prompt.portia_hp,
    )


# --- 단일 호출 형태 (Claude) ------------------------------------------------

SYSTEM_PROMPT = f"""\
You write in-game text for *The Merchant of Venice* trial (shylock-trial.jsx canon).
공작(the Duke) presides over the Venice court and, after Shylock's plea, rules
whether THIS particular argument persuades the court — a bounded win/lose call,
distinct from Portia's own in-character courtroom speech (generated separately).

Output Korean only (한국어). The Duke speaks in formal court register
(~하오/~이오/~노라/~하겠소) — a magistrate reading a ruling, not a debater.
1–2 sentences. No modern references, no breaking the fourth wall.

{_BIAS_GUIDE}
- Do not let LOSE feel arbitrary: when you rule LOSE, the line should name a
  real reason (a technicality, a procedural gap, a failure to move the court)
  — never "no reason, the Duke simply disagrees."

Return JSON only: {{"result": "win" | "lose", "line": "..."}}
"""

# Concede/silent 선택지(ChoiceEffect.dp_delta <= 0)는 LLM 판정자를 거치지
# 않는다 — 아무것도 걸지 않았으니 판정할 것도 없다 (scene_choices.py의
# CHOICE_EFFECTS 주석 참고). trial_progression_interactor가 이런 경우에
# 쓰는, 결정론적이고 지연 시간이 없는 판결 대사다.
CONCEDE_LOSE_LINE = "그대 스스로 물러섰으니, 법정이 겨룰 것도 없소."


def build_user_message(prompt: DukeVerdictPromptDto) -> str:
    return f"""{_case_facts(prompt)}

Return JSON with "result" ("win" or "lose") and "line" (the Duke's ruling, 1–2 Korean sentences)."""


# --- 2단계 호출 형태 (Ollama: judge 모델 + narrator 모델) --------------------

JUDGE_SYSTEM_PROMPT = f"""\
You are 공작(the Duke), presiding judge of the Venice court in *The Merchant
of Venice* trial (shylock-trial.jsx canon). After Shylock's plea, you decide
— and ONLY decide — whether THIS particular argument persuades the court.
You do not write his ruling speech; another writer turns your decision into
the spoken line afterward. Take the space to actually reason through the
bias guide below before answering; this decision is what the game's dp and
portia_hp move on, not just flavor text.

{_BIAS_GUIDE}
Return JSON only: {{"result": "win" | "lose", "reasoning": "..."}}
"reasoning" is a short (1 sentence) English note on WHY — naming the actual
factor that tipped it (e.g. "logical and well-grounded, clears the bar" or
"landed a fair point but the tone reads as contempt of court"). It is never
shown to the player as-is; the narrator model uses it to ground the Duke's
line in a real reason instead of inventing one.
"""


def build_judge_message(prompt: DukeVerdictPromptDto) -> str:
    return f"""{_case_facts(prompt)}

Return JSON with "result" ("win" or "lose") and "reasoning" (short English note on why)."""


NARRATE_SYSTEM_PROMPT = """\
You write in-game text for *The Merchant of Venice* trial (shylock-trial.jsx canon).
공작(the Duke) has already decided the ruling below — your only job is to put
it into his voice. Do not second-guess or change the result.

Output Korean only (한국어). The Duke speaks in formal court register
(~하오/~이오/~노라/~하겠소) — a magistrate reading a ruling, not a debater.
1–2 sentences. No modern references, no breaking the fourth wall. If the
result is LOSE, the line must name a real reason (grounded in the reasoning
given below) — never "no reason, the Duke simply disagrees."

Return JSON only: {"line": "..."}
"""


def build_narrate_message(prompt: DukeVerdictPromptDto, result: str, reasoning: str) -> str:
    return f"""{_case_facts(prompt)}

The Duke's ruling (already decided — do not change it): {result.upper()}
Why: {reasoning}

Return JSON with "line" (the Duke's ruling in his own voice, 1–2 Korean sentences)."""
