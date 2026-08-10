from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.database import get_corpus_db_session
from shylock_trial.adapter.outbound.memory.character_relation_repository import (
    NullCharacterRelationRepository,
)
from shylock_trial.adapter.outbound.pg.character_relation_repository import (
    CharacterRelationPgRepository,
)
from shylock_trial.app.ports.input.character_relation_use_case import CharacterRelationUseCase
from shylock_trial.app.ports.output.character_relation_port import CharacterRelationPort
from shylock_trial.app.use_cases.character_relation_interactor import CharacterRelationInteractor


def get_character_relation_repository(
    session: Annotated[AsyncSession | None, Depends(get_corpus_db_session)],
) -> CharacterRelationPort:
    # NullCharacterRelationRepository (not a real in-memory mirror — see its
    # own docstring) when there's no corpus DB session, so USE_MEMORY_STORE /
    # no-DATABASE_URL local dev degrades to "no character context" instead of
    # hard-failing. This stem now has a live consumer on the core submit_choice
    # path (trial_progression_interactor's reaction prompt), not just the
    # optional lore_chat widget, so it can no longer afford to raise here.
    if session is None:
        return NullCharacterRelationRepository()
    return CharacterRelationPgRepository(session=session)


def get_character_relation_use_case(
    port: CharacterRelationPort = Depends(get_character_relation_repository),
) -> CharacterRelationUseCase:
    return CharacterRelationInteractor(port=port)
