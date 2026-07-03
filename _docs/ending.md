# 엔딩 분기

재판 결과는 **DP**(`dp`) 단일 게이지만으로 판정한다.  
법정 판결(이방인 법·재산 몰수·강제 개종)은 **모든 엔딩에서 동일**하며, 원작과 같이 샤일록은 재판에서 패한다. DP는 “법정이 그의 정신·존엄을 얼마나 꺾었는가”를 나타낸다.

---

## 게이지 정의

| 게이지 | 초기값 | 최대 | 의미 |
|--------|--------|------|------|
| **dp** | 50 | 100 | 도덕적·설득적 위상. 높을수록 논리·인간성을 지키며 끝까지 버텼다 |

- 선택지, 증거 제출, 스킬 사용 등으로 `dp_delta`가 적용된다.
- 값은 0~100으로 클램프된다.

---

## 임계값

| 상수 | 값 | 용도 |
|------|-----|------|
| `DP_FOUGHT_TO_END_THRESHOLD` | **80** | “끝까지 싸운 자” |
| `DP_DIGNITY_ENDING_THRESHOLD` | **60** | “존엄을 지킨 자” |
| `DP_SURVIVAL_ENDING_THRESHOLD` | **40** | “살아남은 자” |

판정 로직 (`backend/.../ending_type_map.py` → `resolve_ending_type`):

```python
if dp >= 80: fought_to_end_ending
elif dp >= 60: dignity_kept_ending
elif dp >= 40: survived_ending
else: silent_ending
```

프론트 표시용 미러: `frontend/lib/constants/ending-thresholds.ts`  
**서버 판정이 최종 권위**이며, 프론트는 UI 라벨·부제·이모지만 맞춘다.

---

## 4가지 엔딩 (DP 단독)

| DP | `ending_type` | UI 제목 | 부제 |
|:--:|----------------|---------|------|
| ≥ 80 | `fought_to_end_ending` | 끝까지 싸운 자 | 법정은 그를 무너뜨리지 못했다 |
| 60–79 | `dignity_kept_ending` | 존엄을 지킨 자 | 그는 흔들렸지만 꺾이지 않았다 |
| 40–59 | `survived_ending` | 살아남은 자 | 살아남았다. 그것으로 충분한가? |
| < 40 | `silent_ending` | 침묵한 자 | 그는 결국 법정이 원하는 대로 무너졌다 |

### 경계값 예시 (테스트 기준)

| dp | 결과 |
|----|------|
| 80 | `fought_to_end_ending` |
| 79 | `dignity_kept_ending` |
| 60 | `dignity_kept_ending` |
| 59 | `survived_ending` |
| 40 | `survived_ending` |
| 39 | `silent_ending` |

---

## `alien_law_reveal` 씬

마지막 씬(인덱스 7, `alien_law_reveal`)은 **유지**한다.  
이 씬의 선택(`reject_conversion`, `bow_accept`, `mock_mercy` 등)은 **DP에만** 영향을 주며, 엔딩 분기나 법정 판결 결과를 바꾸지 않는다.

---

## 게임 오버 vs 정상 엔딩

재판 **중간**에 `dp <= 0`이 되면 **엔딩 분기 없이** 게임 오버 화면으로 종료한다.

| 조건 | `GameOverReason` | UI |
|------|------------------|-----|
| `dp <= 0` | `dp` | 스스로 포기하다 |

정상 플레이는 마지막 씬을 마친 뒤 `GET/POST .../ending` → `generate_ending`이 호출되고, 위 4분기 + AI 나레이션이 표시된다.

---

## 엔딩 생성 흐름

```
마지막 씬 대사·선택 완료
    → finishToEnding() (프론트)
    → generate_ending(trial_id) (백엔드)
        1. ending_type = resolve_ending_type(dp)
        2. Portia LLM에 ending_type·dp·선택 이력 전달
           (법정 판결은 모든 엔딩 동일 — 원작대로 샤일록 패소)
        3. trial.phase = ENDED, narration_text = LLM 결과 저장
    → EndingScreen (제목·부제·DP·나레이션)
```

---

## 관련 소스

| 역할 | 경로 |
|------|------|
| 판정 로직 | `backend/apps/shylock_trial/app/constants/ending_type_map.py` |
| 임계값 상수 | `backend/.../game_balance.py`, `frontend/lib/constants/game-balance.ts` |
| 엔딩 생성 | `backend/.../use_cases/trial_progression_interactor.py` → `generate_ending` |
| 선택지 Δ | `backend/.../scene_choices.py` (`CHOICE_EFFECTS`) |
| UI 메타 | `frontend/lib/constants/ending-thresholds.ts` |
| 엔딩 화면 | `frontend/components/ending/EndingScreen.tsx` |
| LLM 프롬프트 | `backend/.../portia_prompt.py` (`request_type=ending`) |
| 테스트 | `backend/.../tests/domain/test_ending_and_scores.py` |

---

## 설계 메모

- **역사를 바꾼 엔딩**(`history_changed_ending`)은 폐지했다. 원작 맥락상 샤일록이 법정에서 이기는 결말은 없다.
- **DP 80↑** (`fought_to_end_ending`)은 법정 판결은 동일하지만, 정신·존엄을 끝까지 지킨 **도덕적 승리**로 읽히도록 엔딩 나레이션을 작성한다.
- **`alien_law_executed` 필드**는 Trial 엔티티·DB·API에서 완전히 제거했다. 이방인 법 판결은 모든 엔딩의 공통 배경이다.
- 스킬(론슬롯·베니스의 모순 등)은 DP를 바꿔 `ending_type`에 영향을 줄 수 있다.
