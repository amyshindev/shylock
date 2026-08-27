"""Neo4j 드라이버 싱글턴 — infrastructure/database.py의 get_engine()/
get_session_factory() 패턴을 그대로 미러링한다. SQLAlchemy의 AsyncEngine과
마찬가지로 neo4j.AsyncDriver 자체가 내부 커넥션 풀을 들고 있는 무거운
객체라, 요청마다 새로 만들지 않고 프로세스당 하나만 유지한다 — 실제
단위 작업(unit of work)은 driver.session()으로 그때그때 가볍게 여는
Neo4j 세션이 담당한다(character_relation_neo4j_repository.py 참고)."""

from neo4j import AsyncDriver, AsyncGraphDatabase

from infrastructure.config import get_settings

_driver: AsyncDriver | None = None


def get_neo4j_driver() -> AsyncDriver:
    global _driver
    if _driver is None:
        settings = get_settings()
        _driver = AsyncGraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_user, settings.neo4j_password_plain()),
        )
    return _driver


async def close_neo4j_driver() -> None:
    """앱 종료 시(lifespan shutdown) 호출 — 열린 커넥션 풀을 정리한다."""
    global _driver
    if _driver is not None:
        await _driver.close()
        _driver = None
