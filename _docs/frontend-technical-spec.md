# 샤일록의 법정 — 프론트엔드 기술명세서

> Claude Code 구현 레퍼런스용
> Next.js · 일러스트 통합 · Hexagonal 철학의 클라이언트 적용
> 작성일: 2026-06-30

---

## 0. 본 문서가 대체하는 것

본 문서는 과거의 두 명세서를 흡수하고 폐기한다.

| 폐기 문서 | 흡수된 내용 | 폐기 사유 |
|---|---|---|
| `claude-code-spec.md` | SVG → PNG 교체 대상 컴포넌트 목록(§3), 장면별 일러스트 매핑 표 | 단일 파일 Artifact(`shylock-trial.jsx`) 전제로 작성됨. 본 작업은 그 Artifact를 그대로 옮기는 게 아니라 Next.js로 **신규 구축**이므로, "기존 코드의 어디를 고칠지"가 아니라 "새 코드를 어떻게 짤지"가 필요함 |
| `game-technical-spec.md` | §2(데이터 구조: `EVIDENCE`, `SCENES`), §4(AI 연동 함수 시그니처) | 데이터 구조 자체는 여전히 유효하므로 4장에 그대로 가져오되, §1.2(Next.js 마이그레이션 구조 제안)·§7(이식 체크리스트)은 본 문서가 실제로 구현하므로 폐기 |

`shylock-trial.jsx`는 더 이상 "수정 대상"이 아니라 **참조용 프로토타입**이다 — 게임 로직(미터 계산, 장면 전환, AI 호출 흐름)이 검증된 코드이므로 그 로직을 Next.js 구조로 옮겨 짜되, 단일 파일이라는 제약과 SVG 플레이스홀더는 버린다.

---

## 1. 개요

### 1.1 목적
일러스트 11종(장면 6 + 증거 아이콘 5)이 모두 확보된 상태에서, `backend-technical-spec.md`가 정의한 Titanic 표준 백엔드(`apps/shylock_trial/`)를 호출하는 Next.js 프론트엔드를 신규 구축한다.

### 1.2 일러스트 자산 — 확보 완료 목록

`_docs/`에 정리됨. 게임 장면 6장 + 증거 아이콘 5장.

| # | 파일명 | 장면 ID(`scene.id`) | 원본 업로드명 | 비고 |
|---|---|---|---|---|
| 1 | `scene-opening.png` | `opening` | `opening.png` | 인물 없는 법정 풀샷 |
| 2 | `scene-portia-opens.png` | `portia_opens` | `debating.png` | 샤일록↔포샤 대각선 분할 |
| 3 | `scene-crowd-jeers.png` | `crowd_jeers` | `shylockstanding.png` | 샤일록 단독 정면, 무게감 있는 자세 |
| 4 | `scene-jessica-attack.png` | `jessica_attack` | `portia.png` | 포샤 단독 클로즈업, 손가락질 |
| 5 | `scene-hath-not.png` | `hath_not_moment` | `shylockcrying.png` | 샤일록 클로즈업, 분노+눈물 동시 표현 |
| 6 | `scene-blood-reveal.png` | `blood_reveal` | `ending.png` | 군중 앞 변론 장면(최종 판결) |

| # | 파일명 | `EVIDENCE` 키 | 비고 |
|---|---|---|---|
| 7 | `evidence-gaberdine.png` | `gaberdine` | 낡은 외투 아이콘 |
| 8 | `evidence-bond.png` | `bond` | "a pound of flesh" 계약서 |
| 9 | `evidence-jessica.png` | `jessica` | 찢어진 편지(밀랍 인장) |
| 10 | `evidence-mercy.png` | `mercy` | 법봉+깃펜 |
| 11 | `evidence-blood.png` | `blood` | 피 묻은 검 |

