from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.config import get_settings
from infrastructure.database import get_corpus_db_session
from infrastructure.neo4j_driver import get_neo4j_driver
from shylock_trial.adapter.outbound.memory.character_relation_repository import (
    NullCharacterRelationRepository,
)
from shylock_trial.adapter.outbound.neo4j.character_relation_repository import (
    CharacterRelationNeo4jRepository,
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
    # CHARACTER_RELATION_BACKEND(기본값 "pg")가 어느 게이트웨이를 쓸지
    # 결정한다 — LLM_PROVIDER/EMBEDDING_PROVIDER와 같은 독립 스위치 패턴
    # (infrastructure/config.py 참고). "neo4j"를 골라도 위 session 파라미터는
    # 여전히 resolve된다(FastAPI가 Depends를 즉시 평가하므로) — 미사용
    # Postgres corpus 세션 하나가 낭비되는 정도라 눈감아줄 만한 트레이드오프다;
    # 이 스위치가 상시 요청 경로가 아니라 포트폴리오용 대안 게이트웨이를
    # 보여주는 용도라 굳이 조건부 Depends 체인으로 더 복잡하게 만들지 않았다.
    if get_settings().character_relation_backend == "neo4j":
        return CharacterRelationNeo4jRepository(driver=get_neo4j_driver())

    # corpus DB 세션이 없으면 NullCharacterRelationRepository(진짜 in-memory
    # 미러가 아님 — 자체 docstring 참고)를 쓴다. 그래서 USE_MEMORY_STORE /
    # DATABASE_URL 미설정 로컬 dev 환경은 하드 실패 대신 "character context
    # 없음"으로 우아하게 떨어진다. 이 스템은 이제 선택적인 lore_chat
    # 위젯뿐 아니라 핵심 submit_choice 경로(trial_progression_interactor의
    # 반응 프롬프트)에도 실사용자가 있으므로, 여기서 예외를 던질 여유가
    # 더는 없다.
    if session is None:
        return NullCharacterRelationRepository()
    return CharacterRelationPgRepository(session=session)


def get_character_relation_use_case(
    port: CharacterRelationPort = Depends(get_character_relation_repository),
) -> CharacterRelationUseCase:
    return CharacterRelationInteractor(port=port)
