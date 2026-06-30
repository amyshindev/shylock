"""LLM prompts grounded in shylock-trial.jsx / The Merchant of Venice."""

from shylock_trial.app.dtos.portia_response_dto import PortiaResponsePromptDto

SCENE_BRIEFS: dict[int, str] = {
    0: "Opening — Venice court 1596. Shylock stands alone against the court.",
    1: "Portia (as Balthazar) asks Shylock to show mercy and take triple the bond.",
    2: "The crowd jeers at Shylock.",
    3: "Portia invokes Jessica's elopement and conversion.",
    4: "Portia's final question — does Shylock know mercy? Climax: Hath not a Jew eyes?",
    5: "Portia's blood loophole — no drop of blood, exactly one pound of flesh.",
    6: "Portia's alien law reversal — half Shylock's goods to the state, life at stake, forced conversion.",
}

CHOICE_BRIEFS: dict[str, str] = {
    "appeal_contract": "The contract is legally valid.",
    "appeal_humanity": "I am human — like you.",
    "appeal_mercy": "Shylock stays silent.",
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
Portia is disguised as a doctor of laws; the crowd is hostile; Shylock holds a valid bond.

Output Korean only (한국어). 2–3 sentences for reactions; 3–4 for ending narration.
Stay in Elizabethan Venice court — no modern references, no breaking the fourth wall.

request_type:
- narration: neutral narrator tone (opening lines only if requested).
- reaction: Portia's cold, logical courtroom speech responding to Shylock's last choice.
- ending: literary narrator closing — dignity as moral victory, not legal win.
"""


def build_user_message(prompt: PortiaResponsePromptDto) -> str:
    scene_brief = SCENE_BRIEFS.get(prompt.scene_index, "Venice trial scene.")
    choices = [CHOICE_BRIEFS.get(cid, cid) for cid in prompt.choice_history]

    type_instruction = {
        "narration": "Opening narration for the trial.",
        "reaction": "Portia's reaction to Shylock's latest choice.",
        "ending": "Final ending narration based on dignity and choices.",
    }.get(prompt.request_type, "Next trial line.")

    return f"""{type_instruction}

scene: {scene_brief}
context: {prompt.context}
dignity: {prompt.dignity} | confidence: {prompt.confidence}
choices: {choices if choices else ["(none)"]}

Return JSON with a single "text" field containing Korean prose only."""