**⚠️ `hath_not` 증거에 대응하는 아이콘 없음.** `EVIDENCE` 객체(4.1절)는 6개 키(`gaberdine`, `bond`, `hath_not`, `jessica`, `mercy`, `blood`)를 가지나, 원본 `icons.png` 시트는 5개 아이콘만 담고 있었다(6칸 그리드 중 1칸은 빈 공간). `hath_not`("유대인의 증언" — "Hath not a Jew eyes?" 독백)은 게임의 감정적 클라이맥스이자 5번 장면(`scene-hath-not.png`) 자체가 이 증거를 시각적으로 대표하므로, 별도 원형 아이콘이 굳이 필요하지 않을 수 있다. 다만 증거 목록 UI(7.3절)에서 다른 5개와 동일한 형식으로 보여야 한다면 아이콘이 비게 되므로, **Claude Code는 구현 전 사용자에게 다음 중 하나를 확인할 것**:
- (a) `hath_not`만 텍스트/이모지 폴백 아이콘으로 대체
- (b) 추가 아이콘 생성을 요청하고 작업을 일시 보류
- (c) `hath_not`은 증거 목록 UI에서 제외하고 클라이맥스 모달로만 노출(현재 `shylock-trial.jsx`의 `climaxMode`와 동일한 처리)

### 1.3 디자인 원칙 — Titanic 철학의 프론트엔드 적용

`backend-technical-spec.md` §1.2가 채택한 Hexagonal 원칙(관심사 분리, 외부 의존의 명시적 경계)을 프론트엔드에 그대로 적용하되, Next.js 생태계의 관용적 패턴으로 표현한다. 즉 `app/ports/output/`처럼 ABC를 만들진 않지만, **"백엔드 API 호출 로직"과 "화면 렌더링 로직"과 "게임 진행 상태"를 같은 파일에 섞지 않는다**는 동일한 정신을 따른다.

| 책임 | Next.js 표현 | Titanic 백엔드의 대응 개념 |
|---|---|---|
| 화면 표시 | `components/` | `adapter/inbound`(보여주는 쪽) |
| 게임 진행 상태 관리 | `hooks/use-trial-progression.ts` | `app/use_cases/trial_progression_interactor.py` — 같은 책임 경계를 클라이언트 쪽에 미러링 |
| 백엔드 API 호출 | `lib/api-client/` | 백엔드의 `adapter/outbound/client/`를 호출하는 쪽 |
| 정적 게임 데이터 | `data/` | `domain/entities`의 일부(`Evidence`, `Scene`)를 프론트에서도 참조해야 하므로 미러링 |

---

## 2. 기술 스택

| 영역 | 기술 | 비고 |
|---|---|---|
| 프레임워크 | Next.js (App Router) | `game-technical-spec.md` §1.2가 이미 이 방향을 전제했음 |
| 언어 | TypeScript | 기존 `shylock-trial.jsx`는 순수 JS였으나, 백엔드가 Pydantic으로 타입을 명시하는 만큼 프론트도 타입을 맞추는 것을 권장 |
| 스타일링 | 인라인 style 객체 유지 또는 CSS Modules로 이관 | `shylock-trial.jsx`의 다크 테마 색상값(아래 4.4절)을 그대로 재사용 |
| 상태 관리 | React 기본 훅(`useState`, `useEffect`, `useRef`) | 게임 상태가 복잡하지 않으므로 별도 상태관리 라이브러리 불필요 — `shylock-trial.jsx`에서 이미 검증됨 |
| API 통신 | `fetch` 기반 경량 클라이언트(`lib/api-client/`) | 9장 참조 |
| 이미지 최적화 | Next.js `<Image>` 컴포넌트 | 11장 일러스트가 모두 고해상도(2400px 이상)이므로 최적화 필수 |

---

## 3. 디렉토리 구조

