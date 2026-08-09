from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.database import get_corpus_db_session
from shylock_trial.adapter.outbound.pg.character_relation_repository import (
    CharacterRelationPgRepository,
)
from shylock_trial.app.ports.input.character_relation_use_case import CharacterRelationUseCase
from shylock_trial.app.ports.output.character_relation_port import CharacterRelationPort
from shylock_trial.app.use_cases.character_relation_interactor import CharacterRelationInteractor


def get_character_relation_repository(
    session: Annotated[AsyncSession | None, Depends(get_corpus_db_session)],
) -> CharacterRelationPort:
    # No memory/-store fallback (unlike evidence_search_provider) — nothing
    # consumes this yet (no router; see character_relation_repository.py's
    # module docstring for why the pathfinding piece needs a real Postgres
    # session), so there's no live path that would need one. Add
    # InMemoryCharacterRelationRepository if/when that changes.
    if session is None:
        raise RuntimeError("DB session required for CharacterRelationPort")
    return CharacterRelationPgRepository(session=session)


def get_character_relation_use_case(
    port: CharacterRelationPort = Depends(get_character_relation_repository),
) -> CharacterRelationUseCase:
    return CharacterRelationInteractor(port=port)
