# 리밸런싱 — 선택지/고정 씬 수치 정리 및 포샤 HP 소진 가능성

기준: `backend/apps/shylock_trial/app/constants/scene_choices.py`,
`scene_catalog.py`, `game_balance.py` (2026-08-05 시점 코드).

`portia_damage`는 선택 시점의 `dp_delta`(고정값)로부터 `compute_portia_damage()`로
계산되며, 실제로 적용된 `dp_gain`(투발 강화 보너스, 낮은 HP로 인한 절반 감소,
베니스 방패 등으로 달라질 수 있는 값)과는 **무관**합니다. 즉 어떤 스킬을 쓰든
같은 선택지의 `portia_damage`는 항상 고정입니다.

```python
def compute_portia_damage(dp_delta):
    if dp_delta <= 0:
        return 0 if dp_delta <= -5 else 1
    scaled = round(dp_delta * 0.55)          # PORTIA_DAMAGE_DP_RATIO
    return max(2, min(14, scaled))           # PORTIA_DAMAGE_MIN..MAX
```

## 1. 선택형 씬 (씬당 최종 선택은 1개)

각 씬은 2개의 증거 아이템(예: `bond` / `venice_charter`) × 3개 세부 선택지로
구성된 "아이템 먼저 선택 → 세부 문구 선택" 2단계 UI지만, 실제로 `submit_choice`
호출은 씬당 **정확히 1회**입니다. 즉 6개 중 1개만 적용됩니다.

### portia_opens (씬 인덱스 1)

| choice_id | evidence | dp_delta | hp_cost | portia_damage |
|---|---|---:|---:|---:|
| bond_signature | bond | +12 | 8 | 7 |
| bond_double_standard | bond | +18 | 19 | **10** |
| bond_lay_down | bond | +5 | 5 | 3 |
| charter_merchant_trust | venice_charter | +16 | 12 | 9 |
| charter_law_precedent | venice_charter | +18 | 16 | **10** |
| charter_follow_law | venice_charter | +10 | 6 | 6 |

씬 최댓값(portia_damage): **10** (`bond_double_standard` 또는 `charter_law_precedent`)

### bassanio_plea (씬 인덱스 2)

| choice_id | evidence | dp_delta | hp_cost | portia_damage |
|---|---|---:|---:|---:|
| gold_refuse_direct | bassanio_gold | +13 | 9 | 7 |
| gold_shame_bribe | bassanio_gold | +18 | 19 | **10** |
| gold_push_away | bassanio_gold | +6 | 5 | 3 |
| scales_no_reason | scales | +14 | 11 | 8 |
| scales_humour | scales | +18 | 17 | **10** |
| scales_weigh | scales | +8 | 6 | 4 |

씬 최댓값: **10** (`gold_shame_bribe` 또는 `scales_humour`)

### crowd_jeers (씬 인덱스 3)

| choice_id | evidence | dp_delta | hp_cost | portia_damage |
|---|---|---:|---:|---:|
| coat_show_spit | gaberdine | +13 | 9 | 7 |
| coat_before_dry | gaberdine | +18 | 19 | **10** |
| coat_show_silent | gaberdine | +6 | 5 | 3 |
| ghetto_curfew | ghetto_gate | +15 | 11 | 8 |
| ghetto_who_guilty | ghetto_gate | +18 | 17 | **10** |
| ghetto_look_silent | ghetto_gate | +8 | 6 | 4 |

씬 최댓값: **10** (`coat_before_dry` 또는 `ghetto_who_guilty`)

### jessica_attack (씬 인덱스 4)

| choice_id | evidence | dp_delta | hp_cost | portia_damage |
|---|---|---:|---:|---:|
| defend_jessica | jessica | +15 | 19 | 8 |
| letter_irrelevant | jessica | +12 | 9 | 7 |
| letter_fold_silent | jessica | +6 | 5 | 3 |
| ring_leah_gift | leah_ring | +18 | 19 | **10** |
| ring_loss_dignity | leah_ring | +15 | 12 | 8 |
| ring_clutch_silent | leah_ring | +8 | 6 | 4 |