```text
frontend/
├── app/
│   ├── page.tsx                       # 타이틀 화면 진입점
│   ├── trial/
│   │   └── [trialId]/
│   │       └── page.tsx               # 게임 진행 화면(동적 라우트)
│   └── layout.tsx
│
├── components/
│   ├── title/
│   │   └── TitleScreen.tsx
│   ├── battle/
│   │   ├── BattleScreen.tsx           # 메인 게임 화면 컨테이너
│   │   ├── DialogueBox.tsx            # 화자 탭 + 타이핑 애니메이션
│   │   ├── ChoiceList.tsx             # 선택지 영역
│   │   ├── ObjectionBanner.tsx        # "이의 있습니다!" 연출
│   │   ├── ClimaxOverlay.tsx          # hath_not 클라이맥스 전체화면 모달
│   │   ├── EvidenceModal.tsx          # 증거 확대 표시
│   │   ├── EvidenceList.tsx           # 하단 증거 목록 바
│   │   └── MeterDisplay.tsx           # 존엄/확신도 게이지
│   └── ending/
│       └── EndingScreen.tsx
│
├── hooks/
│   ├── use-trial-progression.ts       # 게임 진행 상태 전체(구 useState 더미들의 통합 관리)
│   └── use-typing-effect.ts           # 타이핑 애니메이션 로직 분리(구 typeRef 로직)
│
├── lib/
│   ├── api-client/
│   │   ├── trial-progression.ts       # /trials/* 엔드포인트 호출
│   │   └── evidence-search.ts         # /evidence/* 엔드포인트 호출
│   └── constants/
│       └── ending-thresholds.ts       # victory/standard_defeat/silent_defeat 임계값(백엔드 ending_type_map.py와 동일 값 유지 — 9.4절 참조)
│
├── data/
│   ├── evidence.ts                    # 6개 Evidence 메타데이터(이름, 설명, 출처) — quote 원문은 백엔드가 권위 소스(9.4절)
│   └── scenes.ts                      # 6개 Scene의 대사·선택지·이미지 경로 매핑
│
├── public/
│   └── assets/                        # 11장 일러스트(1.2절) 그대로 배치
│       ├── scene-opening.png
│       ├── scene-portia-opens.png
│       ├── scene-crowd-jeers.png
│       ├── scene-jessica-attack.png
│       ├── scene-hath-not.png
│       ├── scene-blood-reveal.png
│       ├── evidence-gaberdine.png
│       ├── evidence-bond.png
│       ├── evidence-jessica.png
│       ├── evidence-mercy.png
│       └── evidence-blood.png
│
└── styles/
    └── theme.ts                       # 4.4절 색상 상수
```

---

## 4. 데이터 구조 (`data/`)

`game-technical-spec.md` §2가 이미 정의한 구조를 그대로 가져오되, TypeScript 타입을 명시한다.

### 4.1 `data/evidence.ts`

```typescript
interface EvidenceMeta {
  id: string;          // EVIDENCE 키(예: "gaberdine")
  name: string;        // 한국어 표시명
  icon: string;         // public/assets/evidence-{id}.png 경로
  desc: string;         // 한국어 설명(1문장)
  act: string;          // 출처(예: "Act I, Scene 3")
  // quote(영어 원문)는 포함하지 않음 — 9.4절 참조
}
```

**⚠️ `quote` 필드는 프론트엔드 데이터에 두지 않는다.** `shylock-trial.jsx`의 `EVIDENCE` 객체는 `quote`(영어 원문 인용)를 프론트 코드에 하드코딩했으나, `backend-technical-spec.md` 4.2절은 원문이 Folger Digital Texts에서 오는 `PlayLine`/`Evidence` 도메인 데이터이며 백엔드가 `source_ftln_range`까지 관리하는 권위 소스(source of truth)임을 명시한다. 프론트는 `/evidence` 엔드포인트(백엔드 9.1절 라우팅 표)를 호출해 `quote`를 받아오고, 클라이언트 코드에 원문을 중복 저장하지 않는다. 1.2절의 6개 아이콘 매핑(`id`, `icon`, 출처)만 정적 데이터로 두고, 실제 원문 텍스트는 항상 API 응답에서 가져온다.

### 4.2 `data/scenes.ts`

```typescript
interface Scene {
  id: string;
  speaker: "NARRATOR" | "PORTIA" | "CROWD";
  backgroundImage: string;   // public/assets/scene-{id}.png 경로(1.2절 매핑)
  lines: string[];
  challenge: {
    text: string;
    options: {
      id: string;
      text: string;
      evidence: string | null;   // EVIDENCE 키 참조
      dignityChange: number;
      confidenceChange: number;
      special?: "climax";
    }[];
  } | null;
  availableEvidence: string[];
}
```

`portrait` 필드(`game-technical-spec.md` §2.2가 "죽은 코드 가능성"으로 지적)는 본 신규 구현에서 처음부터 포함하지 않는다 — `speaker`와 중복 정보였고, 일러스트 통합 이후로는 `backgroundImage`가 장면의 시각 정보를 전담하므로 더더욱 불필요하다.

### 4.3 게임 진행 상태(`hooks/use-trial-progression.ts`)

