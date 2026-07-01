"""Scene skeletons + canonical Korean copy used as LLM guidance and fallback."""

from dataclasses import dataclass

from shylock_trial.app.dtos.scene_dialogue_dto import (
    DialogueLineKind,
    SceneDialogueContent,
    SceneDialogueLine,
)
from shylock_trial.app.utils.dialogue_text import sanitize_dialogue_line, sanitize_game_text


@dataclass(frozen=True, slots=True)
class SceneTemplate:
    scene_id: str
    speaker: str
    speaker_label: str | None
    brief: str
    canonical_lines: tuple[str, ...]
    canonical_line_kinds: tuple[DialogueLineKind, ...]
    challenge_header: str | None
    canonical_challenge_text: str | None
    choice_ids: tuple[str, ...]
    canonical_choice_texts: dict[str, str]


SCENE_TEMPLATES: tuple[SceneTemplate, ...] = (
    SceneTemplate(
        scene_id="opening",
        speaker="NARRATOR",
        speaker_label=None,
        brief="Opening — Venice court 1596. Shylock stands alone against the court.",
        canonical_lines=(
            "베네치아 법정. 1596년. 해가 지고 있다. 돌벽에는 그림자가 기운다.",
            "샤일록, 당신은 지금 이 법정에 서 있다.",
            "당신의 적들이 당신을 둘러싸고 있다.",
            "당신에게는 법이 있다. 계약이 있다.",
            "... 하지만 그것으로 충분할 것인가?",
        ),
        canonical_line_kinds=(DialogueLineKind.NARRATION,) * 5,
        challenge_header=None,
        canonical_challenge_text=None,
        choice_ids=(),
        canonical_choice_texts={},
    ),
    SceneTemplate(
        scene_id="portia_opens",
        speaker="PORTIA",
        speaker_label="포샤",
        brief="Portia asks Shylock to show mercy and take triple the bond.",
        canonical_lines=(
            "샤일록, 당신은 안토니오의 살 1파운드를 요구하오.",
            "자비를 베푸시오. 세 배의 돈을 받으시오.",
            "이 법정은 당신의 자비를 기다리고 있소.",
        ),
        canonical_line_kinds=(DialogueLineKind.SPEECH,) * 3,
        challenge_header="▶ 샤일록의 선택",
        canonical_challenge_text="자비를 베풀라고? 당신들이 내게 베푼 자비는 어디 있소?",
        choice_ids=("appeal_contract", "appeal_humanity", "appeal_mercy"),
        canonical_choice_texts={
            "appeal_contract": "계약은 법적으로 유효합니다",
            "appeal_humanity": "나도 인간이오 — 당신들처럼",
            "appeal_mercy": "(침묵한다)",
        },
    ),
    SceneTemplate(
        scene_id="crowd_jeers",
        speaker="CROWD",
        speaker_label="군중",
        brief="The crowd jeers at Shylock.",
        canonical_lines=(
            '"저 유대인을 보라!"',
            '"자비도 모르는 자가!"',
            "웅성거림이 법정을 가득 채운다.",
        ),
        canonical_line_kinds=(
            DialogueLineKind.SPEECH,
            DialogueLineKind.SPEECH,
            DialogueLineKind.NARRATION,
        ),
        challenge_header="▶ 샤일록의 선택",
        canonical_challenge_text="군중의 조롱에 당신은—",
        choice_ids=("show_gaberdine", "ignore_court", "rage_at_crowd"),
        canonical_choice_texts={
            "show_gaberdine": "외투의 침 자국을 보여준다",
            "ignore_court": "무시하고 판사를 바라본다",
            "rage_at_crowd": "분노로 맞선다",
        },
    ),
    SceneTemplate(
        scene_id="jessica_attack",
        speaker="PORTIA",
        speaker_label="포샤",
        brief="Portia invokes Jessica's elopement and conversion.",
        canonical_lines=(
            "샤일록, 당신의 딸조차 당신을 떠났소.",
            "로렌조와 함께. 기독교로 개종하여.",
            "당신 스스로도 사랑받지 못하는 자가 어찌 법의 보호를 요구하오?",
        ),
        canonical_line_kinds=(DialogueLineKind.SPEECH,) * 3,
        challenge_header="▶ 샤일록의 선택",
        canonical_challenge_text="딸의 이름이 법정에 소환됐다.",
        choice_ids=("defend_jessica", "reject_private_matter", "speechless"),
        canonical_choice_texts={
            "defend_jessica": "제시카는 내 딸이오. 이 계약과 무슨 상관이오?",
            "reject_private_matter": "사적인 일을 법정에 끌어들이지 마시오",
            "speechless": "(말을 잇지 못한다)",
        },
    ),
    SceneTemplate(
        scene_id="hath_not_moment",
        speaker="PORTIA",
        speaker_label="포샤",
        brief="Portia's final question — does Shylock know mercy?",
        canonical_lines=(
            "샤일록, 마지막으로 묻겠소.",
            "당신은 왜 자비를 모르오?",
            "당신 안에 인간의 감정이 있기는 하오?",
        ),
        canonical_line_kinds=(DialogueLineKind.SPEECH,) * 3,
        challenge_header="▶ 샤일록의 선택",
        canonical_challenge_text="이 순간이다. 당신의 말로 대답할 것인가.",
        choice_ids=("hath_not_speech", "bond_only", "beg_mercy"),
        canonical_choice_texts={
            "hath_not_speech": '"유대인에게 눈이 없소? 피가 없소?"',
            "bond_only": "자비는 계약서에 없소. 법만이 있을 뿐",
            "beg_mercy": "...부탁이오. 제발 계약을 이행해주시오",
        },
    ),
    SceneTemplate(
        scene_id="blood_reveal",
        speaker="PORTIA",
        speaker_label="포샤",
        brief="Portia's blood loophole — no drop of blood, exactly one pound of flesh.",
        canonical_lines=(
            "살을 잘라도 좋소.",
            "단—",
            "피를 한 방울도 흘려서는 안 되오.",
            "살은 딱 1파운드. 그 이상도 이하도 안 되오.",
        ),
        canonical_line_kinds=(DialogueLineKind.SPEECH,) * 4,
        challenge_header="▶ 샤일록의 선택",
        canonical_challenge_text="이건 말이 안 된다. 하지만 법정이 고개를 끄덕인다.",
        choice_ids=("blood_impossible", "drop_knife", "take_principal_only"),
        canonical_choice_texts={
            "blood_impossible": "피 없이 살을 자르는 건 불가능하오!",
            "drop_knife": "...(칼을 내려놓는다)",
            "take_principal_only": "그렇다면 원금만 받겠소",
        },
    ),
    SceneTemplate(
        scene_id="alien_law_reveal",
        speaker="PORTIA",
        speaker_label="포샤",
        brief="Portia's alien law reversal — life, goods, forced conversion.",
        canonical_lines=(
            "당신은 칼을 거둔다.",
            "원금만이라도... 그것만은 받게 해주시오.",
            "포샤가 손을 든다.",
            '"기다리시오, 유대인."',
            '"이 법에는 아직 다른 조항이 남아 있소."',
        ),
        canonical_line_kinds=(
            DialogueLineKind.NARRATION,
            DialogueLineKind.NARRATION,
            DialogueLineKind.NARRATION,
            DialogueLineKind.SPEECH,
            DialogueLineKind.SPEECH,
        ),
        challenge_header="▶ 샤일록의 선택",
        canonical_challenge_text="외국인이라는 이유로, 법이 이번엔 당신의 목숨까지 가져가려 한다.",
        choice_ids=("reject_conversion", "bow_accept", "mock_mercy"),
        canonical_choice_texts={
            "reject_conversion": "개종이라니 — 차라리 죽음을 택하겠소",
            "bow_accept": "...그리하겠소. (고개를 숙인다)",
            "mock_mercy": "이것이 베네치아가 말하는 자비요?",
        },
    ),
)


def get_scene_template(scene_index: int) -> SceneTemplate:
    if scene_index < 0 or scene_index >= len(SCENE_TEMPLATES):
        raise ValueError(f"Unknown scene_index: {scene_index}")
    return SCENE_TEMPLATES[scene_index]


def _canonical_dialogue_lines(template: SceneTemplate) -> tuple[SceneDialogueLine, ...]:
    return tuple(
        SceneDialogueLine(
            text=sanitize_dialogue_line(text),
            kind=kind,
        )
        for text, kind in zip(
            template.canonical_lines,
            template.canonical_line_kinds,
            strict=True,
        )
    )


def fallback_scene_dialogue(scene_index: int) -> SceneDialogueContent:
    template = get_scene_template(scene_index)
    return SceneDialogueContent(
        lines=_canonical_dialogue_lines(template),
        challenge_header=template.challenge_header,
        challenge_text=(
            sanitize_game_text(template.canonical_challenge_text)
            if template.canonical_challenge_text
            else None
        ),
        choice_texts={
            cid: sanitize_game_text(text)
            for cid, text in template.canonical_choice_texts.items()
        },
    )
