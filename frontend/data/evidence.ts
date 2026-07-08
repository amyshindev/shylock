export interface EvidenceMeta {
  id: string;
  name: string;
  icon: string;
  desc: string;
  act: string;
  iconFallback?: string;
  /** Adaptation note for items not grounded in the original play text. */
  note?: string;
}

export const EVIDENCE_META: EvidenceMeta[] = [
  {
    id: "gaberdine",
    name: "낡은 외투",
    icon: "/assets/evidence-gaberdine.png",
    desc: "안토니오가 '개'라 부르며 침을 뱉었던 외투. 아직도 얼룩이 남아 있다.",
    act: "Act I, Scene 3",
  },
  {
    id: "bond",
    name: "살 1파운드 계약서",
    icon: "/assets/evidence-bond.png",
    desc: "안토니오와 맺은 계약. 법적으로 완전히 유효하다.",
    act: "Act I, Scene 3",
  },
  {
    id: "venice_charter",
    name: "베네치아의 헌장",
    icon: "",
    iconFallback: "🏛",
    desc: "이 도시가 상인들의 도시로 설 수 있는 이유. 계약이 계약으로 지켜지기 때문이다.",
    act: "Act IV, Scene 1",
  },
  {
    id: "bassanio_gold",
    name: "바사니오가 내민 돈",
    icon: "",
    iconFallback: "💰",
    desc: "원금의 열 배. 바사니오가 안토니오를 대신해 내미는 돈이다.",
    act: "Act IV, Scene 1",
  },
  {
    id: "scales",
    name: "저울",
    icon: "",
    iconFallback: "⚖",
    desc: "계약서에 명시된, 살을 정확히 달기 위한 도구. 그 자체로는 죄가 없다.",
    act: "Act IV, Scene 1",
  },
  {
    id: "hath_not",
    name: "유대인의 증언",
    icon: "",
    iconFallback: "✊",
    desc: "하나의 인간으로서 샤일록이 한 말.",
    act: "Act III, Scene 1",
  },
  {
    id: "jessica",
    name: "제시카의 편지",
    icon: "/assets/evidence-jessica.png",
    desc: "딸이 도망치며 남긴 흔적. 돈과 보석을 훔쳐갔다.",
    act: "Act III, Scene 1",
  },
  {
    id: "leah_ring",
    name: "리아의 반지",
    icon: "",
    iconFallback: "💍",
    desc: "죽은 아내 리아가 총각 시절의 샤일록에게 준 반지. 제시카가 훔쳐 달아나, 원숭이 한 마리와 바꿔버렸다.",
    act: "Act III, Scene 1",
  },
  {
    id: "whetted_knife",
    name: "갈아온 칼",
    icon: "",
    iconFallback: "🔪",
    desc: "재판 내내 조용히 갈아온 칼. 방금 전까지는, 정의를 집행할 도구였다.",
    act: "Act IV, Scene 1",
  },
  {
    id: "bond_wording",
    name: "계약서의 문구",
    icon: "",
    iconFallback: "✒",
    desc: "'살 1파운드.' 그 문구엔 정확히 그렇게만 쓰여 있다. 더도, 덜도 아니게.",
    act: "Act IV, Scene 1",
  },
  {
    id: "blood",
    name: "피 한 방울 조항",
    icon: "/assets/evidence-blood.png",
    desc: "포샤의 역전 논리. 살은 잘라도 피는 흘리면 안 된다.",
    act: "Act IV, Scene 1",
  },
  {
    id: "alien_law",
    name: "외국인 조항",
    icon: "",
    iconFallback: "🛂",
    desc: "베네치아 시민이 아닌 자가 시민의 목숨을 노리면 적용되는 법. 포샤의 두 번째 반전.",
    act: "Act IV, Scene 1",
  },
  {
    id: "ghetto_gate",
    name: "게토로 돌아가는 문",
    icon: "",
    iconFallback: "🕍",
    desc: "밤마다 유대인을 격리 구역에 가두던 제도. 도시가 강제한 구조적 격리.",
    act: "역사적 각색 (원작에 없음)",
    note: "원작 희곡에는 없는 역사적 각색. 16세기 베네치아에는 유대인을 밤마다 게토에 가두는 제도가 있었으나, 셰익스피어는 이를 언급하지 않는다.",
  },
];

export const EVIDENCE_BY_ID = Object.fromEntries(
  EVIDENCE_META.map((e) => [e.id, e]),
) as Record<string, EvidenceMeta>;
