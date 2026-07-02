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
    7: "Portia's alien law reversal — half Shylock's goods to the state, life at stake, forced conversion.",
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
    "defend_jessica": "Jessica is my daughter — what has that to do with the bond?",
    "reject_private_matter": "Keep private matters out of court.",
    "speechless": "Cannot speak.",
    "hath_not_speech": "Hath not a Jew eyes? (climax speech)",
    "bond_only": "Mercy is not in the contract — only law.",
    "beg_mercy": "Begs for the contract to be fulfilled.",
    "blood_impossible": "Cutting flesh without blood is impossible!",
    "drop_knife": "Lowers the knife.",
    "take_principal_only": "Will take only the principal sum.",
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

request_type:
- narration: neutral narrator tone (opening lines only if requested).
- reaction: 포샤's cold, logical courtroom speech responding to Shylock's last choice.
- ending: literary narrator closing — DP as moral victory, not legal win.
"""

SCENE_DIALOGUE_SYSTEM_PROMPT = """\
You write in-game dialogue for *The Merchant of Venice* trial (Venice court, 1596).
Generate Korean only (한국어). Stay faithful to Shakespeare's trial arc.

The judge is always **포샤** in Korean. Never use 발타자르, 발타사르, 포르샤, or Balthazar.

Speaker roles:
- NARRATOR: second-person to Shylock, atmospheric, no character name tags in lines.
- PORTIA: 포샤 speaks directly to Shylock — scene setup lines only, NOT post-choice reaction.
- BASSANIO: Bassanio pleads with Shylock — emotional, desperate, appeals to mercy.
- CROWD: hostile jeers, short bursts.

Each line must be a complete utterance. Do not end a line with an opening quote or start a line \
with a closing quote. If using quotes for direct speech, keep the full quoted sentence on one line.

Line kinds (required per line):
- speech: a character speaks directly (포샤 to Shylock, or crowd jeers). Show name tab in UI.
- narration: stage direction, third-person description, or player action — no name tab.

Rewrite the reference copy with fresh wording but same beats, facts, and emotional arc.
Do NOT include 포샤's post-choice reaction — that is generated separately.
"""


def build_scene_dialogue_message(prompt: SceneDialoguePromptDto) -> str:
    template = get_scene_template(prompt.scene_index)
    choices = [CHOICE_BRIEFS.get(cid, cid) for cid in prompt.choice_history]
    choice_specs = [
        f'  "{cid}": (reference) {template.canonical_choice_texts.get(cid, cid)}'
        for cid in template.choice_ids
    ]

    return f"""Generate scene dialogue for scene_index={prompt.scene_index} ({template.scene_id}).

scene brief: {template.brief}
speaker: {template.speaker}
dp: {prompt.dp} | shylock_hp: {prompt.shylock_hp}
prior choices: {choices if choices else ["(none)"]}

Reference lines (same meaning, new Korean wording; keep each line's kind):
{chr(10).join(f"  - [{kind.value}] {line}" for line, kind in zip(template.canonical_lines, template.canonical_line_kinds, strict=True))}

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


def build_user_message(prompt: PortiaResponsePromptDto) -> str:
    scene_brief = SCENE_BRIEFS.get(prompt.scene_index, "Venice trial scene.")
    choices = [CHOICE_BRIEFS.get(cid, cid) for cid in prompt.choice_history]

    type_instruction = {
        "narration": "Opening narration for the trial.",
        "reaction": "포샤's reaction to Shylock's latest choice.",
        "ending": "Final ending narration based on DP, alien law, and choices.",
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
dp: {prompt.dp} | shylock_hp: {prompt.shylock_hp}
alien_law_executed: {prompt.alien_law_executed}
choices: {choices if choices else ["(none)"]}
tubal: {tubal_context}
evidence: {evidence_context}

Return JSON with a single "text" field containing Korean prose only."""
