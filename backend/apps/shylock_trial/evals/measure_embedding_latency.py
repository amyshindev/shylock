"""로컬 e5 임베딩 vs Cohere embed-v4.0 단일 쿼리 지연 측정.

Run from backend/ (Cohere 쪽은 프로덕션 어댑터 EvidenceEmbeddingClient를 그대로 재사용하므로
PYTHONPATH=apps:. 필요 — measure_local_embedding_resources.py와 동일한 패턴):
    python -m shylock_trial.evals.measure_embedding_latency                # 로컬만
    python -m shylock_trial.evals.measure_embedding_latency --with-cohere  # Cohere도 함께 비교
    python -m shylock_trial.evals.measure_embedding_latency --repeats 30

필요한 패키지:
    pip install sentence-transformers

Cohere 비교 시 backend/.env(또는 <repo>/.env)에 COHERE_API_KEY 필요 — infrastructure.config를
통해 읽으므로 셸 환경변수로 직접 export할 필요는 없음.
"""

import argparse
import statistics
import time

# 실제 게임에서 나올 법한 쿼리들 (한국어 → 영어 원문 교차 검색)
TEST_QUERIES = [
    "안토니오가 샤일록에게 침을 뱉고 개라고 불렀다",
    "리아가 준 터콰이즈 반지를 제시카가 팔았다",
    "베네치아 헌장과 법령의 효력",
    "유대인도 눈과 손과 감정이 있다",
    "계약서에 피에 대한 언급이 없다",
    "이방인 법에 따라 재산이 몰수된다",
    "바사니오가 원금의 열 배를 제안했다",
    "자비는 강요될 수 없다",
]

LOCAL_MODEL = "intfloat/multilingual-e5-large-instruct"

# e5-instruct 관례: 쿼리에만 instruction 프리픽스
INSTRUCTION = (
    "Given a Korean query about Shakespeare's The Merchant of Venice, "
    "retrieve relevant passages from the play"
)


def fmt_stats(name: str, samples_ms: list[float]) -> str:
    ordered = sorted(samples_ms)
    p95 = ordered[min(int(len(ordered) * 0.95), len(ordered) - 1)]
    return (
        f"{name:<28} "
        f"mean={statistics.mean(samples_ms):8.1f}ms  "
        f"median={statistics.median(samples_ms):8.1f}ms  "
        f"p95={p95:8.1f}ms  "
        f"min={min(samples_ms):8.1f}ms  "
        f"max={max(samples_ms):8.1f}ms  "
        f"(n={len(samples_ms)})"
    )


def measure_local(repeats: int) -> None:
    from sentence_transformers import SentenceTransformer

    print("=" * 100)
    print("1. 로컬 e5 임베딩")
    print("=" * 100)

    t0 = time.perf_counter()
    model = SentenceTransformer(LOCAL_MODEL)
    load_ms = (time.perf_counter() - t0) * 1000
    print(f"모델 로드: {load_ms:,.0f}ms  ({LOCAL_MODEL})")
    print("  (최초 실행이면 ~1.1GB 다운로드 포함 — 재실행하면 순수 로드 시간 확인 가능)")

    device = getattr(model, "device", "unknown")
    print(f"device: {device}")

    # 콜드 스타트 (lazy init 포함)
    cold_query = f"Instruct: {INSTRUCTION}\nQuery: {TEST_QUERIES[0]}"
    t0 = time.perf_counter()
    model.encode(cold_query)
    cold_ms = (time.perf_counter() - t0) * 1000
    print(f"first call (cold): {cold_ms:,.1f}ms")

    # 워밍업
    for _ in range(3):
        model.encode(cold_query)

    # 실측 — 쿼리를 돌려가며 캐시 효과 배제
    samples: list[float] = []
    for i in range(repeats):
        query = TEST_QUERIES[i % len(TEST_QUERIES)]
        prompted = f"Instruct: {INSTRUCTION}\nQuery: {query}"
        t0 = time.perf_counter()
        model.encode(prompted)
        samples.append((time.perf_counter() - t0) * 1000)

    print(fmt_stats("local (warm)", samples))

    # 차원 확인 — 마이그레이션 시 pgvector 컬럼 차원과 맞춰야 함
    vec = model.encode(f"Instruct: {INSTRUCTION}\nQuery: {TEST_QUERIES[0]}")
    print(f"임베딩 차원: {len(vec)}")

    # 배치 처리량 — 전체 코퍼스 재임베딩 시간 추정용
    print()
    print("-" * 100)
    print("배치 처리량 (전체 코퍼스 재임베딩 추정)")
    print("-" * 100)
    batch = [f"passage: {q}" for q in TEST_QUERIES] * 8  # 64개
    t0 = time.perf_counter()
    model.encode(batch, batch_size=32)
    batch_ms = (time.perf_counter() - t0) * 1000
    per_item = batch_ms / len(batch)
    print(f"{len(batch)}개 배치: {batch_ms:,.0f}ms  ({per_item:.1f}ms/item)")
    for label, count in (("play_chunks", 630), ("play_lines", 2623)):
        print(f"  → {label} {count}개 추정: {per_item * count / 1000:,.1f}초")


