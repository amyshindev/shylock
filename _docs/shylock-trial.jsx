import { useState, useEffect, useRef } from "react";

const ANTHROPIC_API_KEY = ""; // demo only — production uses backend ANTHROPIC_API_KEY

// ── 증거 데이터 ───────────────────────────────────────────────
const EVIDENCE = {
  gaberdine: {
    id: "gaberdine", name: "낡은 외투", icon: "🧥",
    desc: "침 자국이 남아있는 샤일록의 외투",
    quote: "You call me misbeliever, cut-throat dog, / And spit upon my Jewish gaberdine.",
    act: "Act I, Scene 3",
  },
  bond: {
    id: "bond", name: "살 1파운드 계약서", icon: "📜",
    desc: "안토니오와 맺은 계약. 법적으로 완전히 유효하다.",
    quote: "If you repay me not on such a day... let the forfeit be nominated for an equal pound of your fair flesh.",
    act: "Act I, Scene 3",
  },
  hath_not: {
    id: "hath_not", name: "유대인의 증언", icon: "✊",
    desc: "하나의 인간으로서 샤일록이 한 말.",
    quote: "Hath not a Jew eyes? If you prick us, do we not bleed? If you wrong us, shall we not revenge?",
    act: "Act III, Scene 1",
  },
  jessica: {
    id: "jessica", name: "제시카의 편지", icon: "💌",
    desc: "딸이 도망치며 남긴 흔적. 돈과 보석을 훔쳐갔다.",
    quote: "I would my daughter were dead at my foot, and the jewels in her ear.",
    act: "Act III, Scene 1",
  },
  blood: {
    id: "blood", name: "피 한 방울 조항", icon: "🩸",
    desc: "포샤의 역전 논리. 살은 잘라도 피는 흘리면 안 된다.",
    quote: "Shed thou no blood, nor cut thou less nor more but just a pound of flesh.",
    act: "Act IV, Scene 1",
  },
};

// ── 장면 데이터 ───────────────────────────────────────────────
const SCENES = [
  {
    id: "opening", speaker: "NARRATOR", portrait: null,
    lines: ["베네치아 법정. 1596년.", "샤일록, 당신은 지금 이 법정에 서 있다.", "당신의 적들이 당신을 둘러싸고 있다.", "당신에게는 법이 있다. 계약이 있다.", "그것으로 충분한가?"],
    challenge: null, availableEvidence: [],
  },
  {
    id: "portia_opens", speaker: "PORTIA", portrait: "PORTIA",
    lines: ["샤일록, 당신은 안토니오의 살 1파운드를 요구하오.", "자비를 베푸시오. 세 배의 돈을 받으시오.", "이 법정은 당신의 자비를 기다리고 있소."],
    challenge: {
      text: "자비를 베풀라고? 당신들이 내게 베푼 자비는 어디 있소?",
      options: [
        { id: "a", text: "계약은 법적으로 유효합니다", evidence: "bond", dignityChange: 0, confidenceChange: 15 },
        { id: "b", text: "나도 인간이오 — 당신들처럼", evidence: "hath_not", dignityChange: 20, confidenceChange: 5 },
        { id: "c", text: "(침묵한다)", evidence: null, dignityChange: -15, confidenceChange: -5 },
      ],
    },
    availableEvidence: ["bond", "hath_not"],
  },
  {
    id: "crowd_jeers", speaker: "CROWD", portrait: "CROWD",
    lines: ["\"저 유대인을 보라!\"", "\"자비도 모르는 자가!\"", "웅성거림이 법정을 가득 채운다."],
    challenge: {
      text: "군중의 조롱에 당신은—",
      options: [
        { id: "a", text: "외투의 침 자국을 보여준다", evidence: "gaberdine", dignityChange: 15, confidenceChange: 10 },
        { id: "b", text: "무시하고 판사를 바라본다", evidence: null, dignityChange: 5, confidenceChange: 5 },
        { id: "c", text: "분노로 맞선다", evidence: null, dignityChange: -10, confidenceChange: -10 },
      ],
    },
    availableEvidence: ["gaberdine", "bond"],
  },
  {
    id: "jessica_attack", speaker: "PORTIA", portrait: "PORTIA",
    lines: ["샤일록, 당신의 딸조차 당신을 떠났소.", "로렌조와 함께. 기독교로 개종하여.", "당신 스스로도 사랑받지 못하는 자가 어찌 법의 보호를 요구하오?"],
    challenge: {
      text: "딸의 이름이 법정에 소환됐다.",
      options: [
        { id: "a", text: "제시카는 내 딸이오. 이 계약과 무슨 상관이오?", evidence: "jessica", dignityChange: 15, confidenceChange: 15 },
        { id: "b", text: "사적인 일을 법정에 끌어들이지 마시오", evidence: "bond", dignityChange: 10, confidenceChange: 10 },
        { id: "c", text: "(말을 잇지 못한다)", evidence: null, dignityChange: -20, confidenceChange: -15 },
      ],
    },
    availableEvidence: ["jessica", "bond", "gaberdine"],
  },
  {
    id: "hath_not_moment", speaker: "PORTIA", portrait: "PORTIA",
    lines: ["샤일록, 마지막으로 묻겠소.", "당신은 왜 자비를 모르오?", "당신 안에 인간의 감정이 있기는 하오?"],
    challenge: {
      text: "이 순간이다. 당신의 말로 대답할 것인가.",
      options: [
        { id: "a", text: "\"유대인에게 눈이 없소? 피가 없소?\"", evidence: "hath_not", dignityChange: 30, confidenceChange: 5, special: "climax" },
        { id: "b", text: "자비는 계약서에 없소. 법만이 있을 뿐", evidence: "bond", dignityChange: 5, confidenceChange: 20 },
        { id: "c", text: "...부탁이오. 제발 계약을 이행해주시오", evidence: null, dignityChange: -20, confidenceChange: 0 },
      ],
    },
    availableEvidence: ["hath_not", "bond", "gaberdine", "jessica"],
  },
  {
    id: "blood_reveal", speaker: "PORTIA", portrait: "PORTIA",
    lines: ["살을 잘라도 좋소.", "단—", "피를 한 방울도 흘려서는 안 되오.", "살은 딱 1파운드. 그 이상도 이하도 안 되오."],
    challenge: {
      text: "이건 말이 안 된다. 하지만 법정이 고개를 끄덕인다.",
      options: [
        { id: "a", text: "피 없이 살을 자르는 건 불가능하오!", evidence: "blood", dignityChange: 15, confidenceChange: -10 },
        { id: "b", text: "...(칼을 내려놓는다)", evidence: null, dignityChange: -10, confidenceChange: -20 },
        { id: "c", text: "그렇다면 원금만 받겠소", evidence: "bond", dignityChange: 5, confidenceChange: 10 },
      ],
    },
    availableEvidence: ["blood", "bond", "hath_not"],
  },
];