씬 최댓값: **10** (`ring_leah_gift`)

### blood_reveal (씬 인덱스 7) — 역전 씬, portia_damage 항상 0

`ChoiceEffect.portia_damage_override=0`이 걸려 있어 **어떤 선택을 해도
포샤에게 피해를 주지 않습니다** (이 씬은 포샤가 반전을 거는 쪽).

| choice_id | evidence | dp_delta | hp_cost | portia_damage |
|---|---|---:|---:|---:|
| blood_impossible | whetted_knife | +10 | 22 | 0 |
| drop_knife | whetted_knife | -10 | 0 | 0 |
| take_principal_only | whetted_knife | +6 | 16 | 0 |
| wording_letter_turned | bond_wording | +10 | 23 | 0 |
| wording_accept_letter | bond_wording | +7 | 17 | 0 |
| wording_reread_silent | bond_wording | +4 | 12 | 0 |

씬 최댓값: **0** (선택 무관)

## 2. 고정 씬 (선택지 없음, `FIXED_SCRIPT_SCENE_IDS`)

| scene_id | 씬 인덱스 | dp_delta | hp_cost | portia_damage | 비고 |
|---|---:|---:|---:|---:|---|
| opening | 0 | 0 | 0 | 0 | 대사만, 게이지 관여 없음 |
| jessica_duet | 5 | 0 | 0 | 0 | 벨몬트 컷어웨이, 순수 연출 |
| hath_not_moment | 6 | **+20** | **26** | **20** | `advance_scene`에서 자동 적용 (선택 불가) |
| alien_law_reveal | 8 | 0 | 0 | 0 | 최근 고정 씬 전환 (`alien_law_reveal_고정씬_전환.md`) — 이전엔 `plead_for_principal`(+5 dp/5 hp/3 dmg) 선택지가 있었으나 제거됨 |
| jessica_intervention | 9 | 0 | 0 | 0 | 현재 대사 1줄("안녕하세요")뿐인 스텁 |

