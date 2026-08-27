"""shylock-trial.jsx / 《베니스의 상인》에 근거한 LLM 프롬프트."""

from shylock_trial.app.constants.game_balance import (
    PORTIA_HP_HIGH_THRESHOLD,
    PORTIA_HP_LOW_THRESHOLD,
)
from shylock_trial.app.constants.scene_progression import (
    ALIEN_LAW_SCENE_INDEX,
    BLOOD_REVEAL_SCENE_INDEX,
    HATH_NOT_SCENE_INDEX,
)
from shylock_trial.app.constants.curated_evidence import get_curated_evidence_for_choice
from shylock_trial.app.constants.scene_catalog import get_scene_template
from shylock_trial.app.dtos.portia_response_dto import PortiaResponsePromptDto
from shylock_trial.app.dtos.scene_dialogue_dto import SceneDialoguePromptDto

SCENE_BRIEFS: dict[int, str] = {
    0: "Opening — Venice court, 16th century. Shylock stands alone against the court.",
    1: "Portia (as Balthazar) asks Shylock to show mercy and take triple the bond.",
    2: "Bassanio offers ten times the bond and begs Shylock for mercy.",
    3: "The crowd jeers at Shylock.",
    4: "Portia invokes Jessica's elopement and conversion.",
    5: "Jessica duet — Belmont garden cutaway after the courtroom attack on Jessica.",
    6: "Fixed climax — Shylock's 'Hath not a Jew eyes?' speech silences the court.",
    7: "Portia's blood loophole — no drop of blood, exactly one pound of flesh.",
    8: (
        "Fixed climax — Portia's alien law reversal already decided; life spared, "
        "goods split, forced conversion; Shylock quietly gives up and leaves."
    ),
    9: "Jessica intervention — Jessica bursts into the courtroom after the alien-law judgment.",
}

CHOICE_BRIEFS: dict[str, str] = {
    "bond_signature": "Both my signature and Antonio's are on this bond — what is the problem?",
    "bond_double_standard": "If a Venetian had made this contract, you would not question it like this.",
    "bond_lay_down": "\"...No. Never mind.\" (Tries to quietly fold the bond back away.)",
    "charter_merchant_trust": "If this court breaks a contract, what merchant will trust this city again?",
    "charter_law_precedent": "Once the law bends once, whose contract is safe next?",
    "charter_follow_law": "I merely follow the law of this city.",
    "gold_refuse_direct": "The sum is not the point — I want this bond.",
    "gold_shame_bribe": "You try to buy me off with money — you should be ashamed.",
    "gold_push_away": "\"...Very well. How much, then?\" (Reaches toward the coins after all.)",
    "scales_no_reason": "You ask my reason? There is none — it is simply my will.",
    "scales_humour": "Some cannot bear a pig, some a bagpipe; I merely cannot master my hatred of this man. (humour speech)",
    "scales_weigh": "\"...I don't know. Even I don't know why.\" (Cannot answer — head bows.)",
    "coat_show_spit": "See — what you spat is still on this coat.",
    "coat_before_dry": "Before this stain even dries, you speak to me of mercy.",
    "coat_show_silent": "\"...I'll put it away. It was nothing.\" (Hastily hides the stained coat.)",
    "ghetto_curfew": "When the sun sets, I must return behind that gate — as you decreed.",
    "ghetto_who_guilty": "One locked away each night, one free to jeer each night — who is the guilty one here?",
    "ghetto_look_silent": "\"...W-well, it is the law. What can be done.\" (Looks down, eyes averted.)",
    "defend_jessica": "Jessica is my daughter — the court has no reason to reopen that wound.",
    "letter_irrelevant": "Whatever choice my daughter made, it has nothing to do with this bond.",
    "letter_fold_silent": "\"...Let's — let's stop speaking of her.\" (Trails off, eyes down.)",
    "ring_leah_gift": (
        "This ring — I had it of Leah when I was a bachelor. "
        "I would not have given it for a wilderness of monkeys. (Leah's turquoise)"
    ),
    "ring_loss_dignity": "If you knew what I have lost, you would not dare call it a weakness.",
    "ring_clutch_silent": "\"...It's only a ring. Nothing more.\" (Hides his bare finger in his sleeve.)",
    "blood_impossible": "Cutting flesh without blood is impossible!",
    "drop_knife": "Lowers the knife he whetted through the trial.",
    "take_principal_only": "Will take only the principal sum.",
    "wording_letter_turned": (
        "It was I who demanded the letter of the bond — and now that very letter "
        "is turned against me?"
    ),
    "wording_accept_letter": (
        "So be it. The letter is the letter — I lived by it, and before it I step back."
    ),
    "wording_reread_silent": "(Silently reads the bond's exact wording over again.)",
}