def measure_cohere(repeats: int) -> None:
    # 프로덕션에서 실제로 쓰는 어댑터를 그대로 재사용 — API 키(COHERE_API_KEY)와 모델 이름
    # (cohere_embed_model)을 이 스크립트가 따로 하드코딩/재구현하지 않고 infrastructure.config
    # 를 통해 읽으므로, 이 프로젝트의 실제 프로덕션 경로와 같은 조건으로 측정된다.
    from infrastructure.asyncio_compat import run_async
    from infrastructure.config import get_settings
    from shylock_trial.adapter.outbound.client.evidence_embedding_client import (
        EvidenceEmbeddingClient,
    )

    try:
        settings = get_settings()
        if not settings.cohere_api_key.get_secret_value():
            print("\nCOHERE_API_KEY가 없어 Cohere 측정을 건너뜁니다.")
            return
    except Exception as exc:  # noqa: BLE001 — .env 미설정 등 구성 오류
        print(f"\nCOHERE_API_KEY 설정을 읽지 못해 Cohere 측정을 건너뜁니다: {exc}")
        return

    print()
    print("=" * 100)
    print(f"2. Cohere {settings.cohere_embed_model} (실제 API 호출, 프로덕션 어댑터 재사용)")
    print("=" * 100)

    # 워밍업 + 실측을 전부 하나의 asyncio.run() 안에서 돈다 — EvidenceEmbeddingClient가 내부에
    # 들고 있는 cohere.AsyncClientV2는 최초 사용 시점의 이벤트 루프에 묶이므로, run_async()를
    # 두 번 나눠 부르면(=루프를 두 번 새로 만들면) 두 번째 호출에서 "Event loop is closed"로 죽는다.
    async def _run() -> list[float] | None:
        client = EvidenceEmbeddingClient()

        try:
            await client.embed_query(TEST_QUERIES[0])  # 워밍업 (연결 수립)
        except Exception as exc:  # noqa: BLE001
            print(f"Cohere 호출 실패: {exc}")
            return None

        out: list[float] = []
        for i in range(repeats):
            query = TEST_QUERIES[i % len(TEST_QUERIES)]
            t0 = time.perf_counter()
            try:
                await client.embed_query(query)
            except Exception as exc:  # noqa: BLE001
                print(f"  호출 실패 ({i + 1}회차): {exc}")
                continue
            out.append((time.perf_counter() - t0) * 1000)
        return out

    samples = run_async(_run())
    if samples:
        print(fmt_stats("Cohere API", samples))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repeats", type=int, default=20)
    parser.add_argument("--with-cohere", action="store_true")
    args = parser.parse_args()

    import platform

    print(f"Host: {platform.platform()} / {platform.machine()}")
    print()

    measure_local(args.repeats)
    if args.with_cohere:
        measure_cohere(args.repeats)

    print()
    print("=" * 100)
    print("판단 기준")
    print("=" * 100)
    print("- 단일 쿼리 지연이 Cohere(약 345ms, EC2 기준)보다 빠르면 전환 이득")
    print("- 100ms 이하면 체감 지연 없음")
    print("- p95가 크게 튀면 안정성 문제 — 반복 측정 필요")
    print("- 임베딩 차원이 1536(Cohere)과 다르면 alembic 마이그레이션 필요")


if __name__ == "__main__":
    main()
