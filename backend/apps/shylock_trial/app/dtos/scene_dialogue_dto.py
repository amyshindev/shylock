from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID


class DialogueLineKind(StrEnum):
    SPEECH = "speech"
    NARRATION = "narration"


@dataclass(frozen=True, slots=True)
class SceneDialogueLine:
    text: str
    kind: DialogueLineKind = DialogueLineKind.NARRATION
    speaker: str | None = None


@dataclass(slots=True)
class SceneDialogueContent:
    lines: tuple[SceneDialogueLine, ...]
    challenge_header: str | None = None
    challenge_text: str | None = None
    choice_texts: dict[str, str] | None = None

    def choice_text_map(self) -> dict[str, str]:
        return dict(self.choice_texts or {})


@dataclass(frozen=True, slots=True)
class SceneDialoguePromptDto:
    trial_id: UUID
    scene_index: int
    dp: int
    choice_history: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class SceneDialogueResultDto:
    content: SceneDialogueContent
    fallback_used: bool = False