`hath_not_moment`의 `portia_damage=20`은 씬 하나의 값으로는 선택지 캡(`PORTIA_DAMAGE_MAX=14`)을
넘는 유일한 수치입니다 (주석: "the speech silences the court not by argument but
by existence").

## 3. 포샤 HP(100)를 0까지 깎는 최적 경로가 존재하는가 — **존재하지 않았음 (2026-08-05 수정됨)**

> **업데이트**: 아래 3절은 수정 전 상태의 분석입니다. `_docs/portia-hp-fix.md`
> 스펙에 따라 `PORTIA_HP_START`/`MAX`를 100→70으로 낮추고 `blood_impossible`에
> portia_damage 10을 부여해 이 문제를 고쳤습니다. 검증 결과는 4절 참고.

### 계산

씬별로 고를 수 있는 최댓값만 모두 더하면:

| 씬 | 선택 가능 최대 portia_damage |
|---|---:|
| portia_opens | 10 |
| bassanio_plea | 10 |
| crowd_jeers | 10 |
| jessica_attack | 10 |
| blood_reveal | 0 (역전 씬, 항상 0) |
| hath_not_moment | 20 (고정, 선택 불가지만 항상 적용됨) |
| jessica_duet / alien_law_reveal / jessica_intervention | 0 |
| **합계** | **60** |

`PORTIA_HP_START = PORTIA_HP_MAX = 100`이므로,

```
100 - 60 = 40
```

**어떤 선택을 조합해도 포샤 HP는 최소 40 이상 남습니다.** 투발 강화(+5 DP
보너스), 베니스 역설 스킬, 낮은 HP로 인한 DP 획득 절반 감소 등은 모두
`trial.dp`에만 영향을 주고 `portia_damage`는 선택 시점의 고정 `dp_delta`로만
계산되므로, 어떤 스킬 조합을 써도 이 60이라는 캡을 넘길 방법이 없습니다.

### 결론

- `resolve_next_scene_index` / `is_narrative_complete` (백엔드
  `scene_progression.py`), `isLastNarrativeScene` (프론트엔드
  `lib/constants/scene-progression.ts`)가 정의하는 "포샤 HP <= 0 →
  jessica_intervention(구원 루트)" 분기는 **현재 수치상 플레이로는 도달
  불가능한 데드 콘텐츠**입니다.
- `jessica_intervention` 씬 자체도 아직 대사가 "안녕하세요" 한 줄뿐인 스텁이라,
  콘텐츠가 완성되지 않은 상태와도 일치합니다 — 의도적으로 막아둔 것인지,
  아니면 언젠가 이 분기를 플레이 가능하게 만들 계획이 있는지 확인이 필요합니다.
- 만약 이 구원 루트를 실제로 열어주려면, 다음 중 하나가 필요합니다:
  - `PORTIA_HP_START`를 60 이하로 낮추거나,
  - 선택지 caps(`PORTIA_DAMAGE_MAX=14`, `PORTIA_DAMAGE_DP_RATIO=0.55`)를 올려
    씬당 최대 피해를 키우거나,
  - `blood_reveal`처럼 damage-0으로 고정된 씬 일부에 조건부 피해를 허용하거나,
  - 씬을 하나 더 추가해 총합을 100에 근접시키는 방법.

## 4. 수정 내역 및 검증 (`_docs/portia-hp-fix.md`)

> **업데이트 (3차까지 진행됨)**: 아래는 1차 수정(`PORTIA_HP_START/MAX`
> 100→70) 시점의 분석입니다. 그 직후 70이 최적 경로 총합(70)과 정확히
> 일치해 여유가 0이라는 문제가 지적되어 60(여유 10)으로, 이후 다시
> 65(여유 5)로 재조정했고, 반응 톤 임계값도 비율 기반으로 리팩터링했습니다.
> **현재 값은 `PORTIA_HP_START/MAX = 65`.** 최신 내용은
> `_docs/portia-hp-fix.md` 하단의 "추가 조정" 절들(2차/3차) 참고.

두 가지를 변경했습니다 (백엔드 `game_balance.py`/`scene_choices.py`, 프론트엔드
`lib/constants/game-balance.ts`/`data/scene-templates.ts` 동일하게 반영):

1. `PORTIA_HP_START` / `PORTIA_HP_MAX`: 100 → **70**
2. `blood_reveal`의 `blood_impossible` 선택지: `portia_damage_override` 0 → **10**
   (다른 5개 선택지는 그대로 0 유지 — 이 씬은 여전히 "포샤가 반전을 거는" 씬)

새 최대 누적 portia_damage = 기존 60 + blood_impossible의 10 = **70**,
`PORTIA_HP_START`(70)와 정확히 일치하므로 이론상 정확히 0까지 도달 가능합니다
(그 이하 값으로는 절대 안 됨 — 예: 8을 골랐다면 총합 68 < 70이라 여전히 도달
불가능했을 것입니다).

### 검증 1 — 이론상 도달 가능 여부

씬별 선택 가능 최대 portia_damage(1절 기준) + `blood_impossible` 반영:

| 씬 | 최대 portia_damage |
|---|---:|
| portia_opens | 10 |
| bassanio_plea | 10 |
| crowd_jeers | 10 |
| jessica_attack | 10 |
| blood_reveal (`blood_impossible`) | 10 |
| hath_not_moment (고정) | 20 |
| **합계** | **70** |

`70 - 70 = 0` → **정확히 도달**. 어떤 선택도 낭비할 수 없는, 말 그대로
"거의 완벽한 플레이"가 요구됩니다.

### 검증 2 — 실제 시뮬레이션 (백엔드 실제 함수로 재현)

`apply_choice_resources`/`apply_skill_resources`/`get_choice_effect`를 그대로
불러와 최댓값 선택지 5개 + `hath_not_moment` 고정 효과 + 스킬 힐량을 순서대로
적용해봤습니다 (시작: DP 25 / HP 100 / 포샤 HP 70):

| 단계 | DP | HP | 포샤 HP |
|---|---:|---:|---:|
| 시작 | 25 | 100 | 70 |
| portia_opens → `bond_double_standard` | 43 | 81 | 60 |
| bassanio_plea → `gold_shame_bribe` | 61 | 62 | 50 |
| crowd_jeers → `coat_before_dry` | 79 | 43 | 40 |
| jessica_attack → `ring_leah_gift` | 97 | 24 | 30 |
| 스킬: 베니스의 모순 ×1 | 79 | 39 | 30 |
| 스킬: 론슬롯 ×2 | 59 | 57 | 30 |
| 스킬: 투발 ×2 | 43 | 69 | 30 |
| jessica_duet (효과 없음) | 43 | 69 | 30 |
| hath_not_moment (고정 +20/-26/-20) | 63 | 43 | 10 |
| 스킬: 투발 ×1 | 55 | 49 | 10 |
| 스킬: 론슬롯 ×1 | 45 | 58 | 10 |
| blood_reveal → `blood_impossible` | 55 | 36 | **0** |
| alien_law_reveal (효과 없음) | 55 | 36 | 0 |

**포샤 HP 0 도달 확인.** 이 경로 전체에서 HP가 가장 낮았던 지점은
jessica_attack 직후의 24 (스킬로 회복하기 전) — 게임오버(HP≤0)나 "탈진"
기준(HP≤20) 어느 쪽에도 걸리지 않고 **여유 있게 완주**합니다. 최종 상태는
DP 55 / HP 36 / 포샤 HP 0 → `resolve_ending_type`이 `portia_hp<=0`을
DP 티어보다 먼저 체크하므로 엔딩은 무조건 `rescued_ending`으로 확정됩니다.

스킬 사용량(베니스의 모순 1회 — 게임당 1회 제한과 일치, 론슬롯 3회, 투발 3회)은
모두 해당 시점에 필요한 DP를 실제로 보유한 상태에서 이루어졌고, 론슬롯/투발은
백엔드에 총 사용 횟수 제한이 없어 이 정도 반복이 실제로 가능합니다.

### 검증 3 — 회귀 테스트

`PORTIA_HP_START`/`MAX`가 100을 가정하던 백엔드 테스트 5곳을 상수 기반으로
고치고 (`test_trial_progression_interactor.py` ×2,
`test_hp_progression.py` ×2, `test_trial_progression_mapper.py` ×2),
`blood_impossible`이 더 이상 무피해가 아님을 반영해
`test_blood_reveal_choices_deal_no_portia_damage`를 수정 + 전용 테스트
(`test_blood_impossible_deals_portia_damage`)를 추가했습니다. 전체 백엔드
테스트 122개 통과, 프론트엔드 `tsc --noEmit` 클린.

### 결론

- 구원 루트(jessica_intervention)는 이제 **수치상 실제로 도달 가능**하며,
  도달하더라도 샤일록이 탈진/게임오버에 빠지지 않습니다 — 히든 루트가 진짜
  "히든"으로 남으면서도 완주 가능한 상태입니다.
- `PORTIA_HP_HIGH_THRESHOLD`(67) / `PORTIA_HP_LOW_THRESHOLD`(34) — 포샤
  반응 톤(침착/평정 흔들림)을 가르는 임계값 — 은 이번 1차 수정에서는
  **의도적으로 건드리지 않았습니다.** (→ 2차 수정에서 비율 기반으로
  리팩터링하고 60 스케일에 맞춰 40/20으로 조정했습니다. `_docs/portia-hp-fix.md`
  "추가 조정" 절 참고.)
