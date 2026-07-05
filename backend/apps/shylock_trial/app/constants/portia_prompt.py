"""LLM prompts grounded in shylock-trial.jsx / The Merchant of Venice."""

from shylock_trial.app.constants.scene_catalog import get_scene_template
from shylock_trial.app.dtos.portia_response_dto import PortiaResponsePromptDto
from shylock_trial.app.dtos.scene_dialogue_dto import SceneDialoguePromptDto

SCENE_BRIEFS: dict[int, str] = {
    0: "Opening — Venice court 1596. Shylock stands alone against the court.",
    1: "Portia (as Balthazar) asks Shylock to show mercy and take triple the bond.",
    2: "Bassanio offers ten times the bond and begs Shylock for mercy.",
    3: "The crowd jeers at Shylock.",
    4: "Portia invokes Jessica's elopement and conversion.",
    5: "Portia's final question — does Shylock know mercy? Climax: Hath not a Jew eyes?",
    6: "Portia's blood loophole — no drop of blood, exactly one pound of flesh.",
    7: "Jessica duet — Belmont garden cutaway before the final courtroom judgment.",
    8: "Portia's alien law reversal — half Shylock's goods to the state, life at stake, forced conversion.",
    9: "Jessica intervention — Jessica bursts into the courtroom after the alien-law judgment.",
}

CHOICE_BRIEFS: dict[str, str] = {
    "appeal_contract": "The contract is legally valid.",
    "appeal_humanity": "I am human — like you.",
    "appeal_mercy": "Shylock stays silent.",
    "invoke_bond": "The contract stands — money cannot replace it.",
    "accuse_bassanio": "Accuses Bassanio of putting Antonio in this position.",
    "cold_silence": "Closes eyes in silence.",
    "show_gaberdine": "Shows the spit stain on his gaberdine.",
    "ignore_court": "Ignores the crowd, looks to the judge.",
    "rage_at_crowd": "Rages back at the crowd.",
    "defend_jessica": "Jessica is my daughter — the court has no reason to reopen that wound.",
    "reject_private_matter": "Do not put my household's affairs on the court's scales.",
    "speechless": "Cannot speak.",
    "hath_not_speech": "Hath not a Jew eyes? (climax speech)",
    "bond_only": "Mercy is not in the contract — only law.",
    "beg_mercy": "Begs for the contract to be fulfilled.",
    "blood_impossible": "Cutting flesh without blood is impossible!",
    "drop_knife": "Lowers the knife.",
    "take_principal_only": "Will take only the principal sum.",
    "plead_for_principal": "Please — let me have at least the principal sum.",
    "reject_conversion": "Death before forced conversion to Christianity.",
    "bow_accept": "Bows head and accepts conversion.",
    "mock_mercy": "Is this what Venice calls mercy?",
}

SYSTEM_PROMPT = """\
You write in-game text for *The Merchant of Venice* trial (shylock-trial.jsx canon).
The judge is always called **포샤** in Korean player-facing text.
Never use 발타자르, 발타사르, 포르샤, Balthazar, or other alternate names.
The crowd is hostile; Shylock holds a valid bond.

Output Korean only (한국어). 2–3 sentences for reactions; 3–4 for ending narration.
Stay in Elizabethan Venice court — no modern references, no breaking the fourth wall.
Do not wrap lines in orphan quotation marks. Each sentence must be complete on its own.

For request_type=reaction (포샤 대사):
- Write ONLY Portia's direct courtroom speech to Shylock, in first person or imperative court register (~하오/~이오/~노라).
- NEVER use third-person narration about any character: no "그녀는", "포샤는", "바사니오가", "라고 말하였다".
- Do NOT describe Portia speaking — only output the words she says.
- Bad: "법정은 증서 위에 서 있노라고 그녀는 선언하였다."
- Good: "법정은 말이 아니라 증서와 법조문 위에 서 있노라."

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

def build_user_message(prompt: PortiaResponsePromptDto) -> str:
    scene_brief = SCENE_BRIEFS.get(prompt.scene_index, "Venice trial scene.")
    choices = [CHOICE_BRIEFS.get(cid, cid) for cid in prompt.choice_history]

    type_instruction = {
        "narration": "Opening narration for the trial.",
        "reaction": (
            "포샤가 샤일록의 최근 선택에 직접 말하는 대사만 작성하라. "
            "3인칭 서술·'라고 그녀는 말하였다' 형식 금지. "
            "포샤 본인의 입으로 법정 연설체(~하오/~이오/~노라)로 2–3문장."
        ),
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

    return f"""{type_instruction}

scene: {scene_brief}
context: {prompt.context}
dp: {prompt.dp} (max 100 — higher means stronger moral dignity retained through the trial)
choices: {choices if choices else ["(none)"]}
tubal: {tubal_context}
evidence: {evidence_context}

Return JSON with a single "text" field containing Korean prose only."""

