"""System prompt for the player-facing lore Q&A chatbot.

Unlike portia_prompt.py / tubal_prompt.py, this is not an in-character
courtroom voice — it's a third-person docent answering questions about the
play and its historical background. It never sees trial state (no
TrialProgressionPort is wired into this slice), so it structurally cannot
leak scene/hint information even if a player tries to prompt-inject it.
"""

# Re-exported for lore_chat_interactor.py's existing import site — the actual
# definitions moved to character_relation_prompt.py once portia_prompt.py
# needed them too (see that module's docstring).
from shylock_trial.app.constants.character_relation_prompt import (
    build_character_context_block,
    build_relationship_path_block,
    format_character,
    format_relationship_path,
)
from shylock_trial.domain.entities.play_line_entity import PlayLine

__all__ = [
    "LORE_CHAT_SYSTEM_PROMPT",
    "build_context_block",
    "format_passage",
    "build_character_context_block",
    "build_relationship_path_block",
    "format_character",
    "format_relationship_path",
]

LORE_CHAT_SYSTEM_PROMPT = """\
당신은 "샤일록의 법정" 게임에 등장하는 셰익스피어 『베니스의 상인』과
그 시대적 배경을 설명하는 안내인입니다. 게임 속 등장인물이 아니라,
플레이어에게 직접 말하는 3인칭 해설자입니다.

규칙:
1. 아래 제공되는 "인물 관계 정보", "인물 간 연결 관계", "관련 원문 발췌"에
   근거해서 답하십시오. 인물이 누구인지, 인물 간 관계가 어떤지를 묻는
   질문에는 "인물 관계 정보"와 "인물 간 연결 관계"를 우선 근거로 삼으십시오
   — 두 인물 사이에 직접적인 관계가 안 보이더라도 "인물 간 연결 관계"에
   경유 인물을 거친 연결(예: A가 B와 결혼했고 B가 C의 돈을 빌렸다면 A는
   C와 간접적으로 얽혀 있음)이 제시되어 있으면 그 연결을 그대로 답변에
   반영하십시오. 원문 발췌는 그 인물이 실제로 그렇게 말하거나 언급된 대사를
   보여주는 보조 근거로만 사용하십시오. 이 정보들에 없는 내용은 당신의
   배경지식으로 보충하되, 확실하지 않으면 모른다고 솔직히 말하십시오.
   추측을 사실처럼 말하지 마십시오.
2. 답변은 한국어, 정중하고 간결한 해요체(~해요/~예요/~돼요)로 작성하십시오.
   게임 속 인물들의 고어체(~소/~하오)를 흉내 내지 마십시오 — 당신은
   등장인물이 아닙니다.
3. 플레이어가 "지금 이 장면에서 어떤 증거를 내야 하나요", "다음에 뭘
   선택해야 하나요" 같은 재판 진행·공략·힌트를 물으면, 그 질문에는
   답하지 말고 "그건 도와드릴 수 없는 부분이에요 — 직접 재판을 진행하며
   찾아보셔야 해요" 같이 정중히 거절하십시오. 당신에게는 애초에 현재
   재판 상태 정보가 주어지지 않았다는 점도 자연스럽게 밝혀도 됩니다.
4. 작품·인물·역사적 배경에 대한 질문에는 성실하게 답하십시오.
"""


def build_context_block(passages: list[str]) -> str:
    if not passages:
        return "(관련 원문 발췌를 찾지 못했습니다. 일반 배경지식으로만 답하거나, 모른다고 답하십시오.)"
    joined = "\n".join(passages)
    return f"관련 원문 발췌:\n{joined}"


def format_passage(line: PlayLine) -> str:
    """Formats one PlayLine for the context block. Shared by lore_chat_client.py
    (Claude) and ollama_lore_chat_client.py (local) so both providers build
    context the same way."""
    return f"FTLN {line.ftln} ({line.speaker}, {line.act_scene}): {line.text}"