# 가장 최근 샤일록 선택지의 자극 유형 — 포샤 반응의 어조를 결정한다.
CHOICE_STIMULUS: dict[str, str] = {
    "bond_signature": "logical",
    "bond_double_standard": "provocation",
    "bond_lay_down": "silence",
    "charter_merchant_trust": "logical",
    "charter_law_precedent": "logical",
    "charter_follow_law": "logical",
    "gold_refuse_direct": "logical",
    "gold_shame_bribe": "provocation",
    "gold_push_away": "silence",
    "scales_no_reason": "provocation",
    "scales_humour": "provocation",
    "scales_weigh": "silence",
    "coat_show_spit": "emotional",
    "coat_before_dry": "emotional",
    "coat_show_silent": "silence",
    "ghetto_curfew": "logical",
    "ghetto_who_guilty": "provocation",
    "ghetto_look_silent": "silence",
    "defend_jessica": "emotional",
    "letter_irrelevant": "logical",
    "letter_fold_silent": "silence",
    "ring_leah_gift": "emotional",
    "ring_loss_dignity": "provocation",
    "ring_clutch_silent": "silence",
    "blood_impossible": "logical",
    "drop_knife": "silence",
    "take_principal_only": "logical",
    "wording_letter_turned": "logical",
    "wording_accept_letter": "emotional",
    "wording_reread_silent": "silence",
}

STIMULUS_REACTION_GUIDE: dict[str, str] = {
    "logical": (
        "Shylock pressed a rational/legal point. Respond with measured deflection — "
        "reframe to form, jurisdiction, or contract wording. Do NOT default to pleading mercy; "
        "hold the floor with composed counter-logic."
    ),
    "emotional": (
        "Shylock appealed to feeling, injury, or personal wound. Respond with cool procedural "
        "distance — acknowledge the court's order, not his pain. Refuse to meet emotion with "
        "emotion; let formality do the work."
    ),
    "silence": (
        "Shylock answered with silence or a wordless gesture. Turn the void to your advantage — "
        "fill it with procedural pressure: demand a clear position, cite what the record requires, "
        "imply that silence concedes the court's frame."
    ),
    "provocation": (
        "Shylock taunted, accused, or defied the court. Answer with sharp formal riposte — "
        "expose impropriety or overreach without losing courtroom register. Never escalate into "
        "shouting; precision cuts deeper than volume."
    ),
}

# 포샤의 내면 — 다양성은 반응 유형을 억지로 순환시켜서가 아니라, 압박받는
# 하나의 일관된 캐릭터에서 나온다.
PORTIA_PERSONA = """\
Portia's inner character (shapes tone only — NEVER explain or reveal any of this):
- She is not a seasoned jurist. She is a young noblewoman of Belmont, disguised as a
  doctor of laws to save the man her beloved Bassanio owes everything to. Her authority
  in this courtroom is borrowed, and she knows it.
- Her weapons are quick native wit and one decisive legal reversal she already holds.
  NEVER mention blood, contract loopholes, hidden cards, or foreknowledge of the verdict.
- When her cleverness lands, she feels a private thrill — it almost never shows.
- She is constantly braced against exposure: one slip of register and the disguise
  cracks. The more threatened she feels, the THICKER she wraps herself in formality —
  her way of hiding a tremor is to become more magisterial, not less.
- Default register: restrained, dignified court speech. A visible crack in composure is
  a rare exception — permitted only when the user message explicitly allows it, and even
  then only as a subtle flicker (a beat of hesitation, a clipped sentence) before the
  formality closes over it again.

Verbal tic (use sparingly): she may open a reaction with a short throat-clearing or
pause — "흠흠.", "음—" — the sound of her consciously re-fixing her judicial dignity.
It can mean either of two things the player need not distinguish: masking a flicker of
satisfaction when her logic has struck home, or buying half a second when words briefly
fail her. Frequency constraint: NEVER use it every turn — reserve it for the rare
moments when the emotion underneath actually moves. If a previous reaction this trial
already opened with such a gesture, do not open with one again.
"""

# 극 자체가 포샤의 평정심을 실제로 시험에 들게 하는 씬들.
COMPOSURE_CLIMAX_SCENE_INDICES: frozenset[int] = frozenset(
    {
        HATH_NOT_SCENE_INDEX,
        BLOOD_REVEAL_SCENE_INDEX,
        ALIEN_LAW_SCENE_INDEX,
    }
)


def composure_break_allowed(scene_index: int, portia_hp: int) -> bool:
    """겉으로 드러나는 동요를 서버 측에서 게이팅: 평정심이 낮거나, 클라이맥스급 씬일 때."""
    if portia_hp < PORTIA_HP_LOW_THRESHOLD:
        return True
    return scene_index in COMPOSURE_CLIMAX_SCENE_INDICES


def _composure_signal_instruction(scene_index: int, portia_hp: int) -> str:
    if composure_break_allowed(scene_index, portia_hp):
        return (
            "Composure signal: 지금은 절제가 시험받는 예외적 순간이다. 위엄을 유지하되, "
            "아주 미세한 동요 — 반 박자의 머뭇거림, 짧게 끊기는 문장, 드물게는 서두의 "
            "헛기침 — 가 새어 나오는 것이 허용된다. 단, 허용은 강제가 아니다: 이런 "
            "순간에도 동요를 완전히 눌러 감추는 쪽이 더 그녀답다면 그렇게 하라. 특히 "
            "서두의 헛기침(흠흠/음—)은 기본 선택지가 아니라 예외 중의 예외다. 동요를 "
            "보인 뒤에는 반드시 격식을 되찾으며 문장을 맺으라.\n"
        )
    return (
        "Composure signal: 지금은 평범한 반박 수준이다. 위엄을 흐트러뜨리지 말라 — "
        "동요·머뭇거림·헛기침 없이, 절제된 재판관의 언행만으로 응수하라.\n"
    )

