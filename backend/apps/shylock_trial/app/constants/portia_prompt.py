"""LLM prompts grounded in shylock-trial.jsx / The Merchant of Venice."""

from shylock_trial.app.constants.game_balance import (
    PORTIA_HP_HIGH_THRESHOLD,
    PORTIA_HP_LOW_THRESHOLD,
)
from shylock_trial.app.constants.scene_progression import (
    ALIEN_LAW_SCENE_INDEX,
    BLOOD_REVEAL_SCENE_INDEX,
    HATH_NOT_SCENE_INDEX,
)
from shylock_trial.app.constants.scene_catalog import get_scene_template
from shylock_trial.app.dtos.portia_response_dto import PortiaResponsePromptDto
from shylock_trial.app.dtos.scene_dialogue_dto import SceneDialoguePromptDto

SCENE_BRIEFS: dict[int, str] = {
    0: "Opening — Venice court 1596. Shylock stands alone against the court.",
    1: "Portia (as Balthazar) asks Shylock to show mercy and take triple the bond.",
    2: "Bassanio offers ten times the bond and begs Shylock for mercy.",
    3: "The crowd jeers at Shylock.",
    4: "Portia invokes Jessica's elopement and conversion.",
    5: "Jessica duet — Belmont garden cutaway after the courtroom attack on Jessica.",
    6: "Fixed climax — Shylock's 'Hath not a Jew eyes?' speech silences the court.",
    7: "Portia's blood loophole — no drop of blood, exactly one pound of flesh.",
    8: "Portia's alien law reversal — half Shylock's goods to the state, life at stake, forced conversion.",
    9: "Jessica intervention — Jessica bursts into the courtroom after the alien-law judgment.",
}

CHOICE_BRIEFS: dict[str, str] = {
    "bond_signature": "Both my signature and Antonio's are on this bond — what is the problem?",
    "bond_double_standard": "If a Venetian had made this contract, you would not question it like this.",
    "bond_lay_down": "(Silently lays the bond down before the court.)",
    "charter_merchant_trust": "If this court breaks a contract, what merchant will trust this city again?",
    "charter_law_precedent": "Once the law bends once, whose contract is safe next?",
    "charter_follow_law": "I merely follow the law of this city.",
    "gold_refuse_direct": "The sum is not the point — I want this bond.",
    "gold_shame_bribe": "You try to buy me off with money — you should be ashamed.",
    "gold_push_away": "(Silently pushes the pile of coins away.)",
    "scales_no_reason": "You ask my reason? There is none — it is simply my will.",
    "scales_humour": "Some cannot bear a pig, some a bagpipe; I merely cannot master my hatred of this man. (humour speech)",
    "scales_weigh": "(Takes out the scales and quietly weighs the flesh.)",
    "coat_show_spit": "See — what you spat is still on this coat.",
    "coat_before_dry": "Before this stain even dries, you speak to me of mercy.",
    "coat_show_silent": "(Silently shows the coat.)",
    "ghetto_curfew": "When the sun sets, I must return behind that gate — as you decreed.",
    "ghetto_who_guilty": "One locked away each night, one free to jeer each night — who is the guilty one here?",
    "ghetto_look_silent": "(Says nothing, only gazes toward the gate to the ghetto.)",
    "defend_jessica": "Jessica is my daughter — the court has no reason to reopen that wound.",
    "letter_irrelevant": "Whatever choice my daughter made, it has nothing to do with this bond.",
    "letter_fold_silent": "(Silently clenches his fist.)",
    "ring_leah_gift": (
        "This ring — I had it of Leah when I was a bachelor. "
        "I would not have given it for a wilderness of monkeys. (Leah's turquoise)"
    ),
    "ring_loss_dignity": "If you knew what I have lost, you would not dare call it a weakness.",
    "ring_clutch_silent": "(Quietly clasps his bare finger where the ring once sat.)",
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
    "plead_for_principal": "Please — let me have at least the principal sum.",
    "reject_conversion": "Death before forced conversion to Christianity.",
    "bow_accept": "Bows head and accepts conversion.",
    "mock_mercy": "Is this what Venice calls mercy?",
}

