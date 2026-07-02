"""Tubal enhancement — rewrite Shylock's choice line using a Folger passage."""

from __future__ import annotations

import anthropic

from infrastructure.config import get_settings
from shylock_trial.app.utils.dialogue_text import sanitize_game_text

MODEL_ID = "claude-sonnet-4-6"

SYSTEM_PROMPT = """\
You are helping Shylock speak in court.
Given a passage from Shakespeare and Shylock's original line,
rewrite the line to incorporate or reference the passage.
Keep it as a single Korean sentence, natural as courtroom speech.
The line should feel stronger and more grounded than the original.\
"""


def _build_user_message(
    passage: str,
    original_choice: str,
    scene_id: str,
    speaker: str,
) -> str:
    return (
        f"passage: {passage} (spoken by {speaker})\n"
        f"original: {original_choice}\n"
        f"scene: {scene_id}\n"
        "Return the enhanced Korean sentence only. No explanation."
    )


def _extract_text(response: anthropic.types.Message) -> str:
    return "".join(
        block.text for block in response.content if block.type == "text"
    ).strip()


class TubalEnhancementClient:
    def __init__(self) -> None:
        settings = get_settings()
        self._client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key_plain())

    async def generate_enhanced_choice(
        self,
        passage: str,
        original_choice: str,
        scene_id: str,
        speaker: str,
    ) -> str:
        original = original_choice.strip()
        if not original:
            return original_choice

        try:
            response = await self._client.messages.create(
                model=MODEL_ID,
                max_tokens=200,
                system=SYSTEM_PROMPT,
                messages=[
                    {
                        "role": "user",
                        "content": _build_user_message(
                            passage=passage,
                            original_choice=original,
                            scene_id=scene_id,
                            speaker=speaker,
                        ),
                    },
                ],
            )
            enhanced = _extract_text(response)
            if not enhanced:
                return original_choice
            return sanitize_game_text(enhanced)
        except Exception:
            return original_choice