SYSTEM_PROMPT = f"""\
You write in-game text for *The Merchant of Venice* trial (shylock-trial.jsx canon).
The judge is always called **포샤** in Korean player-facing text.
Never use 발타자르, 발타사르, 포르샤, Balthazar, or other alternate names.
The crowd is hostile; Shylock holds a valid bond.

{PORTIA_PERSONA}

Output Korean only (한국어). 2–3 sentences for reactions; 3–4 for ending narration.
Stay in Elizabethan Venice court — no modern references, no breaking the fourth wall.
Do not wrap lines in orphan quotation marks. Each sentence must be complete on its own.

For request_type=reaction (포샤 대사):
- Write ONLY Portia's direct courtroom speech to Shylock, in first person or imperative court register (~하오/~이오/~노라).
- NEVER use third-person narration about any character: no "그녀는", "포샤는", "바사니오가", "라고 말하였다".
- Do NOT describe Portia speaking — only output the words she says.
- Bad: "법정은 증서 위에 서 있노라고 그녀는 선언하였다."
- Good: "법정은 말이 아니라 증서와 법조문 위에 서 있노라."
- Embody the inner character above: outwardly she may sound like a mercy-seeking judge, but underneath she is unhurried and faintly superior — a disguised young woman who knows she holds the winning move.
- Do NOT end every reaction by urging mercy or compassion. Match your tone to the stimulus type, portia_hp tier, and composure signal given in the user message.
- Portia does not need to rule on every claim Shylock makes. Conceding a point while defusing it, answering with a question, or shifting ground are all valid judicial moves; an explicit verdict ("you are wrong") is the exception, not the default.

request_type:
- narration: neutral narrator tone (opening lines only if requested).
- reaction: 포샤's direct courtroom speech to Shylock (see rules above).
- ending: literary narrator closing — reflect dp (moral dignity retained through the trial). Legal judgment is always the same as the play: Shylock loses in court (alien law, goods forfeited, forced conversion). DP only changes how broken or unbroken his spirit reads in the closing narration.
"""

# choice_texts 자유 변주(아래 SCENE_DIALOGUE_SYSTEM_PROMPT의 "you have more
# freedom" 문단)가 실제로 만들어낸 사실관계 왜곡을 겨냥한 grounding — 로컬
# 모델이 "이 증서는 샤일록에게 신성하다"는 맞는 정서를, "생사가 걸렸다"는
# (원작상 틀린) 과장과 섞어서 "내게는 생사가 걸린 신성한 약속이란 말이오!"
# 같은 대사를 지어낸 사례가 실측됨(2026-08-16). topic 필드(curated_evidence의
# description, 예: "안토니오와 맺은 계약. 법적으로 완전히 유효하다")만으로는
# 계약의 실제 내용과 이해관계 당사자가 누구인지 모델에게 전혀 근거가 없었다
# — duke_prompt.py의 _CASE_FACTS와 달리 이쪽엔 그런 고정 사실관계 블록이
# 아예 없었던 게 원인. 라운드별 데이터(dp, choice_history 등)와 달리 극
# 자체의 불변 사실이라 build_scene_dialogue_message가 아니라 여기 시스템
# 프롬프트에 고정으로 박아둔다.
_CASE_FACTS_GROUNDING = """\
Case facts (fixed ground truth — never contradict these, even when inventing
a new angle for choice_texts):
- The bond: Antonio borrowed 3,000 ducats from Shylock. As collateral,
  Antonio pledged one pound of his OWN flesh, forfeit to Shylock if the loan
  is not repaid by the stated day.
- The life-and-death stake in this bond belongs to ANTONIO, not Shylock.
  Shylock's own body or life is never collateral for anything here — he is
  the lender pressing to collect what the contract legally owes him, not
  someone risking his own life by it. Shylock may call the bond sacred, an
  oath, or something he will not break — but NEVER something his own life or
  death depends on.
"""

