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
      { text: "베네치아 법정. 1596년.", kind: N },
      { text: "샤일록, 당신은 지금 이 법정에 서 있다.", kind: N },
      { text: "당신의 적들이 당신을 둘러싸고 있다.", kind: N },
      { text: "당신에게는 법이 있다. 계약이 있다.", kind: N },
      { text: "그것으로 충분한가?", kind: N },
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
          id: "appeal_contract",
          fallbackText: "계약은 법적으로 유효합니다",
          evidence: "bond",
          dpChange: 0,
        },
        {
          id: "appeal_humanity",
          fallbackText: "나도 인간이오 — 당신들처럼",
          evidence: "hath_not",
          dpChange: 20,
        },
        {
          id: "appeal_mercy",
          fallbackText: "(침묵한다)",
          evidence: null,
          dpChange: -15,
        },
      ],
    },
    availableEvidence: ["bond", "hath_not"],
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
          id: "invoke_bond",
          fallbackText: "계약서가 있소. 열 배라도 계약을 대신할 수 없소",
          evidence: null,
          dpChange: 15,
        },
        {
          id: "accuse_bassanio",
          fallbackText: "당신이 안토니오를 이 자리에 몰아넣은 거요",
          evidence: null,
          dpChange: 20,
        },
        {
          id: "cold_silence",
          fallbackText: "(눈을 감는다)",
          evidence: null,
          dpChange: -15,
        },
      ],
    },
    availableEvidence: ["bond", "gaberdine"],
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
          id: "show_gaberdine",
          fallbackText: "외투의 침 자국을 보여준다",
          evidence: "gaberdine",
          dpChange: 15,
        },
        {
          id: "ignore_court",
          fallbackText: "무시하고 판사를 바라본다",
          evidence: null,
          dpChange: 5,
        },
        {
          id: "rage_at_crowd",
          fallbackText: "분노로 맞선다",
          evidence: null,
          dpChange: -10,
        },
      ],
    },
    availableEvidence: ["gaberdine", "bond", "hath_not"],
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
        },
        {
          id: "reject_private_matter",
          fallbackText: "내 집안의 일을 이 법정의 저울에 함께 올리지 마시오.",
          evidence: "bond",
          dpChange: 10,
        },
        {
          id: "speechless",
          fallbackText: "(말을 잇지 못한다)",
          evidence: null,
          dpChange: -20,
        },
      ],
    },
    availableEvidence: ["jessica", "bond", "gaberdine"],
  },
  {
    id: "hath_not_moment",
    speaker: "PORTIA",
    speakerLabel: "포샤",
    backgroundImage: "/assets/scene-hath-not.png",
    fallbackLines: [
      { text: "샤일록, 마지막으로 묻겠소.", kind: S },
      { text: "당신은 왜 자비를 모르오?", kind: S },
      { text: "당신 안에 인간의 감정이 있기는 하오?", kind: S },
    ],
    challengeTemplate: {
      header: "▶ 샤일록의 선택",
      fallbackText: "이 순간이다. 당신의 말로 대답할 것인가.",
      options: [
        {
          id: "hath_not_speech",
          fallbackText: '"유대인에게 눈이 없소? 피가 없소?"',
          evidence: "hath_not",
          dpChange: 30,
        },
        {
          id: "bond_only",
          fallbackText: "자비는 계약서에 없소. 법만이 있을 뿐",
          evidence: "bond",
          dpChange: 5,
        },
        {
          id: "beg_mercy",
          fallbackText: "...부탁이오. 제발 계약을 이행해주시오",
          evidence: null,
          dpChange: -20,
        },
      ],
    },
    availableEvidence: ["hath_not", "bond", "gaberdine", "jessica"],
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
        },
        {
          id: "drop_knife",
          fallbackText: "...(칼을 내려놓는다)",
          evidence: null,
          dpChange: -10,
        },
        {
          id: "take_principal_only",
          fallbackText: "그렇다면 원금만 받겠소",
          evidence: "bond",
          dpChange: 5,
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
    fallbackLines: [
      { text: "당신은 칼을 거둔다.", kind: N },
      { text: "원금만이라도... 그것만은 받게 해주시오.", kind: N },
      { text: "포샤가 손을 든다.", kind: N },
      { text: '"기다리시오, 유대인."', kind: S },
      { text: '"이 법에는 아직 다른 조항이 남아 있소."', kind: S },
    ],
    challengeTemplate: {
      header: "▶ 샤일록의 선택",
      fallbackText: "외국인이라는 이유로, 법이 이번엔 당신의 목숨까지 가져가려 한다.",
      options: [
        {
          id: "reject_conversion",
          fallbackText: "개종이라니 — 차라리 죽음을 택하겠소",
          evidence: "alien_law",
          dpChange: 25,
        },
        {
          id: "bow_accept",
          fallbackText: "...그리하겠소. (고개를 숙인다)",
          evidence: null,
          dpChange: -25,
        },
        {
          id: "mock_mercy",
          fallbackText: "이것이 베네치아가 말하는 자비요?",
          evidence: "alien_law",
          dpChange: 15,
        },
      ],
    },
    availableEvidence: ["alien_law", "blood", "hath_not", "jessica"],
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
        text: "당신은 계속 옛날 연인들 얘기를 하지만, 로렌조 — 그들은 전부 버림받았거나, 버리고 떠났어요. 우리 이야기도 그렇게 끝날까요?",
        kind: S,
        speaker: "JESSICA",
        speakerLabel: "제시카",
      },
      { text: "그런 뜻이 아니었어—", kind: S, speaker: "LORENZO", speakerLabel: "로렌조" },
      {
        text: "알아요. 하지만 저는... 오늘 밤 계속 아버지 생각이 나요. 지금쯤 법정은 어떻게 됐을까요.",
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
    id: "jessica_intervention",
    speaker: "JESSICA",
    speakerLabel: "제시카",
    backgroundImage: "/assets/scene-jessica-intervention.png",
    fallbackLines: [{ text: "안녕하세요", kind: S }],
    challengeTemplate: null,
    availableEvidence: [],
  },
];
