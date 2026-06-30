from typing import Any

from anthropic import AsyncAnthropic

from core.config import get_settings
from shylock_trial.app.constants.portia_prompt import SYSTEM_PROMPT, build_user_message
from shylock_trial.app.dtos.portia_response_dto import (
    PortiaResponsePromptDto,
    PortiaResponseResultDto,
)
from shylock_trial.app.ports.output.portia_response_port import PortiaResponsePort

MODEL_ID = "claude-sonnet-4-6"

PORTIA_RESPONSE_TOOL: dict[str, Any] = {
    "name": "portia_response",
    "description": (
        "Korean in-game line for The Merchant of Venice trial "
        "(narration, Portia reaction, or ending)."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "text": {
                "type": "string",
                "description": (
                    "Player-facing Korean prose, 1–4 sentences, "
                    "faithful to Shakespeare's Venice trial."
                ),
            },
        },
        "required": ["text"],
    },
}


class PortiaResponseClient(PortiaResponsePort):
    def __init__(self) -> None:
        settings = get_settings()
        self._client = AsyncAnthropic(api_key=settings.llm_api_key)

    async def generate(self, prompt: PortiaResponsePromptDto) -> PortiaResponseResultDto:
        message = await self._client.messages.create(
            model=MODEL_ID,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": build_user_message(prompt),
                }
            ],
            tools=[PORTIA_RESPONSE_TOOL],
            tool_choice={"type": "tool", "name": "portia_response"},
        )

        for block in message.content:
            if block.type == "tool_use" and block.name == "portia_response":
                payload = block.input if isinstance(block.input, dict) else {}
                text = str(payload.get("text", "")).strip()
                if text:
                    return PortiaResponseResultDto(text=text)

        text_blocks = [b.text for b in message.content if hasattr(b, "text")]
        return PortiaResponseResultDto(text=" ".join(text_blocks).strip())