// ── SVG 캐릭터 스프라이트 ─────────────────────────────────────
function PortraitPortia({ mood = "neutral" }) {
  const eyeColor = mood === "attack" ? "#cc0000" : "#4a3a1a";
  return (
    <svg viewBox="0 0 160 280" width="160" height="280" style={{ filter: "drop-shadow(0 8px 24px #00000080)" }}>
      {/* 법복 */}
      <ellipse cx="80" cy="230" rx="70" ry="60" fill="#1a1430" />
      <rect x="30" y="160" width="100" height="110" rx="8" fill="#1a1430" />
      {/* 흰 칼라 */}
      <ellipse cx="80" cy="165" rx="28" ry="14" fill="#e8e0d0" />
      {/* 목 */}
      <rect x="68" y="140" width="24" height="30" rx="4" fill="#d4a870" />
      {/* 얼굴 */}
      <ellipse cx="80" cy="110" rx="44" ry="50" fill="#d4a870" />
      {/* 눈썹 */}
      <path d="M55 90 Q65 85 75 90" stroke="#4a3010" strokeWidth="2.5" fill="none" />
      <path d="M85 90 Q95 85 105 90" stroke="#4a3010" strokeWidth="2.5" fill="none" />
      {/* 눈 */}
      <ellipse cx="67" cy="100" rx="9" ry="7" fill="white" />
      <ellipse cx="93" cy="100" rx="9" ry="7" fill="white" />
      <ellipse cx="68" cy="101" rx="5" ry="5" fill={eyeColor} />
      <ellipse cx="94" cy="101" rx="5" ry="5" fill={eyeColor} />
      <ellipse cx="69" cy="100" rx="2" ry="2" fill="#111" />
      <ellipse cx="95" cy="100" rx="2" ry="2" fill="#111" />
      {/* 코 */}
      <path d="M78 108 Q80 115 82 108" stroke="#b08040" strokeWidth="1.5" fill="none" />
      {/* 입 */}
      <path d={mood === "attack" ? "M68 125 Q80 120 92 125" : "M68 125 Q80 122 92 125"} stroke="#8b4040" strokeWidth="2" fill="none" />
      {/* 머리카락 */}
      <ellipse cx="80" cy="72" rx="46" ry="32" fill="#2a1a08" />
      <path d="M36 85 Q28 120 34 160" stroke="#2a1a08" strokeWidth="16" fill="none" strokeLinecap="round" />
      <path d="M124 85 Q132 120 126 160" stroke="#2a1a08" strokeWidth="16" fill="none" strokeLinecap="round" />
      {/* 가발 (역전재판 스타일) */}
      <ellipse cx="80" cy="65" rx="48" ry="28" fill="#e8e0c8" opacity="0.9" />
      <ellipse cx="80" cy="58" rx="42" ry="20" fill="#f0e8d0" />
      <rect x="32" y="62" width="20" height="50" rx="10" fill="#e8e0c8" />
      <rect x="108" y="62" width="20" height="50" rx="10" fill="#e8e0c8" />
      {/* 공격 시 효과 */}
      {mood === "attack" && (
        <g>
          <line x1="110" y1="80" x2="135" y2="60" stroke="#ff4444" strokeWidth="3" opacity="0.8" />
          <line x1="115" y1="75" x2="142" y2="65" stroke="#ff6666" strokeWidth="2" opacity="0.6" />
        </g>
      )}
    </svg>
  );
}

