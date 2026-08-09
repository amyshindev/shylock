"""Lore Q&A chatbot — the only slice in this app built on LangChain rather than
the raw Anthropic SDK. Unlike portia_response/tubal_agent (structured output,
tool-use loop, hand-tuned prompt caching), this is a single retrieve-then-generate
call with free-form conversation history, which is what LangChain's prompt
composition + LCEL piping is actually good at.
"""

from __future__ import annotations

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from infrastructure.config import get_settings
from shylock_trial.app.constants.lore_chat_prompt import (
    LORE_CHAT_SYSTEM_PROMPT,
    build_context_block,
    format_passage,
)
from shylock_trial.app.dtos.lore_chat_dto import LoreChatTurnDto
from shylock_trial.app.ports.output.lore_chat_llm_port import LoreChatLlmPort
from shylock_trial.domain.entities.play_line_entity import PlayLine


def _to_lc_messages(history: tuple[LoreChatTurnDto, ...]) -> list[BaseMessage]:
    return [
        HumanMessage(content=turn.content) if turn.role == "human" else AIMessage(content=turn.content)
        for turn in history
    ]


class LoreChatClient(LoreChatLlmPort):
    def __init__(self) -> None:
        settings = get_settings()
        llm = ChatAnthropic(
            model=settings.lore_chat_model_id,
            api_key=settings.anthropic_api_key_plain(),
            max_tokens=1024,
        )
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", LORE_CHAT_SYSTEM_PROMPT),
                MessagesPlaceholder("history"),
                ("human", "{character_context}\n\n{context}\n\n질문: {question}"),
            ]
        )
        self._chain = prompt | llm | StrOutputParser()

    async def answer(
        self,
        question: str,
        history: tuple[LoreChatTurnDto, ...],
        passages: tuple[PlayLine, ...],
        character_context: str = "",
    ) -> str:
        context = build_context_block([format_passage(line) for line in passages])
        result = await self._chain.ainvoke(
            {
                "history": _to_lc_messages(history),
                "context": context,
                "character_context": character_context,
                "question": question,
            }
        )
        return result.strip()
