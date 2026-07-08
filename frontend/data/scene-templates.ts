import type { SceneTemplate } from "@/data/scene-types";

const N = "narration" as const;
const S = "speech" as const;

/** Static structure + fallback copy when API dialogue is unavailable. */
export const SCENE_TEMPLATES: SceneTemplate[] = [
  {
    id: "opening",
    speaker: "NARRATOR",
    backgroundImage: "/assets/scene-crowd-jeers.png",
    fallbackLines: [
      { text: "베네치아 법정. 해가 지고 있다. 돌벽에는 그림자가 기운다.", kind: N },
      { text: "샤일록, 당신은 지금 이 법정에 서 있다.", kind: N },
      { text: "당신의 적들이 당신을 둘러싸고 있다.", kind: N },
      { text: "당신에게는 법이 있다. 계약이 있다.", kind: N },
      { text: "... 그것으로 충분할 것인가?", kind: N },
    ],
    challengeTemplate: null,
    availableEvidence: [],
  },
  {
    id: "portia_opens",
    speaker: "PORTIA",
    speakerLabel: "포샤",
    backgroundImage: "/assets/scene-portia-opens.png",
    fallbackLines: [
      { text: "샤일록, 당신은 안토니오의 살 1파운드를 요구하오.", kind: S },
      {
        text: "법정은 그 증서의 효력을 인정하오. 그러나 그 전에, 내 말을 들으시오.",
        kind: S,
      },
      {
        text: "자비란 강요로 얻어지는 것이 아니오. 그것은 하늘에서 부드럽게 내리는 비와 같이, 스스로 내려와 땅을 적시는 것이오.",
        kind: S,
      },
      {
        text: "자비는 이중으로 축복받은 것이오 — 베푸는 자와 받는 자를 동시에 축복하니.",
        kind: S,
      },
      {
        text: "왕의 왕관보다 자비로운 마음이 더 위대하다 하였소. 권력의 자리에 앉은 자일수록, 그 힘을 어떻게 쓰는가로 진정한 위대함이 드러나는 법이오.",
        kind: S,
      },
      { text: "샤일록, 당신에게는 그 증서를 강제할 권리가 있소.", kind: S },
      {
        text: "하지만 나는 당신에게 묻고 싶소 — 그 권리를 반드시 끝까지 쥐고 있어야만 하는지.",
        kind: S,
      },
      { text: "세 배의 돈을 받으시오. 그것으로 충분하지 않소?", kind: S },
      { text: "이 법정은, 그리고 나는, 당신의 자비를 기다리고 있소.", kind: S },
    ],
    challengeTemplate: {
      header: "▶ 샤일록의 선택",
      fallbackText: "자비를 베풀라고? 당신들이 내게 베푼 자비는 어디 있소?",
      options: [
        {
          id: "bond_signature",
          fallbackText: "이 증서엔 내 서명도, 안토니오의 서명도 있소. 무엇이 문제요?",
          evidence: "bond",
          dpChange: 12,
          hpCost: 5,
        },
        {
          id: "bond_double_standard",
          fallbackText: "베네치아 사람이 맺은 계약이라면, 당신들은 이렇게 따지지 않았을 것이오",
          evidence: "bond",
          dpChange: 18,
          hpCost: 12,
        },
        {
          id: "bond_lay_down",
          fallbackText: "(계약서를 법정 앞에 조용히 내려놓는다)",
          evidence: "bond",
          dpChange: 5,
          hpCost: 3,
        },
        {
          id: "charter_merchant_trust",
          fallbackText: "이 법정이 계약을 어긴다면, 어느 상인이 다시 이 도시를 믿겠소?",
          evidence: "venice_charter",
          dpChange: 16,
          hpCost: 8,
        },
        {
          id: "charter_law_precedent",
          fallbackText: "법이 한 번 흔들리면, 그다음은 누구의 계약이오?",
          evidence: "venice_charter",
          dpChange: 18,
          hpCost: 10,
        },
        {
          id: "charter_follow_law",
          fallbackText: "나는 그저 이 도시의 법을 따를 뿐이오",
          evidence: "venice_charter",
          dpChange: 10,
          hpCost: 4,
        },
      ],
    },
    availableEvidence: ["bond", "venice_charter"],
  },
  {
    id: "bassanio_plea",
    speaker: "BASSANIO",
    speakerLabel: "바사니오",
    backgroundImage: "/assets/scene-bassanio-plea.png",
    fallbackLines: [
      { text: "샤일록, 내가 빌린 돈은 3천 두캇이었소. 그 열 배를 드리겠소.", kind: S },
      {
        text: "당신이 원하는 게 정말 돈이라면, 이보다 더 큰 액수는 없을 것이오.",
        kind: S,
      },
      {
        text: "제발... 이번 한 번만 자비를 베푸시오. 당신도 사람이라면, 마음이 있을 것이오.",
        kind: S,
      },
      {
        text: "당신이 지금 손에 쥔 칼로 얻으려는 건 정의가 아니오. 그저 오래 묵은 증오요.",
        kind: S,
      },
    ],
    challengeTemplate: {
      header: "▶ 샤일록의 선택",
      fallbackText: "바사니오가 당신을 설득하려 한다. 당신은—",
      options: [
        {
          id: "gold_refuse_direct",
          fallbackText: "금액이 문제가 아니오. 내가 원하는 건 이 증서요",
          evidence: "bassanio_gold",
          dpChange: 13,
          hpCost: 6,
        },
        {
          id: "gold_shame_bribe",
          fallbackText: "돈으로 나를 매수하려 하다니, 당신들이야말로 부끄러운 줄 아시오",
          evidence: "bassanio_gold",
          dpChange: 18,
          hpCost: 12,
        },
        {
          id: "gold_push_away",
          fallbackText: "(동전 더미를 조용히 밀어낸다)",
          evidence: "bassanio_gold",
          dpChange: 6,
          hpCost: 3,
        },
        {
          id: "scales_no_reason",
          fallbackText: "이유를 대라 하셨소? 이유는 없소. 그저 내 뜻이오",
          evidence: "scales",
          dpChange: 14,
          hpCost: 7,
        },
        {
          id: "scales_humour",
          fallbackText:
            "어떤 이는 돼지를 보면 못 견디고, 어떤 이는 백파이프 소리에 참지 못하오. 나는 이 사람에 대한 미움을 다스리지 못할 뿐이오",
          evidence: "scales",
          dpChange: 18,
          hpCost: 11,
        },
        {
          id: "scales_weigh",
          fallbackText: "(저울을 꺼내 조용히 무게를 가늠한다)",
          evidence: "scales",
          dpChange: 8,
          hpCost: 4,
        },
      ],
    },
    availableEvidence: ["bassanio_gold", "scales"],
  },
  {
    id: "crowd_jeers",
    speaker: "CROWD",
    speakerLabel: "군중",
    backgroundImage: "/assets/scene-crowd-jeers.png",
    fallbackLines: [
      { text: '"저 유대인을 보라!"', kind: S },
      { text: '"자비도 모르는 자가!"', kind: S },
      { text: "웅성거림이 법정을 가득 채운다.", kind: N },
    ],
    challengeTemplate: {
      header: "▶ 샤일록의 선택",
      fallbackText: "군중의 조롱에 당신은—",
      options: [
        {
          id: "coat_show_spit",
          fallbackText: "보시오. 당신들이 뱉은 것이, 아직도 이 옷에 남아 있소",
          evidence: "gaberdine",
          dpChange: 13,
          hpCost: 6,
        },
        {
          id: "coat_before_dry",
          fallbackText: "이 얼룩이 마르기도 전에, 당신들은 내게 자비를 말하는구려",
          evidence: "gaberdine",
          dpChange: 18,
          hpCost: 12,
        },
        {
          id: "coat_show_silent",
          fallbackText: "(외투를 조용히 보여준다)",
          evidence: "gaberdine",
          dpChange: 6,
          hpCost: 3,
        },
        {
          id: "ghetto_curfew",
          fallbackText: "해가 지면, 나는 저 문 안으로 돌아가야 하오. 당신들이 정한 대로",
          evidence: "ghetto_gate",
          dpChange: 15,
          hpCost: 7,
        },
        {
          id: "ghetto_who_guilty",
          fallbackText:
            "매일 밤 갇히는 자와, 매일 밤 자유로이 떠드는 자 — 이 법정에서 누가 죄인이오?",
          evidence: "ghetto_gate",
          dpChange: 18,
          hpCost: 11,
        },
        {
          id: "ghetto_look_silent",
          fallbackText: "(대답 대신, 게토로 향하는 문 쪽을 가만히 바라본다)",
          evidence: "ghetto_gate",
          dpChange: 8,
          hpCost: 4,
        },
      ],
    },
    availableEvidence: ["gaberdine", "ghetto_gate"],
  },
  {
    id: "jessica_attack",
    speaker: "PORTIA",
    speakerLabel: "포샤",
    backgroundImage: "/assets/scene-jessica-attack.png",
    fallbackLines: [
      {
        text: "샤일록, 법정은 한 가지를 기억하고 있소. 당신의 딸조차 당신의 집을 떠났다는 것을.",
        kind: S,
      },
      {
        text: "로렌조와 함께, 그리고 기독교로 개종하여. 그녀는 스스로 아버지의 이름을 벗어던졌소.",
        kind: S,
      },
      {
        text: "혈육조차 등을 돌리게 만드는 자에게, 낯선 이의 살 한 파운드가 그리 소중하다니 기이한 일이오.",
        kind: S,
      },
      {
        text: "성경에도 이르길, 사람이 제 집을 다스리지 못하면 어찌 하나님의 교회를 돌보겠느냐 하였소.",
        kind: S,
      },
      {
        text: "당신은 딸의 마음 하나 붙들지 못한 자요. 그런 자가 어찌 이 법정에서 정의를 논하려 하시오?",
        kind: S,
      },
      {
        text: "정을 나눌 줄 모르는 자이니, 계약 또한 정 없이 읽으려 하는구려.",
        kind: S,
      },
    ],
    challengeTemplate: {
      header: "▶ 샤일록의 선택",
      fallbackText: "딸의 이름이 법정에 소환됐다.",
      options: [
        {
          id: "defend_jessica",
          fallbackText: "제시카는 내 딸이오. 이 법정이 그 상처를 다시 후벼 파는 것을 두고 볼 이유는 없소.",
          evidence: "jessica",
          dpChange: 15,
          hpCost: 12,
        },
        {
          id: "letter_irrelevant",
          fallbackText: "그 애가 어떤 선택을 했든, 그건 이 계약과 무관한 일이오.",
          evidence: "jessica",
          dpChange: 12,
          hpCost: 6,
        },
        {
          id: "letter_fold_silent",
          fallbackText: "(편지를 조용히 접어 품에 넣는다)",
          evidence: "jessica",
          dpChange: 6,
          hpCost: 3,
        },
        {
          id: "ring_leah_gift",
          fallbackText:
            "이 반지는 총각 시절, 죽은 아내 리아에게 받은 것이오. 광야의 원숭이 떼를 다 준대도 나는 이걸 바꾸지 않았을 것이오.",
          evidence: "leah_ring",
          dpChange: 18,
          hpCost: 12,
        },
        {
          id: "ring_loss_dignity",
          fallbackText: "내가 잃은 것을 아신다면, 당신은 이걸 약점이라 부르지 못할 것이오.",
          evidence: "leah_ring",
          dpChange: 15,
          hpCost: 8,
        },
        {
          id: "ring_clutch_silent",
          fallbackText: "(빈 손가락을 조용히 감싸 쥔다)",
          evidence: "leah_ring",
          dpChange: 8,
          hpCost: 4,
        },
      ],
    },
    availableEvidence: ["jessica", "leah_ring"],
  },
  {
    id: "jessica_duet",
    speaker: "JESSICA",
    speakerLabel: "제시카",
    backgroundImage: "/assets/scene-jessica-duet.png",
    fallbackLines: [
      {
        text: "벨몬트의 정원. 달빛이 낮게 깔린다. 제시카와 로렌조가 나란히 앉아 있다.",
        kind: N,
        speaker: "NARRATOR",
      },
      {
        text: "이런 밤이었지 — 트로일러스가 트로이의 성벽 위에서 크레시다를 향한 그리움에 한숨짓던 것도.",
        kind: S,
        speaker: "LORENZO",
        speakerLabel: "로렌조",
      },
      {
        text: "이런 밤이었죠 — 디도가 버들가지를 들고 해변에 서서, 떠나버린 연인을 향해 손짓하던 것도.",
        kind: S,
        speaker: "JESSICA",
        speakerLabel: "제시카",
      },
      {
        text: "이런 밤이었지 — 메데이아가 마법의 약초를 모아, 늙은 아이손을 다시 젊게 했던 것도.",
        kind: S,
        speaker: "LORENZO",
        speakerLabel: "로렌조",
      },
      {
        text: "...그리고 이런 밤이었죠. 제가 아버지의 집에서 도망쳐 나온 것도.",
        kind: S,
        speaker: "JESSICA",
        speakerLabel: "제시카",
      },
      { text: "제시카...?", kind: S, speaker: "LORENZO", speakerLabel: "로렌조" },
      {
        text: "당신은 계속 옛날 연인들 얘기를 하지만, 로렌조 — 그들은 전부 버림받았거나, 버리고 떠났어요.",
        kind: S,
        speaker: "JESSICA",
        speakerLabel: "제시카",
      },
      {
        text: "우리 이야기도 그렇게 끝날까요?",
        kind: S,
        speaker: "JESSICA",
        speakerLabel: "제시카",
      },
      { text: "그런 뜻이 아니었어—", kind: S, speaker: "LORENZO", speakerLabel: "로렌조" },
      {
        text: "알아요. 하지만 저는... 오늘 밤 계속 아버지 생각이 나요.",
        kind: S,
        speaker: "JESSICA",
        speakerLabel: "제시카"
      },
      {
        text: "지금쯤 법정은 어떻게 됐을까요.",
        kind: S,
        speaker: "JESSICA",
        speakerLabel: "제시카",
      },
      {
        text: "악사들을 불러 음악을 청하지. 그럼 마음이 좀 놓일 거야.",
        kind: S,
        speaker: "LORENZO",
        speakerLabel: "로렌조",
      },
      {
        text: "멀리서 악사들이 현을 고르는 소리가 들린다. 곧 부드러운 선율이 정원에 퍼진다.",
        kind: N,
        speaker: "NARRATOR",
      },
      {
        text: "...저는 아름다운 음악을 들으면 마음이 편치 않아요.",
        kind: S,
        speaker: "JESSICA",
        speakerLabel: "제시카",
      },
      { text: "의아하군. 왜지?", kind: S, speaker: "LORENZO", speakerLabel: "로렌조" },
      {
        text: "모르겠어요. 그냥... 이렇게 평온한 순간일수록, 제 안의 무언가가 더 시끄러워져요.",
        kind: S,
        speaker: "JESSICA",
        speakerLabel: "제시카",
      },
    ],
    challengeTemplate: null,
    availableEvidence: [],
  },
  {
    // Fixed climax scene — scripted verbatim, no item/choice UI (same pattern as
    // jessica_duet). Stat effects are applied server-side when the scene finishes.
    id: "hath_not_moment",
    speaker: "SHYLOCK",
    speakerLabel: "샤일록",
    backgroundImage: "/assets/scene-hath-not.png",
    fallbackLines: [
      {
        text: "샤일록, 마지막으로 묻겠소. 당신은 자비가 무엇인지 아시오?",
        kind: S,
        speaker: "PORTIA",
        speakerLabel: "포샤",
      },
      { text: "...", kind: S, speaker: "SHYLOCK", speakerLabel: "샤일록" },
      { text: "유대인은 눈이 없소?", kind: S, speaker: "SHYLOCK", speakerLabel: "샤일록" },
      {
        text: "손이, 오장육부가, 감정이 없소?",
        kind: S,
        speaker: "SHYLOCK",
        speakerLabel: "샤일록",
      },
      {
        text: "찌르면 피 흘리지 않소? 간지럽히면 웃지 않소? 독을 먹이면 죽지 않소?",
        kind: S,
        speaker: "SHYLOCK",
        speakerLabel: "샤일록",
      },
      {
        text: "당신들이 나머지 모든 점에서 우리와 같다면, 이 점에서도 우리는 같을 것이오.",
        kind: S,
        speaker: "SHYLOCK",
        speakerLabel: "샤일록",
      },
      {
        text: "법정 안이 일순 조용해진다. 야유하던 이들조차, 잠시 입을 다문다.",
        kind: N,
        speaker: "NARRATOR",
      },
      {
        text: "...계속하시오, 재판을 진행하겠소.",
        kind: S,
        speaker: "PORTIA",
        speakerLabel: "포샤",
      },
      // Antonio cut — illustration TBD, blank screen for now (backgroundImage: "").
      {
        text: "줄곧 침착했던 안토니오의 손끝이 미세하게 떨린다.",
        kind: N,
        speaker: "NARRATOR",
        backgroundImage: "",
      },
      {
        text: "...그때, 저 사람은 아무 소리도 내지 않았었지.",
        kind: S,
        speaker: "ANTONIO",
        speakerLabel: "안토니오",
        backgroundImage: "",
      },
      {
        text: "그는 다시 고개를 든다. 여전히 죽음을 받아들일 준비가 된 얼굴로.",
        kind: N,
        speaker: "NARRATOR",
        backgroundImage: "",
      },
    ],
    challengeTemplate: null,
    availableEvidence: [],
  },
  {
    id: "blood_reveal",
    speaker: "PORTIA",
    speakerLabel: "포샤",
    backgroundImage: "/assets/scene-blood-reveal.png",
    fallbackLines: [
      { text: "살을 잘라도 좋소.", kind: S },
      { text: "단—", kind: S },
      { text: "피를 한 방울도 흘려서는 안 되오.", kind: S },
      { text: "살은 딱 1파운드. 그 이상도 이하도 안 되오.", kind: S },
    ],
    challengeTemplate: {
      header: "▶ 샤일록의 선택",
      fallbackText: "이건 말이 안 된다. 하지만 법정이 고개를 끄덕인다.",
      options: [
        {
          id: "blood_impossible",
          fallbackText: "피 없이 살을 자르는 건 불가능하오!",
          evidence: "blood",
          dpChange: 15,
          hpCost: 10,
        },
        {
          id: "drop_knife",
          fallbackText: "...(칼을 내려놓는다)",
          evidence: null,
          dpChange: -10,
          hpCost: 0,
        },
        {
          id: "take_principal_only",
          fallbackText: "그렇다면 원금만 받겠소",
          evidence: "bond",
          dpChange: 5,
          hpCost: 3,
        },
      ],
    },
    availableEvidence: ["blood", "bond", "hath_not"],
  },
  {
    id: "alien_law_reveal",
    speaker: "PORTIA",
    speakerLabel: "포샤",
    backgroundImage: "/assets/scene-alien-law-reveal.png",
    challengeAfterLineIndex: 0,
    fallbackLines: [
      { text: "당신은 칼을 거둔다.", kind: N },
      { text: "포샤가 손을 든다.", kind: N },
      { text: '"기다리시오, 유대인."', kind: S },
      { text: '"이 법에는 아직 다른 조항이 남아 있소."', kind: S },
    ],
    challengeTemplate: {
      header: "▶ 샤일록의 선택",
      fallbackText: "외국인이라는 이유로, 법이 이번엔 당신의 목숨까지 가져가려 한다.",
      options: [
        {
          id: "plead_for_principal",
          fallbackText: "원금만이라도... 그것만은 받게 해주시오.",
          evidence: "bond",
          dpChange: 5,
          hpCost: 3,
        },
      ],
    },
    availableEvidence: ["alien_law", "blood", "hath_not", "jessica"],
  },
  {
    id: "jessica_intervention",
    speaker: "JESSICA",
    speakerLabel: "제시카",
    backgroundImage: "/assets/scene-jessica-intervention.png",
    fallbackLines: [{ text: "안녕하세요", kind: S }],
    challengeTemplate: null,
    availableEvidence: [],
  },
];