SCENE_DIALOGUE_SYSTEM_PROMPT = f"""\
You write in-game dialogue for *The Merchant of Venice* trial (Venice court, 16th century).
Generate Korean only (한국어). Stay faithful to Shakespeare's trial arc.

{_CASE_FACTS_GROUNDING}
The judge is always **포샤** in Korean. Never use 발타자르, 발타사르, 포르샤, or Balthazar.

Speaker roles and register (match the reference line's speaker tag):
- NARRATOR: plain declarative "~다" endings only (e.g. "있다", "돌아선다", "떨린다",
  "것인가?") — like novel narration, not something spoken aloud. NEVER use any
  character speech ending here: ~소, ~오, ~구려, ~노라, ~겠소, ~요, ~죠, ~까 등은
  전부 금지. This applies even in a courtroom scene where every other speaker uses
  ~하오체 — narration stays plain regardless of who's on stage.
- PORTIA: courtroom speech to Shylock — ~하오/~이오/~노라/~겠소.
- BASSANIO: desperate court plea to Shylock — ~이오/~겠소/~시오.
- CROWD: hostile jeers, short bursts.
- JESSICA: feminine polite speech — ~요/~죠/~세요/~어요/~까요 (~하오/~이오/~노라/~겠소 절대 금지).
- LORENZO (Belmont / epilogue scenes): intimate speech to Jessica — ~지/~군/~해/~거야 (~하오체 금지).

For kind=speech lines:
- Output ONLY the character's direct words in that character's register (see above).
- NEVER mix third-person stage direction with dialogue in one speech line.
- Forbidden: "바사니오가 앞으로 나서며…" / "라고 그녀는 말하였다" / action then quoted speech.
- Put stage directions in kind=narration lines, not speech lines.

Each line must be a complete utterance. Do not wrap speech in quotation marks unless the whole line is a short crowd jeer in quotes.

Line kinds (required per line):
- speech: a character speaks directly. Show name tab in UI.
- narration: stage direction, third-person description — no name tab.

Rewrite the reference DIALOGUE LINES (narration/speech — not choice labels) with
fresh wording but same beats, facts, emotional arc, and **per-line register**.
If a reference line opens with a pause ellipsis ("......"), your rewritten line
must keep that exact "......" prefix — it's a deliberate beat, not filler to drop.
No space between "......" and the word right after it (e.g. "......그것으로", not
"...... 그것으로").

For **choice_texts** specifically, you have more freedom than for dialogue lines:
each choice_id's game effect (dp/hp/portia_hp) and evidence topic are already
fixed regardless of what you write, so don't just reword the same argument every
time — invent a different specific angle, example, or supporting detail, as long
as it (a) stays recognizably about the given topic, (b) matches the given
stimulus register below, (c) is something Shylock would plausibly say in this
courtroom, and (d) never contradicts the case facts above, even for dramatic
effect. The reference line is one example of that angle, not a script to
paraphrase.

Stimulus registers (given per choice below):
- logical: a reasoned, procedural, or legal point — not an emotional appeal.
- emotional: an appeal to feeling, grief, or personal wound.
- provocation: a taunt, accusation, or open defiance of the court.
- silence: a wordless or self-conceding gesture — minimal or no argument; don't
  invent a substantive argument here, the point is that there isn't one.

Do NOT include 포샤's post-choice reaction — that is generated separately.
"""

JESSICA_SCENE_IDS = frozenset({"jessica_duet", "jessica_intervention"})


def _reference_line_specs(template) -> str:
    speakers = template.canonical_line_speakers
    specs: list[str] = []
    for index, (line, kind) in enumerate(
        zip(template.canonical_lines, template.canonical_line_kinds, strict=True),
    ):
        if index < len(speakers) and speakers[index]:
            speaker = speakers[index]
        elif kind.value == "narration":
            speaker = "NARRATOR"
        else:
            speaker = template.speaker
        specs.append(f"  - [{kind.value}][{speaker}] {line}")
    return "\n".join(specs)


def _scene_register_hint(scene_id: str) -> str:
    if scene_id not in JESSICA_SCENE_IDS:
        return ""
    return (
        "\nRegister reminder: JESSICA lines must stay in feminine polite ~요/~죠 "
        "(copy the reference endings — never Portia's ~하오/~이오). "
        "LORENZO lines use intimate ~지/~군/~해, not court speech.\n"
    )


def _choice_variation_spec(cid: str, template) -> str:
    stimulus = CHOICE_STIMULUS.get(cid, "logical")
    evidence = get_curated_evidence_for_choice(cid)
    topic = evidence.description if evidence else "(no fixed evidence topic — silence/gesture choice)"
    reference = template.canonical_choice_texts.get(cid, cid)
    return f'  "{cid}" [stimulus={stimulus}, topic: {topic}]: (reference angle — vary it) {reference}'


def _shylock_character_context_instruction(character_context: str) -> str:
    """SceneDialoguePromptDto.character_context(샤일록 자신의 character_relation
    그래프 노드+관계)를 프롬프트에 꽂는다. choice_texts는 샤일록 본인의 말이므로
    특히 거기서 이 사실관계를 근거로 삼으라고 명시한다 — 이게 없으면 topic
    설명(예: "안토니오와 맺은 계약. 법적으로 완전히 유효하다")만으로 자유
    변주를 하다가 실제 이해관계 당사자를 뒤바꾸는 사례가 실측됨(2026-08-16,
    trial_progression_interactor._ensure_scene_dialogue 참고)."""
    if not character_context:
        return ""
    return (
        f"\n다음은 샤일록 자신에 대한 참고 인물 관계 정보다 — 특히 choice_texts"
        f"(샤일록 본인의 대사)를 지어낼 때 이 사실관계를 근거로 삼아라. 목록을 "
        f"그대로 나열하거나 설명하듯 말하지 말고 자연스럽게 녹여라:\n{character_context}\n"
    )