`shylock-trial.jsx`(`game-technical-spec.md` §2.3)가 가졌던 17개 `useState`를 하나의 커스텀 훅으로 통합한다. 이 훅이 사실상 백엔드의 `TrialProgressionInteractor`(`backend-technical-spec.md` 5장)와 같은 책임 경계를 클라이언트 쪽에서 미러링한다.

| 기존 `shylock-trial.jsx`의 상태 | 본 구조에서의 위치 | 비고 |
|---|---|---|
| `phase`, `sceneIdx`, `lineIdx` | `use-trial-progression.ts` 내부 | 게임 진행 위치 |
| `dignity`, `confidence` | `use-trial-progression.ts` 내부 | 백엔드 응답으로 매 턴 갱신(서버가 권위 소스) |
| `portiaReply`, `loadingReply` | `use-trial-progression.ts` 내부 | AI 응답 결과 캐싱 |
| `displayedText`, `isTyping`, `typeRef` | `use-typing-effect.ts`로 분리 | 순수 UI 애니메이션 로직이라 게임 상태 훅과 분리 — 재사용성 위함 |
| `portraitMood`, `shylockMood` | **제거** | 일러스트가 장면별로 이미 고정 표정으로 통째 제공되므로(1.2절) 런타임 표정 전환이 불필요. `claude-code-spec.md` §4.2가 이미 같은 결론을 냈었고 본 구조도 이를 유지함 |

### 4.4 색상 테마(`styles/theme.ts`)

`shylock-trial.jsx`에서 검증된 다크 테마 팔레트를 그대로 가져온다.

```typescript
export const theme = {
  background: "#08030a",
  panelBackground: "#0d0510",
  border: "#3a1a28",
  gold: "#ffd700",
  red: "#8b0000",
  textMuted: "#5a4a3a",
  textBright: "#c8a080",
};
```

---

## 5. 화면 흐름

`game-technical-spec.md` §3의 상태 머신을 그대로 채택하되, 라우팅을 Next.js App Router에 맞게 표현한다.

```text
/ (TitleScreen)
  → POST /shylock-trial/trials 호출(백엔드 9.1절)
  → /trial/{trialId} 로 이동

/trial/{trialId} (BattleScreen)
  → 장면 진행, 선택지 처리(아래 흐름 참조)
  → 마지막 장면 통과 시 EndingScreen으로 전환(같은 라우트 내 phase 분기,
    URL 이동은 하지 않음 — shylock-trial.jsx의 기존 패턴 유지)
```

장면 내부 흐름은 `game-technical-spec.md` §3에 정의된 것과 동일하다(advance/nextScene 구분, makeChoice의 2200ms 연출 타이밍 등). 본 문서에서 재서술하지 않으며, Claude Code는 해당 문서 §3, §6.1, §6.2를 그대로 참조할 것.

---

## 6. 일러스트 적용 — 컴포넌트별 작업

`claude-code-spec.md`가 다루던 "SVG 제거 후 PNG로 교체"라는 작업 자체는 더 이상 의미가 없다(신규 구현이므로 애초에 SVG를 만들지 않는다). 대신 각 컴포넌트가 어떤 일러스트를 어떻게 배치해야 하는지를 명시한다.

### 6.1 `BattleScreen.tsx` — 장면 배경

```tsx
// 개념 코드
<div style={{
  backgroundImage: `url(${scene.backgroundImage})`,
  backgroundSize: "cover",
  backgroundPosition: "center",
}}>
  {/* DialogueBox, ChoiceList 등은 이 위에 오버레이 */}
</div>
```

장면(`scene.id`)별 이미지 매핑은 1.2절 표를 그대로 따른다.

### 6.2 `scene-hath-not.png`의 비율 예외

`shylockcrying.png` 원본은 가로형(2400×1350 추정 범위)으로 확인되었으나, `illustration-prompts.md`의 5번 프롬프트는 본래 3:4 세로 비율을 의도했었다. **실제 받은 일러스트의 정확한 비율은 구현 전 `file` 또는 이미지 메타데이터로 재확인할 것** — 만약 가로형으로 최종 확정되었다면, `claude-code-spec.md` §4.3이 가정했던 "3:4 세로 전용 레이아웃 분기"는 불필요해지므로, 다른 5개 장면과 동일한 `backgroundSize: cover` 처리로 통일 가능하다. 이 확인이 끝나기 전까지는 레이아웃 분기 코드를 임의로 추가하지 말 것.

