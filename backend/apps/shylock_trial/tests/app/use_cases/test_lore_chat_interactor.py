import pytest

from shylock_trial.app.dtos.evidence_search_dto import EvidenceSearchResultDto
from shylock_trial.app.dtos.lore_chat_dto import LoreChatAskInputDto, LoreChatTurnDto
from shylock_trial.app.use_cases.lore_chat_interactor import (
    MAX_HISTORY_TURNS_FOR_LLM,
    LoreChatInteractor,
)
from shylock_trial.domain.entities.play_line_entity import PlayLine


class FakeEvidenceSearchUseCase:
    def __init__(self, play_lines: tuple[PlayLine, ...] = ()) -> None:
        self.play_lines = play_lines
        self.last_query: str | None = None

    async def search(self, input_dto):
        self.last_query = input_dto.query
        return EvidenceSearchResultDto(play_lines=self.play_lines)

    async def search_scored(self, input_dto):
        raise AssertionError("not used by lore_chat")

    async def list_curated_evidence(self):
        raise AssertionError("not used by lore_chat")

    async def get_evidence(self, evidence_id):
        raise AssertionError("not used by lore_chat")

    async def get_line_context(self, ftln_start, ftln_end, radius=2):
        raise AssertionError("not used by lore_chat")

    async def get_lines_by_topic(self, topic_id):
        raise AssertionError("not used by lore_chat")


class FakeLoreChatLlm:
    def __init__(self, answer_text: str = "fake answer") -> None:
        self.answer_text = answer_text
        self.received_history: tuple[LoreChatTurnDto, ...] | None = None
        self.received_passages = None

    async def answer(self, question, history, passages):
        self.received_history = history
        self.received_passages = passages
        return self.answer_text


class FakeLoreChatHistory:
    def __init__(self) -> None:
        self._store: dict[str, list[LoreChatTurnDto]] = {}

    async def get(self, session_id):
        return tuple(self._store.get(session_id, ()))

    async def append(self, session_id, turn):
        self._store.setdefault(session_id, []).append(turn)


def _make_play_line(ftln: int = 1, text: str = "quote") -> PlayLine:
    return PlayLine(ftln=ftln, speaker="SHYLOCK", text=text, act_scene="1.3")


@pytest.mark.asyncio
async def test_ask_generates_session_id_when_absent() -> None:
    interactor = LoreChatInteractor(
        evidence=FakeEvidenceSearchUseCase(),
        llm=FakeLoreChatLlm(),
        history=FakeLoreChatHistory(),
    )

    result = await interactor.ask(LoreChatAskInputDto(message="누가 안토니오인가요?"))

    assert result.session_id


@pytest.mark.asyncio
async def test_ask_reuses_provided_session_id_and_persists_turns() -> None:
    history = FakeLoreChatHistory()
    interactor = LoreChatInteractor(
        evidence=FakeEvidenceSearchUseCase(),
        llm=FakeLoreChatLlm(answer_text="살 1파운드는 계약 조건이었습니다."),
        history=history,
    )

    result = await interactor.ask(
        LoreChatAskInputDto(session_id="session-1", message="살 1파운드가 뭔가요?")
    )

    assert result.session_id == "session-1"
    stored = await history.get("session-1")
    assert stored == (
        LoreChatTurnDto(role="human", content="살 1파운드가 뭔가요?"),
        LoreChatTurnDto(role="ai", content="살 1파운드는 계약 조건이었습니다."),
    )


@pytest.mark.asyncio
async def test_ask_passes_search_results_as_sources() -> None:
    play_line = _make_play_line(ftln=470, text="Let the forfeit be an equal pound of flesh")
    llm = FakeLoreChatLlm()
    interactor = LoreChatInteractor(
        evidence=FakeEvidenceSearchUseCase(play_lines=(play_line,)),
        llm=llm,
        history=FakeLoreChatHistory(),
    )

    result = await interactor.ask(LoreChatAskInputDto(message="살 1파운드 조항 원문이 뭔가요?"))

    assert llm.received_passages == (play_line,)
    assert len(result.sources) == 1
    assert result.sources[0].ftln == 470
    assert result.sources[0].act_scene == "1.3"


@pytest.mark.asyncio
async def test_ask_caps_history_sent_to_llm() -> None:
    session_id = "long-session"
    history = FakeLoreChatHistory()
    for i in range(30):
        await history.append(session_id, LoreChatTurnDto(role="human", content=f"q{i}"))

    llm = FakeLoreChatLlm()
    interactor = LoreChatInteractor(
        evidence=FakeEvidenceSearchUseCase(),
        llm=llm,
        history=history,
    )

    await interactor.ask(LoreChatAskInputDto(session_id=session_id, message="새 질문"))

    assert llm.received_history is not None
    assert len(llm.received_history) == MAX_HISTORY_TURNS_FOR_LLM
    assert llm.received_history[-1].content == "q29"
