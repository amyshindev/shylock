# Backend 디렉터리 구조

`backend/` 루트 기준. `__pycache__` 등 캐시 디렉터리는 생략.

```
backend/
├── Dockerfile
├── alembic.ini
├── main.py
├── pyproject.toml
├── .env.example
│
├── alembic/
│   ├── env.py
│   └── versions/
│       ├── 001_initial_shylock_trial.py
│       ├── 002_add_scene_dialogues_json.py
│       └── 003_hp_dp_gauges.py
│
├── infrastructure/
│   ├── __init__.py
│   ├── config.py          # 환경 설정 (DB, Redis, API 키 등)
│   ├── database.py        # SQLAlchemy async engine / session
│   └── redis.py           # Redis 클라이언트
│
└── apps/
    ├── __init__.py
    └── shylock_trial/
        ├── __init__.py
        │
        ├── dependencies/                    # FastAPI DI 프로바이더
        │   ├── evidence_search_provider.py
        │   ├── portia_response_provider.py
        │   └── trial_progression_provider.py
        │
        ├── domain/                          # 도메인 모델
        │   ├── entities/
        │   │   ├── evidence_entity.py
        │   │   ├── play_line_entity.py
        │   │   └── trial_entity.py
        │   └── value_objects/
        │       ├── dp_score_vo.py
        │       ├── portia_hp_score_vo.py
        │       └── shylock_hp_score_vo.py
        │
        ├── app/                             # 애플리케이션 레이어
        │   ├── constants/
        │   │   ├── ending_type_map.py
        │   │   ├── game_balance.py
        │   │   ├── portia_prompt.py
        │   │   ├── scene_catalog.py
        │   │   └── scene_choices.py
        │   ├── dtos/
        │   │   ├── evidence_search_dto.py
        │   │   ├── portia_response_dto.py
        │   │   ├── scene_dialogue_dto.py
        │   │   └── trial_progression_dto.py
        │   ├── ports/
        │   │   ├── input/                   # 유스케이스 인터페이스
        │   │   │   ├── evidence_search_use_case.py
        │   │   │   ├── portia_response_use_case.py
        │   │   │   └── trial_progression_use_case.py
        │   │   └── output/                  # 저장소·외부 서비스 인터페이스
        │   │       ├── evidence_search_port.py
        │   │       ├── portia_response_port.py
        │   │       ├── trial_progression_cache_port.py
        │   │       └── trial_progression_port.py
        │   ├── use_cases/                   # 인터랙터 (비즈니스 로직)
        │   │   ├── evidence_search_interactor.py
        │   │   ├── portia_response_interactor.py
        │   │   └── trial_progression_interactor.py
        │   └── utils/
        │       ├── dialogue_text.py
        │       ├── portia_text.py
        │       └── scene_dialogue_store.py
        │
        ├── adapter/                         # 헥사고날 어댑터
        │   ├── inbound/
        │   │   └── api/
        │   │       ├── router_registry.py
        │   │       ├── schemas/
        │   │       │   ├── evidence_search_schema.py
        │   │       │   ├── portia_response_schema.py
        │   │       │   └── trial_progression_schema.py
        │   │       └── v1/
        │   │           ├── evidence_search_router.py
        │   │           └── trial_progression_router.py
        │   └── outbound/
        │       ├── cache/
        │       │   └── trial_progression_cache.py
        │       ├── client/
        │       │   ├── evidence_embedding_client.py
        │       │   └── portia_response_client.py
        │       ├── mappers/
        │       │   ├── evidence_search_mapper.py
        │       │   └── trial_progression_mapper.py
        │       ├── memory/                  # 인메모리 저장소 (개발/테스트)
        │       │   ├── evidence_search_repository.py
        │       │   └── trial_progression_repository.py
        │       ├── orm/                     # SQLAlchemy 모델
        │       │   ├── play_line_orm.py
        │       │   └── trial_orm.py
        │       ├── pg/                      # PostgreSQL 저장소
        │       │   ├── evidence_search_repository.py
        │       │   └── trial_progression_repository.py
        │       └── seeding/
        │           └── evidence_search_corpus_seeder.py
        │
        └── tests/
            ├── adapter/
            │   └── outbound/
            │       └── mappers/
            │           └── test_trial_progression_mapper.py
            ├── app/
            │   ├── use_cases/
            │   │   └── test_trial_progression_interactor.py
            │   └── utils/
            │       ├── test_dialogue_text.py
            │       ├── test_portia_text.py
            │       └── test_scene_dialogue_store.py
            └── domain/
                └── test_ending_and_scores.py
```

## 레이어 요약

| 경로 | 역할 |
|------|------|
| `infrastructure/` | DB·Redis·설정 등 공통 인프라 |
| `domain/` | 엔티티, 값 객체 (프레임워크 무관) |
| `app/ports/` | 인바운드·아웃바운드 포트 (인터페이스) |
| `app/use_cases/` | 유스케이스 구현 (인터랙터) |
| `adapter/inbound/` | HTTP API (FastAPI 라우터·스키마) |
| `adapter/outbound/` | DB, Redis, LLM 클라이언트 등 외부 연동 |
| `dependencies/` | FastAPI `Depends` 와이어링 |
| `alembic/` | DB 마이그레이션 |