### 6.3 `ClimaxOverlay.tsx`

`shylock-trial.jsx`의 `climaxMode` 상태로 트리거되는 전체화면 텍스트 모달은 일러스트와 무관하게 기존 로직을 그대로 유지한다("Hath not a Jew eyes?" 원문이 화면을 채우는 연출). `scene-hath-not.png`는 이 모달이 뜨기 직전의 배경 장면으로만 쓰이며, 모달 자체에는 이미지가 들어가지 않는다.

### 6.4 `EvidenceList.tsx` / `EvidenceModal.tsx`

증거 아이콘 5장(1.2절 7~11번)을 원형 그대로 사용한다. 추가 크롭이나 마스킹이 필요 없다 — `icons.png`에서 분리한 결과물이 이미 원형 프레임과 함께 완성된 형태다(2.2절 검증 완료).

```tsx
// 개념 코드
<img src={`/assets/evidence-${evidence.id}.png`} alt={evidence.name} />
```

`hath_not` 키에 대한 처리는 1.2절의 미해결 사항을 따른다.

---

## 7. 컴포넌트별 상세 — UI 요소 인벤토리

`game-technical-spec.md` §5의 컴포넌트 인벤토리를 Next.js 컴포넌트 분할 기준으로 재정리한다.

| 컴포넌트 | 책임 | `shylock-trial.jsx`에서의 대응 |
|---|---|---|
| `TitleScreen.tsx` | 타이틀 화면, 게임 시작 버튼 | `phase === "title"` 블록 |
| `BattleScreen.tsx` | 메인 게임 화면 컨테이너, 장면 배경 표시 | `phase === "game"` 블록의 최상위 구조 |
| `DialogueBox.tsx` | 화자 이름 탭 + 대사 타이핑 출력 | 하단 텍스트박스의 대사 영역 |
| `ChoiceList.tsx` | 선택지 버튼 목록 | `showChallenge` 조건부 렌더링 블록 |
| `ObjectionBanner.tsx` | "이의 있습니다!" 배너(900ms) | `objection` 상태 오버레이 |
| `ClimaxOverlay.tsx` | 클라이맥스 원문 모달 | `climaxMode` 오버레이 |
| `EvidenceModal.tsx` | 증거 확대 팝업(2200ms) | `evidenceModal` 오버레이 |
| `EvidenceList.tsx` | 하단 증거 아이콘 목록 바 | 텍스트박스 하단의 증거 목록 |
| `MeterDisplay.tsx` | 존엄/확신도 게이지 | 상단 미터 UI |
| `EndingScreen.tsx` | 최종 화면, AI 생성 엔딩 텍스트 | `phase === "ending"` 블록 |

각 컴포넌트의 내부 로직(타이밍 상수, 애니메이션 시퀀스)은 `game-technical-spec.md` §6.2(900/2200/2200ms 연출 타이밍 — 서로 맞물려 있으므로 하나만 바꾸면 안 됨)를 그대로 따른다.

---

## 8. 알려진 설계상 특이점 — 신규 구현 시 유의사항

`game-technical-spec.md` §6이 지적한 사항 중, Next.js 신규 구현에서도 여전히 유효한 것만 발췌한다.

### 8.1 `advance`와 `nextScene`은 역할이 다르다(§6.1 그대로 계승)
한 장면 내부에서 대사를 진행시키는 함수(`advance`, 본 구조에서는 `use-trial-progression.ts`의 메서드)와, 장면 자체를 전환하는 함수(`nextScene`)를 혼동하지 말 것. 두 책임을 한 함수에 합치지 않는다.

### 8.2 연출 타이밍 3종 세트(§6.2 그대로 계승)
증거 제출 시 900ms(배너)/2200ms(모달)/2200ms(다음 로직 진행)가 서로 맞물린 상수다. 리팩토링 시에도 이 셋을 따로따로 바꾸지 않는다.

### 8.3 더 이상 유효하지 않은 항목

