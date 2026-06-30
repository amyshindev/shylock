export type Speaker = "NARRATOR" | "PORTIA" | "CROWD";

export interface ChoiceOption {
  id: string;
  text: string;
  evidence: string | null;
  dignityChange: number;
  confidenceChange: number;
  special?: "climax";
}

export interface Scene {
  id: string;
  speaker: Speaker;
  speakerLabel?: string;
  backgroundImage: string;
  lines: string[];
  challenge: {
    header?: string;
    text: string;
    options: ChoiceOption[];
  } | null;
  availableEvidence: string[];
}

/** Synced with _docs/shylock-trial.jsx */
export const SCENES: Scene[] = [
  {
    id: "opening",
    speaker: "NARRATOR",
    speakerLabel: "NARRATOR",
    backgroundImage: "/assets/scene-crowd-jeers.png",
    lines: [
      "베네치아 법정. 1596년.",
      "샤일록, 당신은 지금 이 법정에 서 있다.",
      "당신의 적들이 당신을 둘러싸고 있다.",
      "당신에게는 법이 있다. 계약이 있다.",
      "그것으로 충분한가?",
    ],
    challenge: null,
    availableEvidence: [],
  },
  {
    id: "portia_opens",
    speaker: "PORTIA",
    speakerLabel: "PORTIA · 판사",
    backgroundImage: "/assets/scene-portia-opens.png",
    lines: [
      "샤일록, 당신은 안토니오의 살 1파운드를 요구하오.",
      "자비를 베푸시오. 세 배의 돈을 받으시오.",
      "이 법정은 당신의 자비를 기다리고 있소.",
    ],
    challenge: {
      header: "▶ 샤일록의 선택",
      text: "자비를 베풀라고? 당신들이 내게 베푼 자비는 어디 있소?",
      options: [
        {
          id: "appeal_contract",
          text: "계약은 법적으로 유효합니다",
          evidence: "bond",
          dignityChange: 0,
          confidenceChange: 15,
        },
        {
          id: "appeal_humanity",
          text: "나도 인간이오 — 당신들처럼",
          evidence: "hath_not",
          dignityChange: 20,
          confidenceChange: 5,
        },
        {
          id: "appeal_mercy",
          text: "(침묵한다)",
          evidence: null,
          dignityChange: -15,
          confidenceChange: -5,
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
    lines: [
      '"저 유대인을 보라!"',
      '"자비도 모르는 자가!"',
      "웅성거림이 법정을 가득 채운다.",
    ],
    challenge: {
      header: "▶ 샤일록의 선택",
      text: "군중의 조롱에 당신은—",
      options: [
        {
          id: "show_gaberdine",
          text: "외투의 침 자국을 보여준다",
          evidence: "gaberdine",
          dignityChange: 15,
          confidenceChange: 10,
        },
        {
          id: "ignore_court",
          text: "무시하고 판사를 바라본다",
          evidence: null,
          dignityChange: 5,
          confidenceChange: 5,
        },
        {
          id: "rage_at_crowd",
          text: "분노로 맞선다",
          evidence: null,
          dignityChange: -10,
          confidenceChange: -10,
        },
      ],
    },
    availableEvidence: ["gaberdine", "bond"],
  },
  {
    id: "jessica_attack",
    speaker: "PORTIA",
    speakerLabel: "PORTIA · 판사",
    backgroundImage: "/assets/scene-jessica-attack.png",
    lines: [
      "샤일록, 당신의 딸조차 당신을 떠났소.",
      "로렌조와 함께. 기독교로 개종하여.",
      "당신 스스로도 사랑받지 못하는 자가 어찌 법의 보호를 요구하오?",
    ],
    challenge: {
      header: "▶ 샤일록의 선택",
      text: "딸의 이름이 법정에 소환됐다.",
      options: [
        {
          id: "defend_jessica",
          text: "제시카는 내 딸이오. 이 계약과 무슨 상관이오?",
          evidence: "jessica",
          dignityChange: 15,
          confidenceChange: 15,
        },
        {
          id: "reject_private_matter",
          text: "사적인 일을 법정에 끌어들이지 마시오",
          evidence: "bond",
          dignityChange: 10,
          confidenceChange: 10,
        },
        {
          id: "speechless",
          text: "(말을 잇지 못한다)",
          evidence: null,
          dignityChange: -20,
          confidenceChange: -15,
        },
      ],
    },
    availableEvidence: ["jessica", "bond", "gaberdine"],
  },
  {
    id: "hath_not_moment",
    speaker: "PORTIA",
    speakerLabel: "PORTIA · 판사",
    backgroundImage: "/assets/scene-hath-not.png",
    lines: [
      "샤일록, 마지막으로 묻겠소.",
      "당신은 왜 자비를 모르오?",
      "당신 안에 인간의 감정이 있기는 하오?",
    ],
    challenge: {
      header: "▶ 샤일록의 선택",
      text: "이 순간이다. 당신의 말로 대답할 것인가.",
      options: [
        {
          id: "hath_not_speech",
          text: '"유대인에게 눈이 없소? 피가 없소?"',
          evidence: "hath_not",
          dignityChange: 30,
          confidenceChange: 5,
          special: "climax",
        },
        {
          id: "bond_only",
          text: "자비는 계약서에 없소. 법만이 있을 뿐",
          evidence: "bond",
          dignityChange: 5,
          confidenceChange: 20,
        },
        {
          id: "beg_mercy",
          text: "...부탁이오. 제발 계약을 이행해주시오",
          evidence: null,
          dignityChange: -20,
          confidenceChange: 0,
        },
      ],
    },
    availableEvidence: ["hath_not", "bond", "gaberdine", "jessica"],
  },
  {
    id: "blood_reveal",
    speaker: "PORTIA",
    speakerLabel: "PORTIA · 판사",
    backgroundImage: "/assets/scene-blood-reveal.png",
    lines: [
      "살을 잘라도 좋소.",
      "단—",
      "피를 한 방울도 흘려서는 안 되오.",
      "살은 딱 1파운드. 그 이상도 이하도 안 되오.",
    ],
    challenge: {
      header: "▶ 샤일록의 선택",
      text: "이건 말이 안 된다. 하지만 법정이 고개를 끄덕인다.",
      options: [
        {
          id: "blood_impossible",
          text: "피 없이 살을 자르는 건 불가능하오!",
          evidence: "blood",
          dignityChange: 15,
          confidenceChange: -10,
        },
        {
          id: "drop_knife",
          text: "...(칼을 내려놓는다)",
          evidence: null,
          dignityChange: -10,
          confidenceChange: -20,
        },
        {
          id: "take_principal_only",
          text: "그렇다면 원금만 받겠소",
          evidence: "bond",
          dignityChange: 5,
          confidenceChange: 10,
        },
      ],
    },
    availableEvidence: ["blood", "bond", "hath_not"],
  },
  {
    id: "alien_law_reveal",
    speaker: "PORTIA",
    speakerLabel: "PORTIA · 판사",
    backgroundImage: "/assets/scene-alien-law-reveal.png",
    lines: [
      "당신은 칼을 거둔다.",
      "원금만이라도... 그것만은 받게 해주시오.",
      "포샤가 손을 든다.",
      '"기다리시오, 유대인."',
      '"이 법에는 아직 다른 조항이 남아 있소."',
    ],
    challenge: {
      header: "▶ 샤일록의 선택",
      text: "외국인이라는 이유로, 법이 이번엔 당신의 목숨까지 가져가려 한다.",
      options: [
        {
          id: "reject_conversion",
          text: "개종이라니 — 차라리 죽음을 택하겠소",
          evidence: "alien_law",
          dignityChange: 25,
          confidenceChange: -20,
        },
        {
          id: "bow_accept",
          text: "...그리하겠소. (고개를 숙인다)",
          evidence: null,
          dignityChange: -25,
          confidenceChange: 15,
        },
        {
          id: "mock_mercy",
          text: "이것이 베네치아가 말하는 자비요?",
          evidence: "alien_law",
          dignityChange: 15,
          confidenceChange: -5,
        },
      ],
    },
    availableEvidence: ["alien_law", "blood", "hath_not", "jessica"],
  },
];

export const HATH_NOT_QUOTE = `"Hath not a Jew eyes?
Hath not a Jew hands, organs, dimensions,
senses, affections, passions?

If you prick us, do we not bleed?
If you tickle us, do we not laugh?
If you poison us, do we not die?
And if you wrong us, shall we not revenge?"`;

export const TIMING = {
  objectionBannerMs: 900,
  evidenceModalMs: 2200,
  choiceSequenceMs: 2200,
} as const;