function PortraitShylock({ mood = "neutral" }) {
  return (
    <svg viewBox="0 0 160 280" width="160" height="280" style={{ filter: "drop-shadow(0 8px 24px #00000080)", transform: "scaleX(-1)" }}>
      {/* 외투 */}
      <ellipse cx="80" cy="230" rx="65" ry="58" fill="#2a1a08" />
      <rect x="32" y="155" width="96" height="115" rx="6" fill="#2a1a08" />
      {/* 가브딘 칼라 */}
      <path d="M55 160 Q80 150 105 160 L100 180 Q80 170 60 180 Z" fill="#3a2a10" />
      {/* 목 */}
      <rect x="68" y="138" width="24" height="28" rx="4" fill="#c49060" />
      {/* 얼굴 */}
      <ellipse cx="80" cy="108" rx="42" ry="48" fill="#c49060" />
      {/* 수염 */}
      <ellipse cx="80" cy="145" rx="22" ry="18" fill="#4a3820" />
      <path d="M60 138 Q80 155 100 138" fill="#4a3820" />
      {/* 눈썹 (굵고 심각한) */}
      <path d="M52 88 Q64 82 74 88" stroke="#2a1808" strokeWidth="3.5" fill="none" />
      <path d="M86 88 Q96 82 108 88" stroke="#2a1808" strokeWidth="3.5" fill="none" />
      {/* 눈 */}
      <ellipse cx="65" cy="100" rx="10" ry="7" fill="white" />
      <ellipse cx="95" cy="100" rx="10" ry="7" fill="white" />
      <ellipse cx="66" cy="101" rx="5.5" ry="5" fill="#3a2808" />
      <ellipse cx="96" cy="101" rx="5.5" ry="5" fill="#3a2808" />
      <ellipse cx="67" cy="100" rx="2" ry="2" fill="#111" />
      <ellipse cx="97" cy="100" rx="2" ry="2" fill="#111" />
      {/* 코 (특징적인) */}
      <path d="M76 108 Q80 120 84 108" stroke="#a07040" strokeWidth="2" fill="none" />
      <ellipse cx="80" cy="116" rx="7" ry="5" fill="#b08050" />
      {/* 입 */}
      <path d={mood === "determined" ? "M66 132 Q80 128 94 132" : "M66 132 Q80 136 94 132"} stroke="#6a3020" strokeWidth="2" fill="none" />
      {/* 머리카락 */}
      <ellipse cx="80" cy="68" rx="44" ry="28" fill="#1a0e04" />
      <path d="M38 82 Q30 115 36 150" stroke="#1a0e04" strokeWidth="14" fill="none" strokeLinecap="round" />
      <path d="M122 82 Q130 115 124 150" stroke="#1a0e04" strokeWidth="14" fill="none" strokeLinecap="round" />
      {/* 모자 */}
      <ellipse cx="80" cy="58" rx="46" ry="14" fill="#1a0e04" />
      <rect x="42" y="20" width="76" height="42" rx="4" fill="#1a0e04" />
    </svg>
  );
}

function CrowdSilhouette() {
  return (
    <svg viewBox="0 0 320 200" width="320" height="200">
      {[40,80,130,180,220,270].map((x, i) => (
        <g key={i}>
          <ellipse cx={x} cy={180 - (i % 2) * 15} rx="18" ry="22" fill="#0a0006" opacity="0.9" />
          <ellipse cx={x} cy={155 - (i % 2) * 15} rx="14" ry="16" fill="#0a0006" opacity="0.8" />
        </g>
      ))}
    </svg>
  );
}

// ── Anthropic Claude API ──────────────────────────────────────
const CLAUDE_MODEL = "claude-sonnet-4-6";

async function callClaude(systemPrompt, userPrompt) {
  const res = await fetch("https://api.anthropic.com/v1/messages", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "x-api-key": ANTHROPIC_API_KEY,
      "anthropic-version": "2023-06-01",
    },
    body: JSON.stringify({
      model: CLAUDE_MODEL,
      max_tokens: 1024,
      system: systemPrompt,
      messages: [{ role: "user", content: userPrompt }],
    }),
  });
  const data = await res.json();
  return data.content?.map((p) => p.text || "").join("") || "";
}

async function getPortiaResponse(sceneId, choiceText, evidenceQuote, dignity, confidence) {
  return callClaude(
    `당신은 베니스의 상인에서 법학 박사로 변장한 포샤입니다. 냉정하고 논리적이며 겉으로는 공정하지만 기독교 사회의 편을 듭니다. 한국어로 2~3문장, 법정 연설체로만 응답하세요.`,
    `장면: ${sceneId} | 샤일록 선택: "${choiceText}" | 증거: ${evidenceQuote || "없음"} | 존엄: ${dignity} 확신도: ${confidence}\n포샤의 반응:`
  );
}

async function getEnding(dignity, confidence, choices) {
  return callClaude(
    `당신은 베니스의 상인의 내레이터입니다. 샤일록의 비극을 담담하고 문학적으로 서술합니다. antisemitism 피해자로서 샤일록의 인간성을 중심에 두세요. 한국어로 3~4문장.`,
    `존엄: ${dignity}/100 | 확신도: ${confidence}/100 | 선택들: ${choices.join(", ")}\n엔딩을 서술하세요.`
  );
}