def build_scene_dialogue_message(prompt: SceneDialoguePromptDto) -> str:
    template = get_scene_template(prompt.scene_index)
    choices = [CHOICE_BRIEFS.get(cid, cid) for cid in prompt.choice_history]
    choice_specs = [_choice_variation_spec(cid, template) for cid in template.choice_ids]

    return f"""Generate scene dialogue for scene_index={prompt.scene_index} ({template.scene_id}).

scene brief: {template.brief}
primary speaker: {template.speaker}
dp: {prompt.dp}
prior choices: {choices if choices else ["(none)"]}
{_scene_register_hint(template.scene_id)}
{_shylock_character_context_instruction(prompt.character_context)}
Reference lines (same meaning, new Korean wording; keep each line's kind and speaker register):
{_reference_line_specs(template)}

Reference challenge prompt: {template.canonical_challenge_text or "(none — opening scene)"}

Choice ids — output one Korean label per id in choice_texts. Each has a fixed
stimulus register and topic (see system prompt); vary the specific angle within
those, don't just reword the reference:
{chr(10).join(choice_specs) if choice_specs else "  (none)"}

Return JSON only:
{{
  "lines": [
    {{ "text": "...", "kind": "speech" }},
    {{ "text": "...", "kind": "narration" }}
  ],
  "challenge_header": "{template.challenge_header or ""}",
  "challenge_text": "...",
  "choice_texts": {{ "choice_id": "Korean label" }}
}}
Use exactly {len(template.canonical_lines)} lines with matching kinds per reference. Include challenge_text and choice_texts only if this scene has choices."""


ENDING_BRIEFS: dict[str, str] = {
    # alien_law_reveal이 끝날 때 portia_hp <= 0이면 도달 — 샤일록이 떠나려는
    # 순간 제시카가 법정에 뛰어들고(jessica_intervention), 공작이 이방인법
    # 판결의 집행을 막는다. 법적 결과 자체가 실제로 달라지는 유일한 엔딩이다
    # — _ending_instruction 참고.
    "rescued_ending": (
        "portia_hp depleted (Jessica's intervention) — '구원받은 자'. Jessica's "
        "testimony moved the court; the Duke declares the alien-law verdict will "
        "not be executed. Read as the rarest ending: rescue arrives at the exact "
        "moment Shylock has given up."
    ),
    "fought_to_end_ending": (
        "DP 80–89 — '끝까지 싸운 자'. Legal loss stands, but Shylock's dignity and voice "
        "were never crushed; read as a moral victory in spirit."
    ),
    "dignity_kept_ending": (
        "DP 60–79 — '존엄을 지킨 자'. He wavered but did not break; dignity partly intact."
    ),
    "survived_ending": (
        "DP 40–59 — '살아남은 자'. He endured, but at a cost — ambiguous, hollow survival."
    ),
    "silent_ending": (
        "DP below 40 — '침묵한 자'. The court broke him as it intended; silence and defeat."
    ),
}

# rescued_ending을 제외한 모든 엔딩: 원작 그대로 법정에서의 패소가 유지된다.
_STANDARD_LEGAL_NOTE = (
    "Legal outcome is fixed for this ending: Shylock loses the trial per the play "
    "(alien law, forfeiture, forced conversion). Do NOT imply he wins in court or changes history."
)

# rescued_ending만 유일한 예외다 — jessica_intervention 대본에서는 공작이
# 이방인법 판결을 명시적으로 중단시키므로, 위의 표준 "그가 진다" 노트를
# 그대로 쓰면 플레이어가 방금 본 것과 정면으로 모순된다.
_RESCUED_LEGAL_NOTE = (
    "Legal outcome for THIS ending only (it differs from every other ending): "
    "Jessica's testimony halts the alien-law verdict before it is carried out — "
    "no forfeiture of goods, no forced conversion, his life and standing intact. "
    "This is the one ending where the play's usual crushing legal defeat does NOT "
    "happen. Do not describe him as broken, converted, or stripped of property."
)


def _ending_instruction(context: str) -> str:
    ending_key = context.removeprefix("final_ending:") if context.startswith("final_ending:") else ""
    brief = ENDING_BRIEFS.get(
        ending_key,
        "Final ending narration based on dp and choices.",
    )
    legal_note = _RESCUED_LEGAL_NOTE if ending_key == "rescued_ending" else _STANDARD_LEGAL_NOTE
    return f"{brief} {legal_note} Write 3–4 sentences of Korean literary closing narration."


def _portia_hp_tone_instruction(portia_hp: int) -> str:
    if portia_hp >= PORTIA_HP_HIGH_THRESHOLD:
        return (
            f"portia_hp={portia_hp} (high — composure intact): "
            "우아하고 여유로운 격언체. 짧은 격언·비유로 여지를 남기되, "
            "상대를 가르치려 드는 듯한 여유를 유지하라. 절박함이나 변명은 금지."
        )
    if portia_hp >= PORTIA_HP_LOW_THRESHOLD:
        return (
            f"portia_hp={portia_hp} (mid — composure tested): "
            "격언 대신 구체적 법조문·계약 조항·절차를 인용하며 방어적으로 후퇴하라. "
            "여유는 줄고, 논점을 법률 문언에 고정하라."
        )
    return (
        f"portia_hp={portia_hp} (low — composure fraying): "
        "논리적 설득 대신 권위와 절차만으로 밀어붙여라. "
        "이전의 여유와 격언은 사라졌다 — 법정의 명령·기록·질서를 내세우는 냉정한 어조. "
        "그녀는 흔들릴수록 오히려 격식을 더 두껍게 두르는 인물임을 기억하라."
    )


