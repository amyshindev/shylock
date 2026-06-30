from google import genai
from google.genai import types
from pydantic import BaseModel, Field

from core.config import get_settings
from shylock_trial.app.constants.portia_prompt import SYSTEM_PROMPT, build_user_message
from shylock_trial.app.dtos.portia_response_dto import (
    PortiaResponsePromptDto,
    PortiaResponseResultDto,
)
from shylock_trial.app.ports.output.portia_response_port import PortiaResponsePort
from shylock_trial.app.utils.portia_text import extract_portia_text

# gemini-2.0-flash returns 429 (free-tier quota 0) on some keys; 2.5-flash works.
MODEL_ID = "gemini-2.5-flash"


class PortiaResponseOutput(BaseModel):
    text: str = Field(
        description=(
            "Player-facing Korean prose, 1–4 sentences, "
            "faithful to Shakespeare's Venice trial."
        ),
    )


class PortiaResponseClient(PortiaResponsePort):
    def __init__(self) -> None:
        settings = get_settings()
        self._client = genai.Client(api_key=settings.gemini_api_key())

    async def generate(self, prompt: PortiaResponsePromptDto) -> PortiaResponseResultDto:
        response = await self._client.aio.models.generate_content(
            model=MODEL_ID,
            contents=build_user_message(prompt),
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                max_output_tokens=1024,
                response_mime_type="application/json",
                response_schema=PortiaResponseOutput,
            ),
        )

        parsed = response.parsed
        if isinstance(parsed, PortiaResponseOutput):
            text = parsed.text.strip()
            if text:
                return PortiaResponseResultDto(text=text)

        raw = (response.text or "").strip()
        return PortiaResponseResultDto(text=extract_portia_text(raw))
