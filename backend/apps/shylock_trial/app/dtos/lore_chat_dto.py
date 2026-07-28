from dataclasses import dataclass
from typing import Literal

LoreChatTurnRole = Literal["human", "ai"]


@dataclass(frozen=True, slots=True)
class LoreChatTurnDto:
    role: LoreChatTurnRole
    content: str


@dataclass(frozen=True, slots=True)
class LoreChatSourceDto:
    ftln: int
    act_scene: str
    speaker: str
    excerpt: str


@dataclass(frozen=True, slots=True)
class LoreChatAskInputDto:
    message: str
    session_id: str | None = None


@dataclass(frozen=True, slots=True)
class LoreChatResultDto:
    session_id: str
    answer: str
    sources: tuple[LoreChatSourceDto, ...]