// ── 법정 배경 SVG ─────────────────────────────────────────────
function CourtroomBg() {
  return (
    <svg viewBox="0 0 800 300" width="100%" height="100%" style={{ position: "absolute", inset: 0, opacity: 0.7 }} preserveAspectRatio="xMidYMid slice">
      {/* 바닥 */}
      <rect width="800" height="300" fill="#0d0508" />
      {/* 뒷벽 */}
      <rect x="0" y="0" width="800" height="200" fill="#150a10" />
      {/* 판사석 */}
      <rect x="250" y="60" width="300" height="130" rx="4" fill="#1a0c14" stroke="#3a1a28" strokeWidth="2" />
      <rect x="270" y="40" width="260" height="30" rx="2" fill="#2a1420" />
      {/* 판사석 문양 */}
      <rect x="340" y="70" width="120" height="80" rx="2" fill="#120810" />
      <text x="400" y="118" textAnchor="middle" fill="#3a2030" fontSize="28" fontFamily="serif">⚖</text>
      {/* 창문 */}
      {[80, 640].map((x, i) => (
        <g key={i}>
          <rect x={x} y="20" width="80" height="140" rx="4" fill="#0a0614" stroke="#2a1828" strokeWidth="1.5" />
          <line x1={x + 40} y1="20" x2={x + 40} y2="160" stroke="#2a1828" strokeWidth="1" />
          <line x1={x} y1="90" x2={x + 80} y2="90" stroke="#2a1828" strokeWidth="1" />
          {/* 빛 */}
          <rect x={x} y="20" width="80" height="140" rx="4" fill="#3a2060" opacity="0.15" />
        </g>
      ))}
      {/* 기둥 */}
      {[180, 620].map((x, i) => (
        <rect key={i} x={x} y="0" width="24" height="220" fill="#1a0c18" stroke="#2a1828" strokeWidth="1" />
      ))}
      {/* 바닥선 */}
      <rect x="0" y="200" width="800" height="100" fill="#0d0508" />
      <line x1="0" y1="200" x2="800" y2="200" stroke="#2a1020" strokeWidth="2" />
      {/* 원근감 바닥 */}
      <path d="M0 200 L400 160 L800 200" fill="#110809" />
    </svg>
  );
}

