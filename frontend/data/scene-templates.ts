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
      { text: "자비를 베푸시오. 세 배의 돈을 받으시오.", kind: S },
      { text: "이 법정은 당신의 자비를 기다리고 있소.", kind: S },
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
          shylockHpChange: 15,
        },
        {
          id: "appeal_humanity",
          fallbackText: "나도 인간이오 — 당신들처럼",
          evidence: "hath_not",
          dpChange: 20,
          shylockHpChange: 5,
        },
        {
          id: "appeal_mercy",
          fallbackText: "(침묵한다)",
          evidence: null,
          dpChange: -15,
          shylockHpChange: -5,
        },
      ],
    },
    availableEvidence: ["bond", "hath_not"],
  },
  {
    id: "crowd_jeers",
    speaker: "CROWD",
    speakerLabel: "군중",
    backgroundImage: "/assets/scene-crowd-jeers.png",
    interactionType: "pressPresent",
    fallbackLines: [
      { text: '"저 유대인을 보라!"', kind: S },
      { text: '"자비도 모르는 자가!"', kind: S },
      { text: "웅성거림이 법정을 가득 채운다.", kind: N },
    ],
    challengeTemplate: null,
    pressPresent: {
      testimony: [
        {
          id: "t1",
          text: "저 유대인을 보라! 자비도 모르는 자가!",
          pressReaction: "그렇소! 법만 따를 뿐이오!",
        },
        {
          id: "t2",
          text: "이 자는 인간이 아니라 짐승이오.",
          pressReaction: "짐승이라니... 계속하시오.",
        },
      ],
      contradiction: {
        statementId: "t2",
        evidenceId: "hath_not",
      },
    },
    availableEvidence: ["hath_not", "gaberdine", "bond"],
  },
  {
    id: "jessica_attack",
    speaker: "PORTIA",
    speakerLabel: "포샤",
    backgroundImage: "/assets/scene-jessica-attack.png",
    fallbackLines: [
      { text: "샤일록, 당신의 딸조차 당신을 떠났소.", kind: S },
      { text: "로렌조와 함께. 기독교로 개종하여.", kind: S },
      { text: "당신 스스로도 사랑받지 못하는 자가 어찌 법의 보호를 요구하오?", kind: S },
    ],
    challengeTemplate: {
      header: "▶ 샤일록의 선택",
      fallbackText: "딸의 이름이 법정에 소환됐다.",
      options: [
        {
          id: "defend_jessica",
          fallbackText: "제시카는 내 딸이오. 이 계약과 무슨 상관이오?",
          evidence: "jessica",
          dpChange: 15,
          shylockHpChange: 15,
        },
        {
          id: "reject_private_matter",
          fallbackText: "사적인 일을 법정에 끌어들이지 마시오",
          evidence: "bond",
          dpChange: 10,
          shylockHpChange: 10,
        },
        {
          id: "speechless",
          fallbackText: "(말을 잇지 못한다)",
          evidence: null,
          dpChange: -20,
          shylockHpChange: -15,
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
          shylockHpChange: 5,
        },
        {
          id: "bond_only",
          fallbackText: "자비는 계약서에 없소. 법만이 있을 뿐",
          evidence: "bond",
          dpChange: 5,
          shylockHpChange: 20,
        },
        {
          id: "beg_mercy",
          fallbackText: "...부탁이오. 제발 계약을 이행해주시오",
          evidence: null,
          dpChange: -20,
          shylockHpChange: 0,
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
          shylockHpChange: -10,
        },
        {
          id: "drop_knife",
          fallbackText: "...(칼을 내려놓는다)",
          evidence: null,
          dpChange: -10,
          shylockHpChange: -20,
        },
        {
          id: "take_principal_only",
          fallbackText: "그렇다면 원금만 받겠소",
          evidence: "bond",
          dpChange: 5,
          shylockHpChange: 10,
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
          shylockHpChange: -20,
        },
        {
          id: "bow_accept",
          fallbackText: "...그리하겠소. (고개를 숙인다)",
          evidence: null,
          dpChange: -25,
          shylockHpChange: 15,
        },
        {
          id: "mock_mercy",
          fallbackText: "이것이 베네치아가 말하는 자비요?",
          evidence: "alien_law",
          dpChange: 15,
          shylockHpChange: -5,
        },
      ],
    },
    availableEvidence: ["alien_law", "blood", "hath_not", "jessica"],
  },
];
