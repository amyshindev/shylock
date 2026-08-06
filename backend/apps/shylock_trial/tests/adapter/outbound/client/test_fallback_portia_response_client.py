from uuid import uuid4

import pytest

from shylock_trial.adapter.outbound.client.fallback_portia_response_client import (
    FallbackPortiaResponseClient,
)
from shylock_trial.app.dtos.portia_response_dto import (
    PortiaResponsePromptDto,
    PortiaResponseResultDto,
)
from shylock_trial.app.dtos.scene_dialogue_dto import (
    SceneDialogueContent,
    SceneDialoguePromptDto,
    SceneDialogueResultDto,
)
from shylock_trial.app.ports.output.portia_response_port import PortiaResponsePort
from shylock_trial.domain.entities.trial_entity import TrialPhase


class FakePortiaResponsePort(PortiaResponsePort):
    def __init__(self, *, result=None, scene_result=None, raises: Exception | None = None) -> None:
        self._result = result
        self._scene_result = scene_result
        self._raises = raises
        self.generate_calls = 0
        self.generate_scene_dialogue_calls = 0

    async def generate(self, prompt: PortiaResponsePromptDto) -> PortiaResponseResultDto:
        self.generate_calls += 1
        if self._raises is not None:
            raise self._raises
        return self._result

    async def generate_scene_dialogue(self, prompt: SceneDialoguePromptDto) -> SceneDialogueResultDto:
        self.generate_scene_dialogue_calls += 1
        if self._raises is not None:
            raise self._raises
        return self._scene_result


def _reaction_prompt() -> PortiaResponsePromptDto:
    return PortiaResponsePromptDto(
        trial_id=uuid4(),
        scene_index=1,
        dp=55,
        phase=TrialPhase.IN_PROGRESS,
        choice_history=("bond_signature",),
        context="choice:bond_signature",
        request_type="reaction",
        portia_hp=80,
        choice_id="bond_signature",
    )


def _scene_prompt() -> SceneDialoguePromptDto:
    return SceneDialoguePromptDto(trial_id=uuid4(), scene_index=1, dp=50, choice_history=())


@pytest.mark.asyncio
async def test_generate_uses_primary_when_it_succeeds() -> None:
    primary = FakePortiaResponsePort(result=PortiaResponseResultDto(text="from primary"))
    fallback = FakePortiaResponsePort(result=PortiaResponseResultDto(text="from fallback"))
    client = FallbackPortiaResponseClient(primary=primary, fallback=fallback)

    result = await client.generate(_reaction_prompt())

    assert result.text == "from primary"
    assert fallback.generate_calls == 0


@pytest.mark.asyncio
async def test_generate_falls_back_when_primary_raises() -> None:
    primary = FakePortiaResponsePort(raises=TimeoutError("ollama unreachable"))
    fallback = FakePortiaResponsePort(result=PortiaResponseResultDto(text="from fallback"))
    client = FallbackPortiaResponseClient(primary=primary, fallback=fallback)

    result = await client.generate(_reaction_prompt())

    assert result.text == "from fallback"
    assert primary.generate_calls == 1
    assert fallback.generate_calls == 1


@pytest.mark.asyncio
async def test_generate_falls_back_when_primary_result_is_fallback_quality() -> None:
    primary = FakePortiaResponsePort(
        result=PortiaResponseResultDto(text="mangled", fallback_used=True)
    )
    fallback = FakePortiaResponsePort(result=PortiaResponseResultDto(text="from fallback"))
    client = FallbackPortiaResponseClient(primary=primary, fallback=fallback)

    result = await client.generate(_reaction_prompt())

    assert result.text == "from fallback"
    assert fallback.generate_calls == 1


@pytest.mark.asyncio
async def test_generate_returns_last_resort_text_when_both_providers_fail() -> None:
    primary = FakePortiaResponsePort(raises=ConnectionError("ollama unreachable"))
    fallback = FakePortiaResponsePort(raises=RuntimeError("anthropic billing error"))
    client = FallbackPortiaResponseClient(primary=primary, fallback=fallback)

    result = await client.generate(_reaction_prompt())

    assert result.fallback_used is True
    assert result.text == "법정은 그대의 말을 기록에 남기겠소. 다음 절차로 나아가시오."
    assert primary.generate_calls == 1
    assert fallback.generate_calls == 1


@pytest.mark.asyncio
async def test_generate_scene_dialogue_uses_primary_when_it_succeeds() -> None:
    primary_content = SceneDialogueResultDto(content=SceneDialogueContent(lines=()))
    primary = FakePortiaResponsePort(scene_result=primary_content)
    fallback = FakePortiaResponsePort(scene_result=SceneDialogueResultDto(content=SceneDialogueContent(lines=())))
    client = FallbackPortiaResponseClient(primary=primary, fallback=fallback)

    result = await client.generate_scene_dialogue(_scene_prompt())

    assert result is primary_content
    assert fallback.generate_scene_dialogue_calls == 0


@pytest.mark.asyncio
async def test_generate_scene_dialogue_falls_back_when_primary_raises() -> None:
    primary = FakePortiaResponsePort(raises=ConnectionError("refused"))
    fallback_content = SceneDialogueResultDto(content=SceneDialogueContent(lines=()))
    fallback = FakePortiaResponsePort(scene_result=fallback_content)
    client = FallbackPortiaResponseClient(primary=primary, fallback=fallback)

    result = await client.generate_scene_dialogue(_scene_prompt())

    assert result is fallback_content
    assert primary.generate_scene_dialogue_calls == 1
    assert fallback.generate_scene_dialogue_calls == 1


@pytest.mark.asyncio
async def test_generate_scene_dialogue_falls_back_to_canonical_when_both_providers_fail() -> None:
    primary = FakePortiaResponsePort(raises=ConnectionError("ollama unreachable"))
    fallback = FakePortiaResponsePort(raises=RuntimeError("anthropic billing error"))
    client = FallbackPortiaResponseClient(primary=primary, fallback=fallback)

    result = await client.generate_scene_dialogue(_scene_prompt())

    assert result.fallback_used is True
    assert len(result.content.lines) > 0  # canonical scene script, not empty
