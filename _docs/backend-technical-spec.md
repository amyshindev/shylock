# 샤일록의 법정 — 백엔드 기술명세서

> Claude Code 구현 레퍼런스용
> Hexagonal + DDD + Vertical Slice (Titanic 아키텍처 표준 준수)
> 작성일: 2026-06-30

---

## 0. 아키텍처 표준 출처

본 문서는 `structure.md`(Titanic 아키텍처 참조 가이드)가 정의한
레이어 구조·명명 규칙·슬라이스 패턴을 그대로 따른다. `structure.md`
9장의 안티패턴 표가 명시하듯, 캐릭터 이름은 Titanic 같은 교육용
도메인에 한정된 관례이고 다른 앱은 "도메인에 맞는 접두사"를 쓰면
된다 — 본 프로젝트는 동사형 stem(`trial_progression`,
`portia_response`, `evidence_search`)을 채택한다(1.4절).

새 도메인 앱 뼈대를 만드는 절차(`structure.md` §8: "Titanic을
폴더 단위로 복사한 뒤 이름만 바꾼다")를 그대로 따르되, 본 게임은
`apps/shylock_trial/`이라는 독립 앱으로 둔다(7장).

---

## 1. 개요

### 1.1 목적
본 문서는 `shylock-trial.jsx` 데모(Claude API 직접 호출 방식)를 실서비스
수준의 백엔드로 전환하기 위한 아키텍처 명세서다. 코드 구현은 다루지
않으며, 모듈 경계·책임·기술 스택·데이터 흐름만 정의한다.

**선행 조건 — 인증 문제 해결이 본 백엔드 도입의 1차 목적이다.**
`game-technical-spec.md` §4.1에서 이미 지적되었듯, 현재 데모는 Claude
API를 클라이언트에서 직접 `fetch`로 호출하며 인증 헤더(`x-api-key` 등)를
일절 포함하지 않는다. 이는 Artifact 환경의 프록시 처리에 의존하는
임시방편이며, 어떤 형태로든 환경을 이식하면 그대로 401/403 에러로
이어진다. 본 백엔드는 이 문제를 근본적으로 해결한다 — `LLM_API_KEY`는
오직 6.1절의 outbound Adapter 내부(서버 환경변수)에만 존재하며,
프론트엔드는 Claude API의 존재 자체를 모른 채 자체 API(8장)만 호출한다.

### 1.2 설계 원칙 (Titanic 표준 매핑)

| 원칙 | `structure.md` 근거 | 본 게임에서의 적용 |
|---|---|---|
| Hexagonal (Ports & Adapters) | §2.1 | `domain`은 FastAPI·SQLAlchemy·Anthropic SDK를 import하지 않는다. 모든 외부 의존은 `app/ports/output/`의 Port(ABC)로 추상화하고, `adapter/outbound/`가 구현한다 |
| Vertical Slice | §2.2 | 캐릭터 1명 = 슬라이스 1개라는 Titanic 패턴 대신, 동사형 stem 1개 = 슬라이스 1개(1.4절) |
| 의존성 방향 | §2.3 | `adapter/inbound → app → domain`, `adapter/outbound → app`, `domain`은 outbound를 모름 |
| Use Case 분리 | §3.2~3.3 | Router·Interactor가 같은 `app/ports/input/{stem}_use_case.py` 계약을 공유 |
| DI 단일 지점 | §3.7 | `Depends()`는 router와 `dependencies/{stem}_provider.py`에만 존재 |

### 1.3 기존 프로젝트와의 연속성
SoundBridge(헥사고날 + pgvector)와 Konceit(tool_use 오케스트레이션)에서
검증된 패턴을 계승하되, 본 프로젝트부터는 `structure.md`가 정의한
Titanic 표준 레이어 명칭(`adapter/inbound`, `app/ports/input`,
`app/ports/output`, `app/use_cases`, `dependencies`)을 정식 채택한다.
이전 버전의 본 문서가 쓰던 `orchestration/`, `infrastructure/`라는
이름은 본 개정판부터 폐기되었다 — Claude Code가 과거 버전의 명세서나
대화 이력을 참조할 경우, 이름이 다르더라도 동일한 책임을 가리킨다는
점을 인지할 것(아래 1.5절 대조표 참조).

### 1.4 슬라이스(stem) 정의

`structure.md` §2.2가 요구하는 "슬라이스마다 동일한 stem을 파일명에
반복"하는 규칙에 따라, 본 게임은 책임 단위로 3개의 stem을 둔다.
Titanic의 분할 기준(메서드 단위가 아니라 "하나의 책임을 지는 행위자
단위" — Rose가 `train`/`predict`/`introduce_myself`를 한 Interactor에
묶어 갖듯)을 그대로 따른다.

| stem | 책임 | Titanic 유비 |
|---|---|---|
| `trial_progression` | 재판 시작·선택지 처리·장면 전환·엔딩 판정을 모두 포함하는 단일 행위자. 기존 문서의 4개 오케스트레이터(StartTrial, SubmitChoice, AdvanceScene, GenerateEnding)는 메서드 단위 분할이었으나, Rose 패턴(여러 메서드를 한 Interactor에)에 따라 **하나의 Interactor**로 합친다 | Rose(`train`/`predict`/`introduce_myself`를 한 Interactor가 가짐) |
| `portia_response` | Claude API를 호출해 포샤의 AI 반응·엔딩 서사를 생성하는 행위자 | Smith의 outbound 호출 부분(Gemini 채팅) |
| `evidence_search` | pgvector 기반 원문 검색을 담당하는 행위자 | Walter(CSV 데이터 소스 추상화) — 단, 여기서는 PostgreSQL+pgvector가 데이터 소스 |

**왜 4개 오케스트레이터를 1개 stem으로 합쳤는가:** 기존 문서는
`StartTrialOrchestrator`, `SubmitChoiceOrchestrator`,
`AdvanceSceneOrchestrator`, `GenerateEndingOrchestrator`를 별도
파일로 뒀다. 그러나 이 넷은 모두 "재판 진행 상태(`Trial` Aggregate)를
다루는 하나의 책임"이라는 공통점을 가지며, `structure.md` §6.1의
Rose 사례("모델 서빙 + 소개 API가 한 bounded context면 Interactor
하나로 유지")가 정확히 이 상황에 해당한다. 따라서
`TrialProgressionInteractor` 하나가 `start`, `submit_choice`,
`advance_scene`, `generate_ending` 네 메서드를 갖는다(5장).

### 1.5 이전 버전 명칭 대조표

과거 본 문서(또는 이전 대화)가 사용했던 명칭과 본 개정판의 대응
관계. Claude Code가 작업 이력 전체를 참조할 때 혼동을 막기 위함.

| 폐기된 명칭 | Titanic 표준 명칭 | 비고 |
|---|---|---|
| `orchestration/*_orchestrator.py` | `app/use_cases/{stem}_interactor.py` | 4개 파일 → `trial_progression_interactor.py` 1개로 통합(1.4절) |
| `domain/*/ports.py`(컨텍스트별 분산) | `app/ports/input/{stem}_use_case.py` + `app/ports/output/{stem}_port.py` | input/output 분리, 위치도 domain 밖으로 이동 |
| `infrastructure/llm/claude_adapter.py` | `adapter/outbound/client/portia_response_client.py` | client 하위로 |
| `infrastructure/persistence/postgres_trial_repository.py` | `adapter/outbound/pg/trial_progression_repository.py` | |
| `infrastructure/search/pgvector_evidence_search.py` | `adapter/outbound/pg/evidence_search_repository.py` | |
| `infrastructure/embedding/cohere_embedding_adapter.py` | `adapter/outbound/client/evidence_embedding_client.py` | |
| `api/routers/trial_router.py` | `adapter/inbound/api/v1/trial_progression_router.py` | |
| `api/schemas/trial_schemas.py` | `adapter/inbound/api/schemas/trial_progression_schema.py` | |
| `config/container.py` | `dependencies/{stem}_provider.py`(슬라이스별 분산) | 단일 파일 → stem마다 분리 |
| Value Object가 계층 간 전달 데이터 겸용 | `app/dtos/{stem}_dto.py` 별도 분리 | `structure.md` §3.8 |

---

## 2. 레이어 구조

```text
        [ HTTP ]                          ← adapter/inbound
                 │
         app/ports/input  (UseCase ABC)
                 │
           app/use_cases  (Interactor)
                 │
        app/ports/output  (Port ABC)
                 │
    [ PostgreSQL / pgvector / Claude API / Cohere ]  ← adapter/outbound
```

`structure.md` §2.3의 의존성 방향을 그대로 따른다.

```text
adapter/inbound  →  app  →  domain
adapter/outbound →  app           (domain은 outbound를 모른다)
dependencies     →  adapter + app (조립만)
main.py          →  router_registry만 등록
```

| 금지 | 이유 |
|---|---|
| `domain` → `fastapi`, `sqlalchemy`, `anthropic` | 순수 모델 오염 |
| `app/use_cases` 안에 `Depends()` | 테스트·재사용 불가 |
| `adapter` 끼리 직접 import | 레이어 우회 |
| 다른 앱(`apps/*`)의 adapter 직접 참조 | `core/` 또는 Port 경계로 공유 |

---

## 3. 디렉토리 구조

`structure.md` §8("Titanic을 폴더 단위로 복사한 뒤 이름만 바꾼다")에
따라, 본 게임은 모노레포 안의 독립 앱 `apps/shylock_trial/`로 둔다.

```text
backend/
├── main.py                              # shylock_trial_router 등 앱별 router include만
├── core/                                # DB 커넥션, Claude/Cohere 키 관리 등 공유 인프라
└── apps/
    └── shylock_trial/
        ├── adapter/
        │   ├── inbound/
        │   │   └── api/
        │   │       ├── schemas/
        │   │       │   ├── trial_progression_schema.py
        │   │       │   ├── portia_response_schema.py
        │   │       │   └── evidence_search_schema.py
        │   │       ├── v1/
        │   │       │   ├── trial_progression_router.py
        │   │       │   └── evidence_search_router.py
        │   │       └── router_registry.py
        │   └── outbound/
        │       ├── pg/
        │       │   ├── trial_progression_repository.py
        │       │   └── evidence_search_repository.py
        │       ├── orm/
        │       │   ├── trial_orm.py
        │       │   └── play_line_orm.py        # 8.2절 PlayLine 코퍼스
        │       ├── mappers/
        │       │   ├── trial_progression_mapper.py
        │       │   └── evidence_search_mapper.py
        │       ├── client/
        │       │   ├── portia_response_client.py     # Claude API 호출
        │       │   └── evidence_embedding_client.py  # Cohere embed-v4.0
        │       └── seeding/                     # Adapter가 아닌 1회성 배치(6.4절과 동일 역할)
        │           └── evidence_search_corpus_seeder.py  # Folger API → PlayLine 적재
        ├── app/
        │   ├── ports/
        │   │   ├── input/
        │   │   │   ├── trial_progression_use_case.py
        │   │   │   └── evidence_search_use_case.py
        │   │   └── output/
        │   │       ├── trial_progression_port.py
        │   │       ├── portia_response_port.py
        │   │       └── evidence_search_port.py
        │   ├── use_cases/
        │   │   ├── trial_progression_interactor.py   # start/submit_choice/advance_scene/generate_ending
        │   │   └── evidence_search_interactor.py
        │   ├── dtos/
        │   │   ├── trial_progression_dto.py
        │   │   ├── portia_response_dto.py             # NarrationPrompt/NarrationResult 대응
        │   │   └── evidence_search_dto.py
        │   └── constants/
        │       └── ending_type_map.py            # victory/standard_defeat/silent_defeat 임계값
        ├── domain/
        │   ├── entities/
        │   │   ├── trial_entity.py               # Trial, Scene, Choice
        │   │   ├── evidence_entity.py             # 큐레이션된 6개 Evidence
        │   │   └── play_line_entity.py            # 전체 코퍼스 PlayLine
        │   └── value_objects/
        │       ├── dignity_score_vo.py            # 0~100 클램핑 불변값
        │       └── confidence_score_vo.py
        ├── dependencies/
        │   ├── trial_progression_provider.py
        │   ├── portia_response_provider.py
        │   └── evidence_search_provider.py
        ├── tests/
        │   ├── domain/
        │   ├── app/use_cases/
        │   └── adapter/outbound/mappers/
        └── _docs/
            ├── CLAUDE.md                          # 본 게임 도메인 규칙(별도 작성 필요)
            └── structure.md                       # 본 문서 또는 요약 링크
```

**Titanic과의 의도적 차이 — VO 위치.** `structure.md` §3.6은 VO가
"캐릭터별이 아니라 도메인 피처별"이어야 한다고 명시한다. 본 게임의
`DignityScore`, `ConfidenceScore`는 Titanic의 `Age`, `Gender`처럼
피처 단위 VO이므로 이 원칙을 그대로 따른다 — stem별로 쪼개지 않고
`domain/value_objects/`에 공유 VO로 둔다.

---

## 4. 도메인 모델 (`domain/`)

### 4.1 Entity — `trial_entity.py`

게임의 중심 Aggregate Root.

- `Trial`: `trial_id`, 현재 `scene_index`, `dignity`(DignityScore VO),
  `confidence`(ConfidenceScore VO), 선택 이력(`choice_history`),
  상태(`phase`: in_progress / ended)를 가진다.
- `Scene`: 장면 정의(화자, 대사, 선택지 목록). 정적 데이터에 가깝지만
  도메인 규칙(어떤 선택지가 어떤 효과를 갖는지)을 캡슐화한다.
- `Choice`: 플레이어가 고를 수 있는 선택지. 결부된 증거, 존엄/확신도
  변화량, 특수 플래그(climax 여부)를 가진다.

### 4.2 Entity — `evidence_entity.py` / `play_line_entity.py`

원문 데이터를 두 계층으로 구분한다(데이터 소스는 6.4절 참조).

**데이터 소스 — Folger Digital Texts.** 원문 전체는
`folgerdigitaltexts.org`의 *The Merchant of Venice*(play code: `MV`)를
사용한다. Barbara Mowat·Paul Werstine이 편집한 Folger Shakespeare
Library 정본이며, 전체 소스 코드를 비상업적 용도로 무료 다운로드할
수 있다. Folger는 `ftln`(Folger Throughline Number) 기준 단일 행
조회, `text` 함수로 전체 대사, `charText` 함수로 인물별 대사 목록을
제공하는 API도 함께 제공한다. Konceit에서 이미 사용 중인 데이터
소스와 동일하므로 별도 학습 비용이 들지 않는다.

- `PlayLine`(`play_line_entity.py`): 희곡 전체 대사 중 한 줄.
  `ftln`, `speaker`, `text`, `act_scene`을 가진다. 전체 코퍼스를
  구성하는 가장 작은 단위이며 `evidence_search` 슬라이스의 검색
  대상이다.
- `Evidence`(`evidence_entity.py`): 게임이 명시적으로 의미를 부여한
  핵심 증거(현재 6개: gaberdine, bond, hath_not, jessica, mercy,
  blood). `quote`, `act_scene`, `icon`, `description`, 그리고
  `source_ftln_range`(원본 `PlayLine` 범위 참조)를 가진다.
  `trial_progression` 슬라이스가 선택지의 `evidence` 필드로 참조하는
  대상은 이 Entity이며, `PlayLine`을 직접 참조하지 않는다.

즉 `PlayLine`은 검색 가능한 "재료", `Evidence`는 게임 메커니즘
(존엄/확신도 변화)에 결부되도록 큐레이션된 "완성품"이다. 향후 6개
외의 구절을 증거로 채택하려면, 해당 `PlayLine` 범위를 골라 새
`Evidence`로 승격시키는 방식을 취한다.

### 4.3 Value Object — `dignity_score_vo.py` / `confidence_score_vo.py`

`structure.md` §3.6의 "피처 단위 VO" 원칙에 따라 stem과 무관하게
도메인 전역에서 공유한다.

- `DignityScore`: 0~100 범위로 클램핑되는 불변 값 객체.
- `ConfidenceScore`: 위와 동일한 패턴.

### 4.4 상수 — `app/constants/ending_type_map.py`

`structure.md` §6.3(Andrews의 의도 맵 패턴: "Interactor는 상수만
참조, NLP SDK는 outbound")을 그대로 따른다.

- `EndingType` 판정 임계값: victory(존엄 70 이상) /
  standard_defeat(40~69) / silent_defeat(40 미만). Interactor는
  이 상수만 참조하며, 판정 로직 자체는 `trial_progression_interactor.py`
  내부의 순수 함수로 둔다(외부 SDK 의존 없음).

---

## 5. `app/use_cases/trial_progression_interactor.py` — 핵심 슬라이스

가장 무거운 Interactor. Rose 패턴(여러 메서드를 한 Interactor에)에
따라 기존 4개 오케스트레이터를 메서드로 통합한다. 생성자에서
`portia_response`, `evidence_search` 두 하위 Use Case를 주입받는
**Smith 오케스트레이터 패턴**(`structure.md` §3.3, §6.4)을 따른다.

```text
TrialProgressionInteractor
  ├── PortiaResponseUseCase   → Claude API 호출 (4.x 메서드에서 사용)
  ├── EvidenceSearchUseCase   → pgvector 검색 (선택적, 5.2절 참조)
  └── TrialProgressionPort    → PostgreSQL 영속화 (outbound)
```

**순환 의존 방지**(`structure.md` §6.4): `trial_progression` →
`portia_response` / `evidence_search` 방향만 허용한다. 두 하위
Use Case가 `trial_progression`을 거꾸로 참조하지 않는다.

### 5.1 `start(...)`
```
입력: (없음, 새 세션 생성)
흐름:
  1. TrialProgressionPort로 새 Trial Aggregate 생성·저장
  2. PortiaResponseUseCase 호출 → 첫 내레이션 텍스트 획득(Scene 1 맥락)
  3. 결과를 Trial에 반영 후 저장
출력: 초기 Trial 상태 + 첫 장면 텍스트
```

### 5.2 `submit_choice(trial_id, choice_id)`
데모의 `makeChoice` 함수에 대응하는 가장 복잡한 흐름.
```
흐름:
  1. TrialProgressionPort로 현재 Trial 조회
  2. (도메인 순수 로직) 선택지의 dignity/confidence 변화량 적용,
     새 점수 계산 — 외부 호출 없음
  3. 선택지에 결부된 핵심 Evidence가 있으면, 그 주변 맥락을 보강하기
     위해 EvidenceSearchUseCase로 관련 PlayLine 추가 조회 (선택적 —
     핵심 Evidence의 효과치 자체는 4.2절에서 정의했듯 이 검색 결과와
     무관하게 고정값으로 적용됨)
  4. PortiaResponseUseCase 호출 → 포샤의 AI 반응 생성
  5. (도메인 순수 로직) EndingType 판정 — ending_type_map.py 상수 참조
  6. Trial 상태 갱신 후 TrialProgressionPort로 저장
출력: 갱신된 Trial 상태, 포샤 반응 텍스트, 엔딩 여부
```

### 5.3 `advance_scene(trial_id)`
```
흐름:
  1. Trial 조회
  2. (도메인 순수 로직) 다음 Scene 결정
  3. Trial의 scene_index 갱신 후 저장
출력: 다음 장면 데이터
```

### 5.4 `generate_ending(trial_id)`
```
흐름:
  1. Trial 조회 (최종 dignity, confidence, choice_history 포함)
  2. (도메인 순수 로직) EndingType 최종 확정
  3. PortiaResponseUseCase 호출 → 엔딩 텍스트 생성(전체 선택 이력 +
     최종 점수 전달)
  4. Trial을 ended 상태로 갱신, 저장
출력: 엔딩 타입 + 생성된 엔딩 텍스트
```

---

## 6. `app/use_cases/` — 하위 슬라이스

### 6.1 `portia_response_interactor.py`

`app/ports/input/portia_response_use_case.py`(ABC)를 구현. 책임은
"무엇을 생성할지"에 대한 프롬프트 조립 규칙(순수 로직)이며, 실제
LLM 호출은 outbound Port(6.x) 뒤에 위임한다.

- `PortiaResponseDto`(`app/dtos/portia_response_dto.py`): 보스/포샤
  페르소나, 현재 장면 맥락, 미터 상태를 조합해 구조화된 프롬프트를
  만드는 불변 데이터 객체(기존 문서의 `NarrationPrompt`에 대응).
- 응답 파싱 결과를 담는 별도 DTO(기존 `NarrationResult`에 대응)도
  같은 파일에 정의하며, 파싱 실패 시의 처리 규칙(폴백 텍스트 등)을
  포함한다.

### 6.2 `evidence_search_interactor.py`

`app/ports/input/evidence_search_use_case.py`(ABC)를 구현. 특정
선택/맥락에 대해 어떤 `PlayLine`이 가장 관련 있는지 판단하는 규칙.
실제 벡터 유사도 계산은 outbound(`adapter/outbound/pg/evidence_search_repository.py`)의
책임이고, 이 Interactor는 검색 결과를 받아 도메인 규칙에 따라
필터링/우선순위화하는 역할만 한다.

---

## 7. `adapter/outbound/` — 실제 I/O

### 7.1 `client/portia_response_client.py` — `PortiaResponsePort` 구현

- Anthropic Python SDK 사용, `claude-sonnet-4-6` 모델 고정
- **`LLM_API_KEY`는 이 client 내부에서만 환경변수로 읽힌다.**
  `core/`의 설정 모듈을 통해 주입되며, `domain`·`app`·`adapter/inbound`
  레이어 어디에도 이 값이 노출되지 않는다. 프론트엔드는 이 키의
  존재 자체를 알 필요가 없다 — 이것이 §1.1에서 언급한 인증 문제의
  해결책이다.
- `PortiaResponseDto`를 받아 system/user 메시지로 변환, 응답 텍스트를
  파싱해 결과 DTO로 변환(JSON 파싱 실패 시 재시도 또는 폴백 처리)
- tool_use 활용: Konceit에서 검증한 패턴대로, 평가 결과를 자유 텍스트가
  아닌 구조화된 tool_use 응답으로 받아 파싱 안정성 확보

### 7.2 `pg/trial_progression_repository.py` — `TrialProgressionPort` 구현

- `Trial` Aggregate를 관계형 테이블로 영속화
- 주요 테이블: `trials`(메인 상태), `trial_choice_history`(선택 이력
  — 추후 분석/리플레이 기능 확장 대비)
- SQLAlchemy 사용(비동기: `asyncpg` 드라이버), ORM 모델은
  `adapter/outbound/orm/trial_orm.py`, Entity ↔ ORM 변환은
  `adapter/outbound/mappers/trial_progression_mapper.py`(`structure.md`
  §3.5 Mapper 패턴)

### 7.3 `pg/evidence_search_repository.py` — `EvidenceSearchPort` 구현

SoundBridge에서 검증한 pgvector 패턴을 그대로 재사용.

- 희곡 전체 `PlayLine` 코퍼스(약 2,700행 추정 — 정확한 행 수는 시딩
  시 확정)를 `evidence_embedding_client.py`(Cohere `embed-v4.0`)로
  사전 임베딩, pgvector 컬럼에 저장
- 런타임에는 "현재 선택/맥락"을 임베딩해 코사인 유사도로 가장 관련
  높은 `PlayLine` 목록을 검색
- 이제 벡터 검색이 실제로 의미를 갖는 규모다 — 기존 6개 증거만
  대상이었을 때는 사실상 키워드 매칭으로 충분했지만, 전체 코퍼스를
  대상으로 하면서 "선택지 맥락과 의미적으로 가장 가까운 대사 찾기"가
  실질적인 기능이 됨
- 단, 게임의 6개 핵심 `Evidence`는 검색 결과가 아니라 **사전에
  큐레이션된 고정 데이터**다(4.2절). 검색은 어디까지나 "추가로 참고할
  만한 주변 대사를 찾는 보조 기능"이며, 핵심 증거의 효과는 검색
  결과에 좌우되지 않는다.

### 7.4 `client/evidence_embedding_client.py`

- Cohere `embed-v4.0` 호출 전용 client. `evidence_search_repository.py`가
  내부적으로 사용한다(Walter 패턴 — `structure.md` §6.2: "Port 구현체
  안에서 Reader를 감싼다").

### 7.5 세션 상태 — Redis

`structure.md`의 표준 슬라이스 파일 세트(§4)에는 Redis 같은 캐시
계층이 명시적으로 없으나, 본 게임은 "진행 중인 게임의 빠른 상태
조회" 용도로 필요하다. `adapter/outbound/pg/trial_progression_repository.py`와
같은 레벨에 `adapter/outbound/cache/trial_progression_cache.py`를
별도로 두고, `TrialProgressionPort`와는 다른 보조 Port
(`TrialProgressionCachePort`, 선택적)로 분리할 것을 권장한다.

- `trial_id` → 활성 세션 매핑, TTL 설정으로 장시간 미사용 세션 자동
  정리
- PostgreSQL(영구 저장)과 역할 분리: Redis는 "지금 진행 중인 게임의
  빠른 상태 조회", PostgreSQL은 "완료된 게임의 기록"

---

## 8. `adapter/outbound/seeding/` — 데이터 시딩 파이프라인

`structure.md`의 표준 슬라이스 파일 세트에는 없는 본 게임 고유의
1회성 배치 작업. Adapter라기보다 별도 관리 명령(management command)에
가까우며, 애플리케이션의 정상 요청-응답 경로와는 분리되어 운영된다.
그래서 `pg/`, `client/`와 나란히 두되 별도 하위 폴더(`seeding/`)로
명확히 구분한다.

**흐름**
```text
1. Folger Digital Texts API(MV play code)에서 원문 가져오기
   - charText 함수로 인물별 대사 목록을 받거나
   - text 함수로 전체 대사를 받아 act/scene/ftln 기준으로 파싱
2. 각 대사를 act_scene, speaker, ftln, text 필드로 PlayLine 레코드화
3. evidence_embedding_client.py(Cohere embed-v4.0)로 각 PlayLine의
   text를 임베딩
4. PostgreSQL(pgvector 컬럼 포함)에 bulk insert
5. 기존 6개 Evidence 레코드에 source_ftln_range를 매핑
   (수동 매핑 — 어떤 ftln 구간이 어떤 Evidence에 대응하는지는
   기획 의도가 반영된 결정이므로 자동화 대상이 아님)
```

**구현 위치**: `adapter/outbound/seeding/evidence_search_corpus_seeder.py`.
런타임 요청을 처리하는 Adapter와 같은 디렉토리에 섞지 않는다.

**API 호출 vs 직접 파싱**: Folger가 공식 API(`folgerdigitaltexts.org/api`)를
제공하므로, raw 텍스트나 PDF를 직접 파싱하는 방식보다 API 호출을
우선한다. 단, API가 일부 케이스(예: 특정 act/scene 경계의 모호함)에서
기대와 다른 형태로 응답할 수 있으므로, 시딩 스크립트 실행 후 결과
행 수와 act/scene 분포를 사람이 한 번 육안 검증하는 단계를 작업
순서에 포함시킬 것(11장 권장 순서 참조).

**재실행 정책**: 코퍼스는 한 번 시딩되면 거의 불변이다(희곡 원문은
바뀌지 않으므로). 재실행이 필요한 경우는 사실상 임베딩 모델 교체
시뿐이며, 이 경우 기존 `PlayLine` 레코드를 전부 삭제 후 재시딩하는
것을 권장한다.

---

## 9. `adapter/inbound/api/` — Presentation Layer

`structure.md` §3.1의 Router 책임 정의를 그대로 따른다.

**Router가 하는 일 (이것만):**
- HTTP 메서드·경로·status code
- Schema 파싱·`response_model`
- Use Case 호출 + 로깅
- `HTTPException`

**Router가 하지 않는 일:** DB 쿼리, 임베딩 계산, Claude API 호출.

### 9.1 라우팅 표

| Method | Endpoint | 호출 Interactor.메서드 |
|---|---|---|
| POST | `/shylock-trial/trials` | `TrialProgressionInteractor.start()` |
| GET | `/shylock-trial/trials/{trial_id}` | (단순 조회, Port 직접 호출 가능) |
| POST | `/shylock-trial/trials/{trial_id}/choices` | `TrialProgressionInteractor.submit_choice()` |
| POST | `/shylock-trial/trials/{trial_id}/advance` | `TrialProgressionInteractor.advance_scene()` |
| GET | `/shylock-trial/trials/{trial_id}/ending` | `TrialProgressionInteractor.generate_ending()` |
| GET | `/shylock-trial/evidence` | (단순 조회 — 큐레이션된 6개 `Evidence`만 반환) |
| GET | `/shylock-trial/evidence/{evidence_id}` | (단순 조회 — 위와 동일 범위) |
| GET | `/shylock-trial/evidence/{evidence_id}/related` | `EvidenceSearchInteractor.search()` — 해당 Evidence와 의미적으로 유사한 주변 `PlayLine` 목록 반환 |

**`/evidence`와 `/evidence/{id}/related`의 범위 차이**: 전자는
게임 프론트엔드가 항상 보여주는 6개 고정 증거만 다룬다. 후자는 그
증거 하나를 기준점 삼아 전체 `PlayLine` 코퍼스에서 추가로 참고할
만한 주변 대사를 검색하는, 선택적 보강 기능이다. 현재 데모
(`shylock-trial.jsx`)에는 이 보강 검색을 호출하는 UI가 없으므로,
프론트엔드에서 실제로 쓰일지는 별도 확인이 필요한 **선택적
엔드포인트**다 — 반드시 1차 구현 범위에 포함해야 하는 것은 아니다.

### 9.2 `router_registry.py`

`structure.md` §3.1, §7을 따라 앱 단일 라우터에 하위 라우터를
등록한다.

```python
# apps/shylock_trial/adapter/inbound/api/router_registry.py (개념)
from .v1.trial_progression_router import trial_progression_router
from .v1.evidence_search_router import evidence_search_router

shylock_trial_router = APIRouter(prefix="/shylock-trial")
shylock_trial_router.include_router(trial_progression_router)
shylock_trial_router.include_router(evidence_search_router)
```

```python
# main.py (개념) — router 등록만, 도메인별 수정 최소화
from shylock_trial.adapter.inbound.api.router_registry import shylock_trial_router
app.include_router(shylock_trial_router)
```

### 9.3 ⚠️ 경로 불일치 — 작업 전 반드시 확인할 것

`game-technical-spec.md` §1.2는 향후 확장 구조로 Next.js API 라우트
(`app/api/game/portia-response/route.js`, `app/api/game/ending/route.js`)를
가정하고 있다. 반면 본 문서(9.1절)는 독립 FastAPI 서버를 가정한다.
**이 둘은 서로 다른 두 가지 아키텍처 선택지이며, 동시에 채택할 수 없다.**

- Next.js API 라우트 방식 → 프론트(Next.js)와 백엔드(API 라우트)가
  같은 배포 단위. 간단하지만 Titanic의 Hexagonal + Vertical Slice
  구조를 Next.js 라우트 핸들러 안에 욱여넣어야 해서 본 문서 4~8장의
  레이어 분리가 다소 어색해짐.
- 독립 FastAPI 서버 방식(본 문서 전제) → 프론트와 백엔드가 별도
  배포 단위. 본 문서의 구조를 그대로 살릴 수 있으나, 프론트 쪽
  `fetch` 호출 경로를 `/api/game/...`가 아니라 `/shylock-trial/...`로
  맞춰 재작성해야 함.

**Claude Code는 작업 착수 전 사용자에게 둘 중 어느 쪽을 원하는지
먼저 확인할 것.**

### 9.4 의존성 주입

`structure.md` §3.7("유일한 `Depends` 허용 위치 — Router + provider")을
그대로 따른다.

```python
# dependencies/trial_progression_provider.py (개념)
def get_trial_progression_use_case(
    port: TrialProgressionPort = Depends(get_trial_progression_repository),
    portia: PortiaResponseUseCase = Depends(get_portia_response_use_case),
    evidence: EvidenceSearchUseCase = Depends(get_evidence_search_use_case),
) -> TrialProgressionUseCase:
    return TrialProgressionInteractor(port=port, portia=portia, evidence=evidence)
```

---

## 10. 기술 스택 요약

| 영역 | 기술 |
|---|---|
| 웹 프레임워크 | FastAPI (async) |
| 아키텍처 표준 | Hexagonal + DDD + Vertical Slice (`structure.md` 준수) |
| 도메인 모델링 | Python dataclass / Pydantic (Value Object 불변성 보장) |
| LLM | Anthropic Claude API (`claude-sonnet-4-6`), tool_use 패턴 |
| 영구 저장소 | PostgreSQL + pgvector extension |
| ORM | SQLAlchemy 2.0 (async) + Alembic 마이그레이션 |
| 세션/캐시 | Redis |
| 임베딩 | Cohere `embed-v4.0` |
| 의존성 주입 | FastAPI `Depends()`, `dependencies/{stem}_provider.py` 단위 분리 |
| 테스트 | pytest, `domain`은 외부 의존 없이 순수 단위 테스트 |
| 마이그레이션 | Alembic |

---

## 11. Claude Code 구현 시 권장 순서

`structure.md` §8("첫 슬라이스 1개만 end-to-end로 만든다")을 따라,
가장 핵심적인 슬라이스(`trial_progression`)부터 수직으로 완성한 뒤
나머지를 확장한다.

1. `domain/entities`, `domain/value_objects` 구현 (외부 의존 없는
   순수 로직이라 가장 빠르게 테스트 가능)
2. `app/ports/input/trial_progression_use_case.py`,
   `app/ports/output/trial_progression_port.py` 인터페이스 정의
   (구현체 없이 ABC만)
3. `app/ports/input/portia_response_use_case.py`,
   `app/ports/output/portia_response_port.py` 정의
4. `adapter/outbound/client/portia_response_client.py` — Port
   구현체 작성, 단위 테스트는 Mock으로 먼저 통과시킴
5. `app/use_cases/trial_progression_interactor.py` — `start`,
   `submit_choice` 두 메서드부터 먼저 조립해 전체 흐름 검증
   (`advance_scene`, `generate_ending`은 흐름이 단순하므로 후순위 가능)
6. `adapter/inbound/api/v1/trial_progression_router.py`,
   `router_registry.py` — 얇은 라우터 작성, Interactor 연결
7. `adapter/outbound/pg/trial_progression_repository.py`,
   `orm/trial_orm.py`, `mappers/trial_progression_mapper.py` — 이
   시점부터 실제 DB 연동 테스트
8. `adapter/outbound/seeding/evidence_search_corpus_seeder.py` —
   Folger API에서 원문 전체를 가져와 `PlayLine`으로 적재(8장).
   **이 단계는 9번(pgvector 검색)보다 반드시 먼저 끝나야 한다** —
   검색 기능을 구현해도 적재된 데이터가 없으면 검증 자체가
   불가능하다. 시딩 완료 후 결과 행 수·act/scene 분포를 육안으로
   한 번 확인할 것(8장 "API 호출 vs 직접 파싱" 참조)
9. `app/use_cases/evidence_search_interactor.py`,
   `adapter/outbound/pg/evidence_search_repository.py` — 8번에서
   적재된 `PlayLine` 데이터를 대상으로 실제 유사도 검색이 동작하는지
   검증
10. `dependencies/*_provider.py` 3개 — DI 조립 마무리, 5번에서
    가짜로 연결했던 부분을 실제 Provider로 교체

이 순서는 "도메인 로직을 먼저 확정하고 외부 기술은 나중에 갈아끼운다"는
Hexagonal 아키텍처의 핵심 이점을 실제 구현 과정에서도 누리기 위함이다.
시딩(8번)을 검색 구현(9번) 뒤로 미루면, 검색 로직은 다 짜놓고도
"빈 테이블에 대고 쿼리하는" 상태로 한동안 머무르게 되므로 순서를
바꾸지 말 것.

---

## 12. `structure.md` 자가 점검 체크리스트 적용 결과

`structure.md` §11의 체크리스트를 본 명세서 기준으로 미리 확인한다.
Claude Code는 실제 구현 후 다시 한번 이 체크리스트로 검증할 것.

- [x] stem이 router ~ provider까지 동일한가 — `trial_progression`,
  `portia_response`, `evidence_search` 3개 stem이 9장(router)부터
  9.4절(provider)까지 일관되게 사용됨
- [x] `Depends`는 `dependencies/`와 router에만 있는가 — 9.4절에서
  명시
- [x] `domain/`에 FastAPI·SQLAlchemy import가 없는가 — 4장 전체가
  순수 Entity/VO로만 구성됨
- [ ] Schema에 OpenAPI example이 있는가 — 본 문서는 Schema 필드
  상세를 정의하지 않았으므로, 실제 구현 시 `model_config =
  ConfigDict(json_schema_extra={"examples": [...]})`를 빠뜨리지
  않도록 Claude Code가 직접 채울 것
- [x] Outbound가 Port 인터페이스를 구현하는가 — 7장 전체가
  `app/ports/output/`의 ABC를 구현하는 구조로 명시됨
- [x] `main.py`는 router 등록만 추가했는가 — 9.2절에서 명시
- [ ] ML 피처는 척도를 문서화했는가 — 본 게임은 ML 피처가 없으므로
  해당 없음(Titanic 전용 항목)

---

## 13. 관련 문서 — 작업 범위 분담

| 문서 | 다루는 범위 | 본 문서와의 관계 |
|---|---|---|
| `structure.md` | Titanic 아키텍처 표준(레이어 명칭, 슬라이스 패턴, 안티패턴) | 본 문서가 따르는 1차 표준. 충돌 시 `structure.md`가 우선 |
| `game-design-document.md` | 기획 의도, 내러티브, 포트폴리오 포지셔닝 | 배경지식. 백엔드 작업과 직접 관련 없음 |
| `illustration-prompts.md` | 일러스트 생성 프롬프트 | 백엔드 작업과 무관 |
| `game-technical-spec.md` | 현재 프론트엔드(`shylock-trial.jsx`)의 데이터 구조, 상태 관리, 화면 흐름, 그리고 §4.1의 **인증 문제 최초 지적** | 본 문서가 풀어야 할 문제(§1.1, 7.1절)의 출처. 프론트 마이그레이션 시 함께 참조 |
| `claude-code-spec.md` | SVG → PNG 일러스트 통합 작업 절차 | 백엔드와 독립적인 별개 작업. 순서 의존성 없음 |
| 본 문서 | 백엔드 아키텍처(Titanic 표준 준수), 도메인 모델, 슬라이스 구성, 인프라 Adapter, API 레이어 | 백엔드 신규 구축의 1차 레퍼런스 |

**작업 착수 전 필수 확인 사항 (Claude Code용 체크리스트):**

- [ ] 9.3절에서 경고한 API 라우팅 방식(Next.js API 라우트 vs 독립
  FastAPI 서버)을 사용자에게 먼저 확인했는가 — 확인 없이 진행 금지
- [ ] `shylock-trial.jsx`의 기존 `callClaude`, `getPortiaResponse`,
  `getEnding` 함수를 프론트가 새 백엔드 엔드포인트를 호출하는
  방식으로 교체해야 한다는 점을 인지했는가 — 본 문서 범위 밖이지만
  필연적 후속 작업이므로 별도 작업으로 분리해 안내할 것
- [ ] 일러스트 통합(`claude-code-spec.md`)과 백엔드 구축(본 문서)은
  서로 다른 파일을 건드리므로 순서 무관하게 병행 가능하나, 같은
  세션에서 두 작업을 동시에 지시받았다면 먼저 사용자에게 어느
  작업부터 진행할지 확인할 것
- [ ] Folger Digital Texts API가 시딩 시점에 실제로 응답 가능한
  상태인지 사전 확인했는가 — 외부 API 의존이므로 시딩 스크립트에는
  반드시 실패 시 명확한 에러 메시지를 남기도록 할 것(8장)
- [ ] 6개 `Evidence`의 `source_ftln_range` 수동 매핑(8장)은 자동화
  대상이 아니라는 점을 인지했는가 — 매핑값 자체는 사용자(기획자)에게
  확인받을 것
- [ ] 1.4절에서 4개 오케스트레이터를 1개 Interactor로 통합한 결정의
  근거(Rose 패턴)를 이해했는가 — 만약 추후 `submit_choice`처럼 특정
  메서드만 별도 슬라이스로 분리해야 할 필요가 생기면, `structure.md`
  §6.4(Smith 오케스트레이터 Provider)처럼 별도 stem으로 승격시키는
  것이 표준 확장 경로다