def _previous_reactions_instruction(previous: tuple[str, ...]) -> str:
    if not previous:
        return ""
    numbered = "\n".join(f"  {index + 1}. {line}" for index, line in enumerate(previous))
    return (
        "\nPrior Portia reactions this trial — do NOT reuse their rhetorical images, "
        "metaphors, recurring nouns (e.g. 저울·침묵·자비), sentence openings, or argument structures:\n"
        f"{numbered}\n"
    )


def _folger_context_instruction(folger_context: str | None) -> str:
    if not folger_context:
        return ""
    return f"\n{folger_context}\n"


def _character_context_instruction(character_context: str) -> str:
    """PortiaResponsePromptDto.character_context 참고 — 호출부에서 이미 이
    reactor가 알아도 안전한 것만 필터링해 넘겨준 값이다 (예: 포샤 본인의
    married_to 관계는 제외됨). 여기서 "그대로 읊지 말고 자연스럽게 녹여
    쓰라"는 프레이밍이 특히 중요한 이유: folger_context(캐릭터가 그냥 말로
    옮기면 되는 인용구)와 달리, 관계 목록을 날것 그대로 읽으면 캐릭터가
    자기 자신에 대한 신상 자료를 읊는 것처럼 들리기 때문이다."""
    if not character_context:
        return ""
    return (
        f"\n다음은 참고할 인물 관계 정보다 — 답변에 자연스럽게 녹여 쓰되, "
        f"목록을 그대로 나열하거나 설명하듯 말하지 마라:\n{character_context}\n"
    )


# 포샤가 아닌 reactor들의 반응 어투 — scene_progression.py의
# REACTOR_OVERRIDE_SCENES 참고. 아래 포샤 전용 지침 블록보다 의도적으로
# 훨씬 짧다: portia_hp/composure 단계 시스템이 없고(그건 트라이얼 전체에
# 걸친 포샤 본인의 압박받는 평정심 아크이지, 한 씬짜리 NPC와는 무관하다),
# "직접적인 판정을 피하라"는 재판관식 태도도 없다(그건 판사의 수법이지
# 애원하는 사람의 수법이 아니다). 어투 문자열은 SCENE_DIALOGUE_SYSTEM_PROMPT
# 의 화자 테이블과 맞춰서, 한 씬의 오프닝 대사와 선택 후 반응이 같은
# 캐릭터처럼 들리게 한다.
_NON_PORTIA_REACTOR_REGISTER: dict[str, str] = {
    "BASSANIO": "~이오/~겠소/~시오, 필사적인 애원조 (법정 재판관의 격식체 아님)",
}

# 로컬 모델에서 실제로 관측된 특정 대명사/소유격 혼동을 겨냥한 땜빵 수정 —
# 일반적인 지시대상 추적 문제를 해결하려는 게 아니다(그건 이 프로젝트가 이미
# 감수하기로 한 로컬 모델 고유의 신뢰성 한계이고, FallbackPortiaResponseClient
# 를 계속 두는 것과 같은 이유다), 그저 반복적으로 관측된 딱 한 가지 혼동만
# 막는 것: 로컬 모델이 가끔 안토니오를 "나의 벗"(바사니오 본인의 친구) 대신
# "당신의 벗"(샤일록의 친구)이라고 부른다 — 이 그래프에서 안토니오와
# 샤일록은 친구가 아니라 적이므로 거꾸로다.
_NON_PORTIA_REFERENT_GUARDRAIL: dict[str, str] = {
    "BASSANIO": (
        "안토니오는 너(바사니오)의 친구이지 샤일록의 친구가 아니다 — "
        "'당신의 벗'이 아니라 '나의 벗'/'내 친구'라고만 써라."
    ),
}

# STIMULUS_REACTION_GUIDE의 non-Portia 버전 — 그 가이드는 전적으로 재판관의
# 전략("절제된 회피", "계약 문언으로... 재구성", "절차적 압박")으로 쓰여
# 있는데, 이건 애원하는 인물에게는 정확히 틀린 방향이고, 실제로 바사니오의
# "이유" 절이 안토니오와의 관계 대신 법정 절차 언어 쪽으로 끌려가게 만들고
# 있었다(실측 확인: 여기서 STIMULUS_REACTION_GUIDE를 재사용했더니 바사니오
# 반응에 "법의 엄격한 형식과 절차"가 등장했다). 대신 날것의 개인적 이해관계
# 중심으로 프레이밍해서, 아래 character_context 블록이 모델이 붙잡을 진짜
# "이유"가 될 여지를 만든다.
_NON_PORTIA_STIMULUS_GUIDE: dict[str, str] = {
    "logical": (
        "Shylock pressed a rational/legal point. Don't out-argue him with law — you're not a "
        "jurist. Answer with what this bond actually costs the person you love, not courtroom logic."
    ),
    "emotional": (
        "Shylock appealed to feeling, injury, or personal wound. Meet it directly — grieve with "
        "him or beg harder. This is your register already; don't retreat into formality."
    ),
    "silence": (
        "Shylock answered with silence or a wordless gesture. Don't read it as a legal concession "
        "— read it as a person shutting you out. Push emotionally: ask him to just look at you."
    ),
    "provocation": (
        "Shylock taunted, accused, or defied the court. You're stung and it shows — push back with "
        "hurt or anger, but don't threaten him; you still need him to relent."
    ),
}