`game-technical-spec.md` §6.3(죽은 코드: `scene.portrait`, `portraitMood`, `shylockMood`)과 §6.4(색상 하드코딩 문제)는 신규 구현에서는 애초에 발생하지 않는다 — 4.2절에서 `portrait` 필드를 처음부터 제외했고, 4.3절에서 mood 상태를 처음부터 만들지 않으며, 4.4절에서 색상을 `theme.ts`로 변수화했기 때문이다. Claude Code가 과거 이력에서 이 항목들을 "고쳐야 할 버그"로 다시 끄집어내지 않도록 명시해둔다.

---

## 9. 백엔드 연동(`lib/api-client/`)

### 9.1 호출 대상

`backend-technical-spec.md` 9.1절의 라우팅 표를 그대로 호출한다.

```typescript
// lib/api-client/trial-progression.ts (개념)
export async function startTrial(): Promise<TrialState> {
  const res = await fetch(`${API_BASE}/shylock-trial/trials`, { method: "POST" });
  return res.json();
}

export async function submitChoice(
  trialId: string,
  choiceId: string
): Promise<{ trial: TrialState; portiaReply: string; gameOver: boolean }> {
  const res = await fetch(
    `${API_BASE}/shylock-trial/trials/${trialId}/choices`,
    { method: "POST", body: JSON.stringify({ choice_id: choiceId }) }
  );
  return res.json();
}
```

### 9.2 ⚠️ 경로 미확정 — `backend-technical-spec.md` 9.3절과 동일한 경고

**본 문서는 백엔드 API 경로 방식을 미확정 상태로 둔다.** `backend-technical-spec.md` §9.3이 이미 경고했듯, Next.js API 라우트 방식(`/api/game/...`)과 독립 FastAPI 서버 방식(`/shylock-trial/...`)은 동시에 채택할 수 없는 두 갈래이며, 이 결정이 아직 내려지지 않았다(작업 착수 시점 확인 사항).

**Claude Code는 본 프론트엔드 작업 착수 전, 다음을 사용자에게 반드시 확인할 것:**
- 독립 FastAPI 서버 방식이라면 → `API_BASE`를 환경변수(`NEXT_PUBLIC_API_BASE_URL` 등)로 설정하고, `lib/api-client/`가 그 주소로 호출
- Next.js API 라우트 방식이라면 → 본 문서의 `app/` 디렉토리 구조(3장)에 `app/api/shylock-trial/...` 라우트 핸들러가 추가로 필요해지며, 이는 본 문서가 현재 다루지 않은 범위이므로 별도 보강이 필요함을 안내할 것

이 결정이 내려지기 전까지, `lib/api-client/`의 호출 경로는 가정값(`/shylock-trial/...`)으로 두되 하드코딩하지 말고 상수 하나로 분리해, 결정 후 한 곳만 고치면 되도록 만들 것.

### 9.3 인증 — 프론트는 Gemini API 키를 모른다

`backend-technical-spec.md` §1.1, 7.1절이 이미 해결한 문제를 프론트 쪽에서 재확인한다. **프론트엔드 코드 어디에도 `LLM_API_KEY`나 Gemini API 키가 등장하지 않는다.** `shylock-trial.jsx`의 기존 `callGemini` 함수(Gemini API를 클라이언트에서 직접 호출하던 패턴)는 본 신규 구현에서 완전히 제거되며, 그 자리를 9.1절의 백엔드 API 클라이언트가 대신한다. 과거 코드 패턴을 참조해 `fetch("https://generativelanguage.googleapis.com/...")` 같은 호출을 프론트에 작성하지 않도록 주의할 것 — 이는 명백한 퇴행이다.

### 9.4 증거 원문(quote)의 권위 소스

4.1절에서 이미 명시했듯, 영어 원문 인용문은 프론트 정적 데이터에 두지 않고 `/evidence`, `/evidence/{id}` 엔드포인트 응답에서 받는다. `ending-thresholds.ts`(존엄 70/40 임계값)는 예외적으로 프론트에도 상수로 둘 수 있으나, 이는 UI가 엔딩 분기에 따라 다른 톤의 메시지를 미리 준비해두는 등 표시 목적으로만 쓰여야 하며, **실제 엔딩 판정 자체는 항상 백엔드 응답(`gameOver` 필드)을 신뢰**해야 한다 — 프론트가 자체적으로 재계산해 백엔드와 다른 판정을 내리는 일이 없도록 한다.

---