# Stimulus category for the most recent Shylock choice — drives Portia reaction tone.
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
    "plead_for_principal": "emotional",
    "reject_conversion": "provocation",
    "bow_accept": "emotional",
    "mock_mercy": "provocation",
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

# Portia's inner life — variety comes from one coherent character under strain,
# not from a forced rotation of reaction types.
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

# Scenes where the drama itself puts Portia's composure under real strain.
COMPOSURE_CLIMAX_SCENE_INDICES: frozenset[int] = frozenset(
    {
        HATH_NOT_SCENE_INDEX,
        BLOOD_REVEAL_SCENE_INDEX,
        ALIEN_LAW_SCENE_INDEX,
    }
)


def composure_break_allowed(scene_index: int, portia_hp: int) -> bool:
    """Server-side gate for visible cracks: low composure, or a climax-weight scene."""
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

SCENE_DIALOGUE_SYSTEM_PROMPT = """\
You write in-game dialogue for *The Merchant of Venice* trial (Venice court, 1596).
Generate Korean only (한국어). Stay faithful to Shakespeare's trial arc.

The judge is always **포샤** in Korean. Never use 발타자르, 발타사르, 포르샤, or Balthazar.

Speaker roles and register (match the reference line's speaker tag):
- NARRATOR: neutral third-person prose; no character speech endings.
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

Rewrite the reference copy with fresh wording but same beats, facts, emotional arc, and **per-line register**.
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


def build_scene_dialogue_message(prompt: SceneDialoguePromptDto) -> str:
    template = get_scene_template(prompt.scene_index)
    choices = [CHOICE_BRIEFS.get(cid, cid) for cid in prompt.choice_history]
    choice_specs = [
        f'  "{cid}": (reference) {template.canonical_choice_texts.get(cid, cid)}'
        for cid in template.choice_ids
    ]

    return f"""Generate scene dialogue for scene_index={prompt.scene_index} ({template.scene_id}).

scene brief: {template.brief}
primary speaker: {template.speaker}
dp: {prompt.dp}
prior choices: {choices if choices else ["(none)"]}
{_scene_register_hint(template.scene_id)}
Reference lines (same meaning, new Korean wording; keep each line's kind and speaker register):
{_reference_line_specs(template)}

Reference challenge prompt: {template.canonical_challenge_text or "(none — opening scene)"}

Choice ids and reference labels — output one Korean label per id in choice_texts:
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
    "rescued_ending": (
        "DP 90+ — '구원받은 자'. Legal loss stands, but Shylock's spirit and dignity "
        "survived the trial intact — read as the rarest moral triumph."
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


def _ending_instruction(context: str) -> str:
    ending_key = context.removeprefix("final_ending:") if context.startswith("final_ending:") else ""
    brief = ENDING_BRIEFS.get(
        ending_key,
        "Final ending narration based on dp and choices.",
    )
    return (
        f"{brief} "
        "Legal outcome is fixed for all endings: Shylock loses the trial per the play "
        "(alien law, forfeiture, forced conversion). Do NOT imply he wins in court or changes history. "
        "Write 3–4 sentences of Korean literary closing narration."
    )


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


def _reaction_instruction(prompt: PortiaResponsePromptDto) -> str:
    choice_id = prompt.choice_id
    if choice_id is None and prompt.context.startswith("choice:"):
        choice_id = prompt.context.removeprefix("choice:")

    stimulus = CHOICE_STIMULUS.get(choice_id or "", "logical")
    stimulus_guide = STIMULUS_REACTION_GUIDE.get(stimulus, STIMULUS_REACTION_GUIDE["logical"])
    choice_brief = CHOICE_BRIEFS.get(choice_id or "", prompt.context)

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
        f"{_folger_context_instruction(prompt.folger_context)}\n"
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