// ── 메인 컴포넌트 ─────────────────────────────────────────────
export default function ShylockTrial() {
  const [phase, setPhase] = useState("title");
  const [sceneIdx, setSceneIdx] = useState(0);
  const [lineIdx, setLineIdx] = useState(0);
  const [dignity, setDignity] = useState(50);
  const [confidence, setConfidence] = useState(40);
  const [showChallenge, setShowChallenge] = useState(false);
  const [portiaReply, setPortiaReply] = useState("");
  const [loadingReply, setLoadingReply] = useState(false);
  const [choicesMade, setChoicesMade] = useState([]);
  const [endingText, setEndingText] = useState("");
  const [loadingEnding, setLoadingEnding] = useState(false);
  const [objection, setObjection] = useState(false); // "이의 있습니다!" 연출
  const [climaxMode, setClimaxMode] = useState(false);
  const [displayedText, setDisplayedText] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [evidenceModal, setEvidenceModal] = useState(null); // 증거 확대 표시
  const [portraitMood, setPortraitMood] = useState("neutral");
  const [shylockMood, setShylockMood] = useState("neutral");
  const typeRef = useRef(null);

  const scene = SCENES[sceneIdx];

  // 타이핑 애니메이션
  const typeText = (text) => {
    setIsTyping(true);
    setDisplayedText("");
    let i = 0;
    clearInterval(typeRef.current);
    typeRef.current = setInterval(() => {
      i++;
      setDisplayedText(text.slice(0, i));
      if (i >= text.length) {
        clearInterval(typeRef.current);
        setIsTyping(false);
      }
    }, 30);
  };

  useEffect(() => {
    if (phase === "game" && scene && lineIdx < scene.lines.length) {
      typeText(scene.lines[lineIdx]);
    }
  }, [sceneIdx, lineIdx, phase]);

  const nextScene = () => {
    setPortiaReply("");
    setClimaxMode(false);
    setPortraitMood("neutral");
    if (sceneIdx >= SCENES.length - 1) {
      setPhase("ending");
      setLoadingEnding(true);
      getEnding(dignity, confidence, choicesMade).then(t => {
        setEndingText(t);
        setLoadingEnding(false);
      });
    } else {
      setSceneIdx(s => s + 1);
      setLineIdx(0);
      setShowChallenge(false);
    }
  };

  const advance = () => {
    if (isTyping) {
      clearInterval(typeRef.current);
      setIsTyping(false);
      setDisplayedText(scene.lines[lineIdx]);
      return;
    }
    if (lineIdx < scene.lines.length - 1) {
      setLineIdx(l => l + 1);
    } else if (scene.challenge && !showChallenge && !portiaReply) {
      setShowChallenge(true);
    } else if (!scene.challenge && !portiaReply) {
      nextScene();
    }
  };

  const makeChoice = async (opt) => {
    const ev = opt.evidence ? EVIDENCE[opt.evidence] : null;
    setShowChallenge(false);

    // 이의 있습니다 연출
    if (ev) {
      setObjection(true);
      setEvidenceModal(ev);
      setTimeout(() => setObjection(false), 900);
      setTimeout(() => setEvidenceModal(null), 2200);
      await new Promise(r => setTimeout(r, 2200));
    }

    const newDig = Math.max(0, Math.min(100, dignity + opt.dignityChange));
    const newConf = Math.max(0, Math.min(100, confidence + opt.confidenceChange));
    setDignity(newDig);
    setConfidence(newConf);
    setChoicesMade(prev => [...prev, opt.text]);
    setShylockMood("determined");
    setPortraitMood("attack");

    if (opt.special === "climax") setClimaxMode(true);

    setLoadingReply(true);
    const reply = await getPortiaResponse(scene.id, opt.text, ev?.quote, newDig, newConf);
    setLoadingReply(false);
    setPortiaReply(reply);
    setPortraitMood(newConf > 50 ? "neutral" : "attack");
    setTimeout(() => setShylockMood("neutral"), 1000);
  };

  const dignityColor = dignity > 60 ? "#ffd700" : dignity > 30 ? "#ff8800" : "#ff4444";
  const confColor = confidence > 60 ? "#44ff88" : confidence > 30 ? "#44aaff" : "#ff4444";

  // ── 타이틀 ──────────────────────────────────────────────────
  if (phase === "title") return (
    <div style={{ minHeight: "100vh", background: "#08030a", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", fontFamily: "'Georgia', serif", padding: 24, gap: 0, position: "relative", overflow: "hidden" }}>
      <CourtroomBg />
      <div style={{ position: "relative", zIndex: 10, display: "flex", flexDirection: "column", alignItems: "center", gap: 28 }}>
        <div style={{ textAlign: "center" }}>
          <div style={{ color: "#6a2a3a", fontSize: 11, letterSpacing: 8, marginBottom: 14, textTransform: "uppercase" }}>The Merchant of Venice</div>
          <div style={{ color: "#ffd700", fontSize: 36, letterSpacing: 3, textShadow: "0 0 40px #ffd70070, 0 2px 0 #000", marginBottom: 6, fontWeight: "bold" }}>샤일록의 법정</div>
          <div style={{ color: "#7a5a4a", fontSize: 13, fontStyle: "italic" }}>당신은 유죄인가, 피해자인가.</div>
        </div>

        {/* 두 캐릭터 대치 */}
        <div style={{ display: "flex", alignItems: "flex-end", gap: 40, margin: "8px 0" }}>
          <div style={{ opacity: 0.9 }}><PortraitShylock mood="neutral" /></div>
          <div style={{ color: "#4a2030", fontSize: 28, marginBottom: 60, fontWeight: "bold", textShadow: "0 0 10px #ff000040" }}>VS</div>
          <div style={{ opacity: 0.9 }}><PortraitPortia mood="neutral" /></div>
        </div>

        <div style={{ background: "#0d0510cc", border: "1px solid #3a1a28", borderRadius: 6, padding: "14px 28px", maxWidth: 380, textAlign: "center", backdropFilter: "blur(4px)" }}>
          <div style={{ color: "#c8a080", fontSize: 13, lineHeight: 2 }}>
            베네치아, 1596년.<br />
            당신은 <span style={{ color: "#ffd700" }}>샤일록</span>이다.<br />
            계약은 유효하다. 하지만 이 법정은<br />
            처음부터 당신 편이 아니다.
          </div>
        </div>

        <button onClick={() => setPhase("game")} style={{
          background: "#8b0000", color: "#ffd700", border: "2px solid #ffd70060",
          padding: "14px 48px", borderRadius: 2, fontSize: 15, letterSpacing: 4,
          cursor: "pointer", fontFamily: "'Georgia', serif", fontWeight: "bold",
          boxShadow: "0 0 24px #8b000080", transition: "all 0.2s",
          textTransform: "uppercase",
        }}
        onMouseEnter={e => { e.currentTarget.style.background = "#aa0000"; e.currentTarget.style.boxShadow = "0 0 40px #cc0000a0"; }}
        onMouseLeave={e => { e.currentTarget.style.background = "#8b0000"; e.currentTarget.style.boxShadow = "0 0 24px #8b000080"; }}
        >법정에 서다</button>
      </div>
    </div>
  );

  // ── 엔딩 ────────────────────────────────────────────────────
  if (phase === "ending") {
    const won = dignity >= 60;
    return (
      <div style={{ minHeight: "100vh", background: "#08030a", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", fontFamily: "'Georgia', serif", padding: 32, gap: 24, position: "relative", overflow: "hidden" }}>
        <CourtroomBg />
        <div style={{ position: "relative", zIndex: 10, display: "flex", flexDirection: "column", alignItems: "center", gap: 20, textAlign: "center" }}>
          <div style={{ fontSize: 60 }}>{dignity >= 70 ? "⚖️" : dignity >= 40 ? "🕯️" : "💔"}</div>
          <div style={{ fontSize: 26, fontWeight: "bold", letterSpacing: 4, color: won ? "#ffd700" : "#c84040", textShadow: `0 0 20px ${won ? "#ffd70060" : "#cc000060"}` }}>
            {dignity >= 70 ? "존엄을 지켰다" : dignity >= 40 ? "그는 패했다" : "침묵만이 남았다"}
          </div>
          <div style={{ display: "flex", gap: 40, margin: "4px 0" }}>
            {[["존엄", dignity, dignityColor], ["확신도", confidence, confColor]].map(([label, val, color]) => (
              <div key={label} style={{ textAlign: "center" }}>
                <div style={{ color: "#5a4a3a", fontSize: 10, letterSpacing: 2, marginBottom: 4 }}>{label}</div>
                <div style={{ color, fontSize: 28, fontWeight: "bold" }}>{val}</div>
              </div>
            ))}
          </div>
          <div style={{ background: "#0d0510cc", border: "1px solid #3a1a28", borderRadius: 6, padding: 24, maxWidth: 480, backdropFilter: "blur(4px)" }}>
            {loadingEnding
              ? <div style={{ color: "#5a4a3a", fontStyle: "italic" }}>⚙️ 이야기를 마무리하는 중...</div>
              : <div style={{ color: "#c8a080", fontSize: 14, lineHeight: 2, fontStyle: "italic" }}>{endingText}</div>
            }
          </div>
          <button onClick={() => { setPhase("title"); setSceneIdx(0); setLineIdx(0); setDignity(50); setConfidence(40); setChoicesMade([]); setPortiaReply(""); setShowChallenge(false); setEndingText(""); }} style={{
            background: "transparent", color: "#5a4a3a", border: "1px solid #3a2a2a",
            padding: "10px 28px", borderRadius: 2, fontSize: 12, letterSpacing: 3,
            cursor: "pointer", fontFamily: "'Georgia', serif",
          }}>다시 법정에 서다</button>
        </div>
      </div>
    );
  }

  // ── 게임 화면 ────────────────────────────────────────────────
  return (
    <div style={{ height: "100vh", background: "#08030a", fontFamily: "'Georgia', serif", color: "#c8a080", display: "flex", flexDirection: "column", position: "relative", overflow: "hidden" }}>

      {/* "이의 있습니다!" 배너 */}
      {objection && (
        <div style={{
          position: "fixed", inset: 0, zIndex: 300,
          display: "flex", alignItems: "center", justifyContent: "center",
          background: "#00000060",
          animation: "fadeInOut 0.9s ease",
        }}>
          <div style={{
            background: "#cc0000", color: "white",
            fontSize: 42, fontWeight: "bold", letterSpacing: 4,
            padding: "16px 48px", borderRadius: 4,
            boxShadow: "0 0 60px #ff000080, inset 0 2px 0 #ff666660",
            border: "3px solid #ff444460",
            fontFamily: "'Georgia', serif",
            textShadow: "2px 2px 0 #660000",
            transform: "rotate(-2deg)",
          }}>이의 있습니다!</div>
        </div>
      )}
      <style>{`
        @keyframes fadeInOut { 0%{opacity:0;transform:scale(1.3) rotate(-2deg)} 20%{opacity:1;transform:scale(1) rotate(-2deg)} 80%{opacity:1} 100%{opacity:0} }
        @keyframes blink { 0%,100%{opacity:1} 50%{opacity:0} }
        @keyframes slideUp { from{transform:translateY(100%)} to{transform:translateY(0)} }
        @keyframes evidencePop { 0%{transform:scale(0.5);opacity:0} 60%{transform:scale(1.05)} 100%{transform:scale(1);opacity:1} }
      `}</style>

      {/* 클라이맥스 */}
      {climaxMode && (
        <div style={{ position: "fixed", inset: 0, background: "#000000d0", zIndex: 200, display: "flex", alignItems: "center", justifyContent: "center", padding: 24 }}>
          <div style={{ background: "#0d0208", border: "2px solid #ffd700", borderRadius: 6, padding: 32, maxWidth: 480, textAlign: "center", boxShadow: "0 0 60px #ffd70030" }}>
            <div style={{ color: "#6a3a2a", fontSize: 11, letterSpacing: 4, marginBottom: 14 }}>ACT III · SCENE 1</div>
            <div style={{ color: "#f0d090", fontSize: 14, lineHeight: 2.2, fontStyle: "italic", marginBottom: 20 }}>
              "Hath not a Jew eyes?<br />
              Hath not a Jew hands, organs, dimensions,<br />
              senses, affections, passions?<br /><br />
              If you prick us, do we not bleed?<br />
              If you tickle us, do we not laugh?<br />
              If you poison us, do we not die?<br />
              And if you wrong us, shall we not revenge?"
            </div>
            <div style={{ color: "#6a4a2a", fontSize: 11, marginBottom: 20, letterSpacing: 2 }}>— William Shakespeare</div>
            <button onClick={() => setClimaxMode(false)} style={{ background: "#8b0000", color: "#ffd700", border: "none", padding: "10px 28px", borderRadius: 2, cursor: "pointer", fontFamily: "'Georgia',serif", fontSize: 13, letterSpacing: 2 }}>계속</button>
          </div>
        </div>
      )}

      {/* 증거 확대 팝업 */}
      {evidenceModal && !objection && (
        <div style={{ position: "fixed", inset: 0, background: "#000000a0", zIndex: 250, display: "flex", alignItems: "center", justifyContent: "center" }}>
          <div style={{ background: "#100810", border: "2px solid #ffd700", borderRadius: 6, padding: 28, maxWidth: 400, animation: "evidencePop 0.3s ease", boxShadow: "0 0 40px #ffd70030" }}>
            <div style={{ display: "flex", gap: 12, alignItems: "center", marginBottom: 14 }}>
              <span style={{ fontSize: 36 }}>{evidenceModal.icon}</span>
              <div>
                <div style={{ color: "#ffd700", fontSize: 15, fontWeight: "bold" }}>{evidenceModal.name}</div>
                <div style={{ color: "#5a4a3a", fontSize: 10, letterSpacing: 2 }}>{evidenceModal.act}</div>
              </div>
            </div>
            <div style={{ color: "#d4b060", fontSize: 13, fontStyle: "italic", lineHeight: 1.8, borderLeft: "2px solid #ffd70040", paddingLeft: 12 }}>"{evidenceModal.quote}"</div>
          </div>
        </div>
      )}

      {/* 법정 배경 + 캐릭터 영역 */}
      <div style={{ flex: 1, position: "relative", minHeight: 0, overflow: "hidden" }}>
        <CourtroomBg />

        {/* 장면 진행도 */}
        <div style={{ position: "absolute", top: 8, left: 0, right: 0, display: "flex", gap: 3, padding: "0 12px", zIndex: 10 }}>
          {SCENES.map((s, i) => (
            <div key={s.id} style={{ flex: 1, height: 3, borderRadius: 2, background: i <= sceneIdx ? "#8b0000" : "#2a1020", transition: "background 0.3s" }} />
          ))}
        </div>

        {/* 상단 미터 */}
        <div style={{ position: "absolute", top: 16, left: 12, right: 12, display: "flex", gap: 12, zIndex: 10 }}>
          {[["존엄 DIGNITY", dignity, dignityColor], ["법정 확신도", confidence, confColor]].map(([label, val, color]) => (
            <div key={label} style={{ flex: 1, background: "#08030acc", borderRadius: 3, padding: "6px 10px", border: "1px solid #2a1020" }}>
              <div style={{ display: "flex", justifyContent: "space-between", fontSize: 9, letterSpacing: 1, marginBottom: 3 }}>
                <span style={{ color: "#5a3a4a" }}>{label}</span>
                <span style={{ color }}>{val}</span>
              </div>
              <div style={{ background: "#1a0814", height: 5, borderRadius: 2 }}>
                <div style={{ width: `${val}%`, height: "100%", background: `linear-gradient(90deg,${color}80,${color})`, borderRadius: 2, transition: "width 0.5s", boxShadow: `0 0 6px ${color}60` }} />
              </div>
            </div>
          ))}
        </div>

        {/* 캐릭터 스프라이트 */}
        <div style={{ position: "absolute", bottom: 0, left: 0, right: 0, display: "flex", justifyContent: "space-between", alignItems: "flex-end", padding: "0 16px", zIndex: 5 }}>
          {/* 샤일록 (왼쪽, 항상) */}
          <div style={{ opacity: scene.speaker === "NARRATOR" ? 0.5 : 1, transition: "opacity 0.3s", filter: scene.speaker === "PORTIA" || scene.speaker === "CROWD" ? "brightness(0.5)" : "brightness(1)" }}>
            <PortraitShylock mood={shylockMood} />
          </div>

          {/* 상대방 (오른쪽) */}
          <div style={{ opacity: scene.speaker === "NARRATOR" ? 0.3 : 1, transition: "opacity 0.3s", filter: scene.speaker === "PORTIA" || scene.speaker === "CROWD" ? "brightness(1)" : "brightness(0.5)" }}>
            {scene.speaker === "CROWD"
              ? <CrowdSilhouette />
              : <PortraitPortia mood={portraitMood} />
            }
          </div>
        </div>
      </div>

      {/* 하단 텍스트박스 (역전재판 스타일) */}
      <div style={{ background: "#08030a", borderTop: "3px solid #3a1028", flexShrink: 0, animation: "slideUp 0.2s ease" }}>
        {/* 화자 이름 탭 */}
        <div style={{ display: "flex", alignItems: "center", borderBottom: "1px solid #2a1020" }}>
          <div style={{
            background: scene.speaker === "PORTIA" ? "#2a0820" : scene.speaker === "NARRATOR" ? "#1a1428" : "#200a08",
            border: "1px solid #3a1028", borderBottom: "none",
            padding: "5px 18px", fontSize: 11, letterSpacing: 3,
            color: scene.speaker === "PORTIA" ? "#c0a060" : scene.speaker === "NARRATOR" ? "#6a5a8a" : "#aa6040",
            marginLeft: 12, borderRadius: "4px 4px 0 0",
          }}>
            {scene.speaker === "PORTIA" ? "PORTIA · 판사" : scene.speaker === "NARRATOR" ? "NARRATOR" : "군중"}
          </div>
        </div>

        {/* 대사 영역 */}
        <div onClick={advance} style={{ padding: "14px 20px 8px", minHeight: 72, cursor: "pointer", position: "relative" }}>
          {/* 포샤 AI 반응 */}
          {portiaReply ? (
            <div>
              <div style={{ fontSize: 10, color: "#5a3a4a", letterSpacing: 2, marginBottom: 6 }}>⚖️ PORTIA의 반응</div>
              {loadingReply
                ? <div style={{ color: "#5a4a3a", fontStyle: "italic", fontSize: 13 }}>포샤가 반응하고 있다...</div>
                : <div style={{ fontSize: 14, lineHeight: 1.8, color: "#c0a060", fontStyle: "italic" }}>{portiaReply}</div>
              }
            </div>
          ) : (
            <div style={{ fontSize: 15, lineHeight: 1.8, color: scene.speaker === "NARRATOR" ? "#6a5a7a" : "#e8d0a0" }}>
              {displayedText}
              {isTyping && <span style={{ animation: "blink 0.7s infinite", color: "#ffd700" }}>▌</span>}
            </div>
          )}
          {/* 화살표 */}
          {!isTyping && !showChallenge && (
            <div style={{ position: "absolute", bottom: 8, right: 16, color: "#4a2a38", fontSize: 12, animation: "blink 1s infinite" }}>▼</div>
          )}
        </div>

        {/* 선택지 영역 */}
        {showChallenge && scene.challenge && !portiaReply && (
          <div style={{ borderTop: "1px solid #2a1020", padding: "10px 12px 12px" }}>
            <div style={{ fontSize: 10, color: "#5a3a4a", letterSpacing: 2, marginBottom: 8, paddingLeft: 4 }}>▶ 샤일록의 선택</div>
            <div style={{ fontSize: 12, color: "#7a5a6a", fontStyle: "italic", marginBottom: 8, paddingLeft: 4 }}>{scene.challenge.text}</div>
            <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
              {scene.challenge.options.map((opt, i) => {
                const ev = opt.evidence ? EVIDENCE[opt.evidence] : null;
                return (
                  <button key={opt.id} onClick={() => makeChoice(opt)} style={{
                    background: "#100510", border: "1px solid #3a1828",
                    color: "#e0c090", padding: "9px 14px", borderRadius: 2,
                    cursor: "pointer", textAlign: "left", fontSize: 13,
                    fontFamily: "'Georgia', serif", lineHeight: 1.5,
                    display: "flex", justifyContent: "space-between", alignItems: "center",
                    transition: "all 0.15s",
                  }}
                  onMouseEnter={e => { e.currentTarget.style.background = "#1a0820"; e.currentTarget.style.borderColor = "#ffd70050"; }}
                  onMouseLeave={e => { e.currentTarget.style.background = "#100510"; e.currentTarget.style.borderColor = "#3a1828"; }}
                  >
                    <span><span style={{ color: "#5a3a4a" }}>{i + 1}. </span>{opt.text}</span>
                    {ev && <span style={{ color: "#8b6040", fontSize: 11, marginLeft: 8, flexShrink: 0 }}>{ev.icon} {ev.name}</span>}
                  </button>
                );
              })}
            </div>
          </div>
        )}

        {/* 다음 장면 버튼 */}
        {portiaReply && !loadingReply && (
          <div style={{ padding: "8px 12px 12px" }}>
            <button onClick={nextScene} style={{
              width: "100%", background: "#1a0810", color: "#c0a060",
              border: "1px solid #4a1828", padding: "10px", borderRadius: 2,
              cursor: "pointer", fontFamily: "'Georgia', serif", fontSize: 12,
              letterSpacing: 3, transition: "all 0.15s",
            }}
            onMouseEnter={e => { e.currentTarget.style.background = "#2a0c18"; }}
            onMouseLeave={e => { e.currentTarget.style.background = "#1a0810"; }}
            >▶ 다음 장면</button>
          </div>
        )}

        {/* 증거 목록 (하단 고정) */}
        {scene.availableEvidence?.length > 0 && !showChallenge && !portiaReply && (
          <div style={{ borderTop: "1px solid #1a0814", padding: "8px 12px", display: "flex", gap: 8, overflowX: "auto" }}>
            {scene.availableEvidence.map(id => {
              const ev = EVIDENCE[id];
              return (
                <button key={id} onClick={() => setEvidenceModal(evidenceModal?.id === id ? null : ev)} style={{
                  background: evidenceModal?.id === id ? "#2a1020" : "#100510",
                  border: `1px solid ${evidenceModal?.id === id ? "#ffd70060" : "#2a1020"}`,
                  borderRadius: 3, padding: "5px 10px",
                  cursor: "pointer", display: "flex", alignItems: "center", gap: 5,
                  color: "#8b6040", fontSize: 11, fontFamily: "'Georgia', serif",
                  flexShrink: 0, transition: "all 0.15s",
                }}>
                  <span>{ev.icon}</span><span>{ev.name}</span>
                </button>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