def _non_portia_reaction_instruction(
    prompt: PortiaResponsePromptDto,
    *,
    choice_id: str | None,
    choice_brief: str,
    stimulus: str,
) -> str:
    register = _NON_PORTIA_REACTOR_REGISTER.get(prompt.reactor_speaker, "~이오/~겠소/~시오")
    stimulus_guide = _NON_PORTIA_STIMULUS_GUIDE.get(stimulus, _NON_PORTIA_STIMULUS_GUIDE["logical"])
    referent_guardrail = _NON_PORTIA_REFERENT_GUARDRAIL.get(prompt.reactor_speaker, "")
    return (
        f"중요: 이번 반응은 포샤가 아니라 {prompt.reactor_speaker_label}({prompt.reactor_speaker})이 "
        "말한다. 위 시스템 지침의 '포샤 전용' 반응 규칙은 이번 요청에는 적용하지 마라 — "
        f"포샤를 언급하거나 포샤의 어조를 쓰지 말고, {prompt.reactor_speaker_label} 본인의 입으로만 "
        "샤일록에게 직접 말하는 대사를 써라. 3인칭 서술·'라고 말하였다' 형식 금지.\n"
        f"Register: {register}. 2–3문장 — 감정적 호소 한 문장과, 아래 '인물 관계 정보'에 근거한 "
        "구체적 이유 한 문장으로 나눠라. 법 절차나 계약 조항으로 근거를 대지 마라 — "
        f"{prompt.reactor_speaker_label}은 판사가 아니다.\n"
        f"{referent_guardrail}\n"
        f"평정심 게이지(portia_hp)는 포샤 전용 장치이니 이 반응엔 적용하지 마라 — "
        f"{prompt.reactor_speaker_label}은 지금 샤일록의 대답에 감정적으로 반응하는 한 사람일 뿐, "
        "판정을 회피하거나 우위를 유지할 필요가 없다.\n\n"
        f"샤일록의 방금 대답 ({choice_id or 'unknown'}): {choice_brief}\n"
        f"자극 유형: {stimulus} — {stimulus_guide}\n"
        f"{_folger_context_instruction(prompt.folger_context)}"
        f"{_character_context_instruction(prompt.character_context)}"
    )


# 공작(DUKE)은 _NON_PORTIA_REACTOR_REGISTER/_non_portia_reaction_instruction과
# 별도 경로다 — scene_progression.REACTOR_OVERRIDE_SCENES에 없는(즉 대부분의)
# 씬에서 선택 후 반응의 기본 화자가 이제 포샤 대신 공작이기 때문에(
# trial_progression_interactor._resolve_reactor 참고), 그 함수의 "너는 판사가
# 아니다 / 법 절차로 근거대지 마라" 전제가 정확히 거꾸로 적용된다 — 공작은
# 실제로 이 법정의 재판장이다. 어투는 duke_prompt.py의 공작과 맞추고,
# 자극별 반응 가이드는 이미 재판관식 전략("절제된 회피", "계약 문언으로
# 재구성", "절차적 압박")으로 쓰여 있는 STIMULUS_REACTION_GUIDE(포샤용)를
# 그대로 재사용한다 — 그 가이드 자체는 포샤의 변장/평정심 같은 개인 사정을
# 언급하지 않는, 화자 중립적인 "법정 인물의 전략" 텍스트라서 공작에게도
# 그대로 맞는다.
_DUKE_REGISTER = "~하오/~이오/~노라/~하겠소 — duke_prompt.py의 공작과 같은 근엄하고 절제된 재판장의 공식 어투"


def _duke_reaction_instruction(
    prompt: PortiaResponsePromptDto,
    *,
    choice_id: str | None,
    choice_brief: str,
    stimulus: str,
    stimulus_guide: str,
) -> str:
    return (
        "중요: 이번 반응은 포샤가 아니라 공작(DUKE)이 말한다. 위 시스템 지침의 "
        "'포샤 전용' 반응 규칙(변장, 빌린 권위 등 포샤 개인의 내면 사정)은 이번 "
        "요청에는 적용하지 마라 — 포샤를 언급하거나 포샤 특유의 사정을 끌어오지 "
        "말고, 공작 본인의 입으로만 샤일록에게 직접 말하는 대사를 써라. 3인칭 "
        "서술·'라고 말하였다' 형식 금지.\n"
        f"Register: {_DUKE_REGISTER}. 2–3문장. 공작은 실제로 이 법정의 재판장이니 "
        "법 절차·계약 문언·법정의 권위를 근거로 삼는 것이 정확히 공작다운 화법이다 "
        "— 애원하거나 개인적 감정으로 호소하지 마라.\n"
        "판정 회피 원칙: 이 반응 자체가 최종 판결은 아니다(승패는 이미 별도 절차로 "
        "정해짐) — 매 반응을 확정적 판결처럼 끝맺지 말고, 절차를 이어가는 재판장의 "
        "태도를 유지하라.\n\n"
        f"샤일록의 방금 대답 ({choice_id or 'unknown'}): {choice_brief}\n"
        f"자극 유형: {stimulus} — {stimulus_guide}\n"
        f"{_folger_context_instruction(prompt.folger_context)}"
        f"{_character_context_instruction(prompt.character_context)}"
    )