## 10. Claude Code 구현 시 권장 순서

`backend-technical-spec.md` §11("첫 슬라이스 1개만 end-to-end로 완성한 뒤 확장")과 동일한 철학을 프론트에도 적용한다.

1. **9.2절의 API 경로 방식을 사용자에게 먼저 확인.** 이게 정해지지 않으면 `lib/api-client/`를 짤 수 없으므로 가장 먼저 처리한다.
2. `data/scenes.ts`, `data/evidence.ts` 작성 — 1.2절 일러스트 매핑을 그대로 반영, `quote` 필드는 비워둠(9.4절)
3. `TitleScreen.tsx` → `BattleScreen.tsx`(배경 이미지 표시까지만) — 가장 단순한 화면부터 시각적으로 먼저 확인
4. `hooks/use-trial-progression.ts`, `hooks/use-typing-effect.ts` — 게임 진행 로직, 아직 API 연동 없이 더미 데이터로 동작 검증
5. `lib/api-client/trial-progression.ts` 연결 — 실제 백엔드 호출로 전환
6. `DialogueBox.tsx`, `ChoiceList.tsx` — 핵심 인터랙션 완성, 여기까지 되면 한 장면을 처음부터 끝까지 플레이 가능해야 함
7. `ObjectionBanner.tsx`, `EvidenceModal.tsx`, `EvidenceList.tsx` — 증거 제출 연출(8.2절 타이밍 준수)
8. `ClimaxOverlay.tsx` — `hath_not_moment` 장면 특수 처리, 6.2절의 비율 확인을 이 시점에 마칠 것
9. `EndingScreen.tsx` — 엔딩 텍스트 표시, AI 생성 로딩 상태 포함
10. 전체 플레이스루 — 1번 장면부터 6번 장면까지, 그리고 엔딩까지 한 번도 끊기지 않고 진행되는지 직접 확인. 1.2절의 `hath_not` 아이콘 미해결 사항이 이 시점까지 해결되지 않았다면 여기서 다시 사용자에게 확인할 것

---

## 11. 관련 문서 — 작업 범위 분담

| 문서 | 다루는 범위 | 본 문서와의 관계 |
|---|---|---|
| `game-design-document.md` | 기획 의도, 내러티브, 포트폴리오 포지셔닝 | 배경지식. 코드 작업과 직접 관련 없음 |
| `illustration-prompts.md` | 일러스트 생성 프롬프트(이미 완료된 작업의 기록) | 11장 일러스트가 어떤 의도로 만들어졌는지의 출처. 신규 작업과는 무관 |
| `backend-technical-spec.md` | 백엔드 아키텍처(Titanic 표준), API 경로, 도메인 모델 | 본 문서가 호출하는 대상. 9.2절의 경로 미확정 이슈는 이 문서 §9.3과 직결됨 |
| `structure.md` | Titanic 아키텍처 표준 원본 | 백엔드가 따르는 표준. 본 문서는 그 철학(1.3절)만 빌려오고 동일한 폴더명을 강제하지는 않음 — Next.js 관용 구조를 우선함 |
| ~~`claude-code-spec.md`~~ | (폐기) | 0장 참조 |
| ~~`game-technical-spec.md`~~ | (부분 폐기, §2·§4만 흡수) | 0장 참조 |
| 본 문서 | Next.js 프론트엔드 구조, 컴포넌트 분할, 일러스트 적용, 백엔드 연동 | 프론트엔드 신규 구축의 1차 레퍼런스 |

**작업 착수 전 필수 확인 사항 (Claude Code용 체크리스트):**

- [ ] 9.2절의 API 경로 방식(Next.js 라우트 vs 독립 FastAPI)을 사용자에게 먼저 확인했는가 — 확인 없이 진행 금지
- [ ] 1.2절의 `hath_not` 아이콘 부재 문제에 대해 (a)/(b)/(c) 중 어느 방식을 택할지 사용자에게 확인했는가
- [ ] 6.2절의 `scene-hath-not.png` 실제 비율을 확인 없이 임의로 3:4 레이아웃 분기 코드를 작성하지 않았는가
- [ ] `shylock-trial.jsx`의 `callGemini` 같은 Gemini API 직접 호출 패턴이 신규 코드 어디에도 재등장하지 않았는가(9.3절)
