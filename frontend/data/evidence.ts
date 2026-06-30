export interface EvidenceMeta {
  id: string;
  name: string;
  icon: string;
  desc: string;
  act: string;
  iconFallback?: string;
}

export const EVIDENCE_META: EvidenceMeta[] = [
  {
    id: "gaberdine",
    name: "낡은 가브딘",
    icon: "/assets/evidence-gaberdine.png",
    desc: "침 자국이 남아있는 샤일록의 외투",
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
    id: "blood",
    name: "피 한 방울 조항",
    icon: "/assets/evidence-blood.png",
    desc: "포샤의 역전 논리. 살은 잘라도 피는 흘리면 안 된다.",
    act: "Act IV, Scene 1",
  },
];

export const EVIDENCE_BY_ID = Object.fromEntries(
  EVIDENCE_META.map((e) => [e.id, e]),
) as Record<string, EvidenceMeta>;