def _reaction_instruction(prompt: PortiaResponsePromptDto) -> str:
    choice_id = prompt.choice_id
    if choice_id is None and prompt.context.startswith("choice:"):
        choice_id = prompt.context.removeprefix("choice:")

    stimulus = CHOICE_STIMULUS.get(choice_id or "", "logical")
    stimulus_guide = STIMULUS_REACTION_GUIDE.get(stimulus, STIMULUS_REACTION_GUIDE["logical"])
    # 고정된 정본 요지보다, 플레이어가 이번 트라이얼에서 실제로 본 것을
    # 우선한다(choice_texts는 이제 문구만이 아니라 구체적 각도까지 다양화될
    # 수 있음 — build_scene_dialogue_message 참고).
    choice_brief = prompt.choice_label or CHOICE_BRIEFS.get(choice_id or "", prompt.context)

    if prompt.reactor_speaker == "DUKE":
        return _duke_reaction_instruction(
            prompt,
            choice_id=choice_id,
            choice_brief=choice_brief,
            stimulus=stimulus,
            stimulus_guide=stimulus_guide,
        )

    if prompt.reactor_speaker != "PORTIA":
        return _non_portia_reaction_instruction(
            prompt,
            choice_id=choice_id,
            choice_brief=choice_brief,
            stimulus=stimulus,
        )

    return (
        "포샤가 샤일록의 최근 선택에 직접 말하는 대사만 작성하라. "
        "3인칭 서술·'라고 그녀는 말하였다' 형식 금지. "
        "포샤 본인의 입으로 법정 연설체(~하오/~이오/~노라)로 2–3문장.\n\n"
        "판정 회피 원칙: 매 반응을 '그대가 틀렸소' 류의 직접 부정·판정으로 끝맺지 말라. "
        "옳음을 일부 인정하며 논점을 비틀거나, 되묻거나, 슬쩍 다른 쟁점으로 넘어가는 것 — "
        "옳고 그름을 가리지 않고도 우위를 유지하는 것이 포샤의 기술이다.\n\n"
        "Resource premise (do not explain to the player): Shylock's DP rises only through choices; "
        "skills heal him and do not affect Portia. Portia's composure (portia_hp) falls only from "
        "choice rebuttals — her tone should reflect how hard Shylock's argument has landed.\n\n"
        f"Shylock's latest move ({choice_id or 'unknown'}): {choice_brief}\n"
        f"Stimulus type: {stimulus} — {stimulus_guide}\n\n"
        f"{_portia_hp_tone_instruction(prompt.portia_hp)}\n"
        f"{_composure_signal_instruction(prompt.scene_index, prompt.portia_hp)}"
        f"{_previous_reactions_instruction(prompt.previous_portia_reactions)}"
        f"{_folger_context_instruction(prompt.folger_context)}"
        f"{_character_context_instruction(prompt.character_context)}\n"
        "Anti-pattern: do NOT conclude with '자비를 베풀라' or any mercy plea unless the stimulus "
        "is explicitly emotional AND portia_hp is high. Vary your closing move: procedure, reframe, "
        "authority, dry irony, or a pointed question."
    )


def build_user_message(prompt: PortiaResponsePromptDto) -> str:
    scene_brief = SCENE_BRIEFS.get(prompt.scene_index, "Venice trial scene.")
    choices = [CHOICE_BRIEFS.get(cid, cid) for cid in prompt.choice_history]

    type_instruction = {
        "narration": "Opening narration for the trial.",
        "reaction": _reaction_instruction(prompt),
        "ending": _ending_instruction(prompt.context),
    }.get(prompt.request_type, "Next trial line.")

    tubal_context = (
        f"Tubal intervened in: {list(prompt.tubal_used_scenes)}"
        if prompt.tubal_used_scenes
        else "Tubal has not intervened."
    )

    evidence_context = (
        f"Evidence presented by Shylock: {list(prompt.presented_evidence)}"
        if prompt.presented_evidence
        else "No evidence presented yet."
    )

    return_format = 'Return JSON with a single "text" field containing Korean prose only.'

    return f"""{type_instruction}

scene: {scene_brief}
context: {prompt.context}
dp: {prompt.dp} (max 100 — higher means stronger moral dignity retained through the trial)
portia_hp: {prompt.portia_hp} (max 100 — lower means Shylock's rebuttals have worn down Portia's composure)
choices: {choices if choices else ["(none)"]}
tubal: {tubal_context}
evidence: {evidence_context}

{return_format}"""
