"""Scene skeletons + canonical Korean copy used as LLM guidance and fallback."""

from dataclasses import dataclass

from shylock_trial.app.dtos.scene_dialogue_dto import (
    DialogueLineKind,
    SceneDialogueContent,
    SceneDialogueLine,
)
from shylock_trial.app.utils.dialogue_text import (
    sanitize_character_direct_speech,
    sanitize_dialogue_line,
    sanitize_game_text,
)


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
    canonical_line_speakers: tuple[str | None, ...] = ()


SCENE_TEMPLATES: tuple[SceneTemplate, ...] = (
    SceneTemplate(
        scene_id="opening",
        speaker="NARRATOR",
        speaker_label=None,
        brief="Opening — Venice court 1596. Shylock stands alone against the court.",
        canonical_lines=(
            "베네치아 법정. 해가 지고 있다. 돌벽에는 그림자가 기운다.",
            "샤일록, 당신은 지금 이 법정에 서 있다.",
            "당신의 적들이 당신을 둘러싸고 있다.",
            "당신에게는 법이 있다. 계약이 있다.",
            "... 그것으로 충분할 것인가?",
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
            "법정은 그 증서의 효력을 인정하오. 그러나 그 전에, 내 말을 들으시오.",
            "자비란 강요로 얻어지는 것이 아니오. 그것은 하늘에서 부드럽게 내리는 비와 같이, 스스로 내려와 땅을 적시는 것이오.",
            "자비는 이중으로 축복받은 것이오 — 베푸는 자와 받는 자를 동시에 축복하니.",
            "왕의 왕관보다 자비로운 마음이 더 위대하다 하였소. 권력의 자리에 앉은 자일수록, 그 힘을 어떻게 쓰는가로 진정한 위대함이 드러나는 법이오.",
            "샤일록, 당신에게는 그 증서를 강제할 권리가 있소.",
            "하지만 나는 당신에게 묻고 싶소 — 그 권리를 반드시 끝까지 쥐고 있어야만 하는지.",
            "세 배의 돈을 받으시오. 그것으로 충분하지 않소?",
            "이 법정은, 그리고 나는, 당신의 자비를 기다리고 있소.",
        ),
        canonical_line_kinds=(DialogueLineKind.SPEECH,) * 9,
        challenge_header="▶ 샤일록의 선택",
        canonical_challenge_text="자비를 베풀라고? 당신들이 내게 베푼 자비는 어디 있소?",
        choice_ids=(
            "bond_signature",
            "bond_double_standard",
            "bond_lay_down",
            "charter_merchant_trust",
            "charter_law_precedent",
            "charter_follow_law",
        ),
        canonical_choice_texts={
            "bond_signature": "이 증서엔 내 서명도, 안토니오의 서명도 있소. 무엇이 문제요?",
            "bond_double_standard": "베네치아 사람이 맺은 계약이라면, 당신들은 이렇게 따지지 않았을 것이오",
            "bond_lay_down": "(계약서를 법정 앞에 조용히 내려놓는다)",
            "charter_merchant_trust": "이 법정이 계약을 어긴다면, 어느 상인이 다시 이 도시를 믿겠소?",
            "charter_law_precedent": "법이 한 번 흔들리면, 그다음은 누구의 계약이오?",
            "charter_follow_law": "나는 그저 이 도시의 법을 따를 뿐이오",
        },
    ),
    SceneTemplate(
        scene_id="bassanio_plea",
        speaker="BASSANIO",
        speaker_label="바사니오",
        brief="Bassanio offers ten times the bond and begs Shylock for mercy.",
        canonical_lines=(
            "샤일록, 내가 빌린 돈은 3천 두캇이었소. 그 열 배를 드리겠소.",
            "당신이 원하는 게 정말 돈이라면, 이보다 더 큰 액수는 없을 것이오.",
            "제발... 이번 한 번만 자비를 베푸시오. 당신도 사람이라면, 마음이 있을 것이오.",
            "당신이 지금 손에 쥔 칼로 얻으려는 건 정의가 아니오. 그저 오래 묵은 증오요.",
        ),
        canonical_line_kinds=(DialogueLineKind.SPEECH,) * 4,
        challenge_header="▶ 샤일록의 선택",
        canonical_challenge_text="바사니오가 당신을 설득하려 한다. 당신은—",
        choice_ids=(
            "gold_refuse_direct",
            "gold_shame_bribe",
            "gold_push_away",
            "scales_no_reason",
            "scales_humour",
            "scales_weigh",
        ),
        canonical_choice_texts={
            "gold_refuse_direct": "금액이 문제가 아니오. 내가 원하는 건 이 증서요",
            "gold_shame_bribe": "돈으로 나를 매수하려 하다니, 당신들이야말로 부끄러운 줄 아시오",
            "gold_push_away": "(동전 더미를 조용히 밀어낸다)",
            "scales_no_reason": "이유를 대라 하셨소? 이유는 없소. 그저 내 뜻이오",
            "scales_humour": "어떤 이는 돼지를 보면 못 견디고, 어떤 이는 백파이프 소리에 참지 못하오. 나는 이 사람에 대한 미움을 다스리지 못할 뿐이오",
            "scales_weigh": "(저울을 꺼내 조용히 무게를 가늠한다)",
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
        choice_ids=(
            "coat_show_spit",
            "coat_before_dry",
            "coat_show_silent",
            "ghetto_curfew",
            "ghetto_who_guilty",
            "ghetto_look_silent",
        ),
        canonical_choice_texts={
            "coat_show_spit": "보시오. 당신들이 뱉은 것이, 아직도 이 옷에 남아 있소",
            "coat_before_dry": "이 얼룩이 마르기도 전에, 당신들은 내게 자비를 말하는구려",
            "coat_show_silent": "(외투를 조용히 보여준다)",
            "ghetto_curfew": "해가 지면, 나는 저 문 안으로 돌아가야 하오. 당신들이 정한 대로",
            "ghetto_who_guilty": "매일 밤 갇히는 자와, 매일 밤 자유로이 떠드는 자 — 이 법정에서 누가 죄인이오?",
            "ghetto_look_silent": "(대답 대신, 게토로 향하는 문 쪽을 가만히 바라본다)",
        },
    ),
    SceneTemplate(
        scene_id="jessica_attack",
        speaker="PORTIA",
        speaker_label="포샤",
        brief="Portia invokes Jessica's elopement and conversion.",
        canonical_lines=(
            "샤일록, 법정은 한 가지를 기억하고 있소. 당신의 딸조차 당신의 집을 떠났다는 것을.",
            "로렌조와 함께, 그리고 기독교로 개종하여. 그녀는 스스로 아버지의 이름을 벗어던졌소.",
            "혈육조차 등을 돌리게 만드는 자에게, 낯선 이의 살 한 파운드가 그리 소중하다니 기이한 일이오.",
            "성경에도 이르길, 사람이 제 집을 다스리지 못하면 어찌 하나님의 교회를 돌보겠느냐 하였소.",
            "당신은 딸의 마음 하나 붙들지 못한 자요. 그런 자가 어찌 이 법정에서 정의를 논하려 하시오?",
            "정을 나눌 줄 모르는 자이니, 계약 또한 정 없이 읽으려 하는구려.",
        ),
        canonical_line_kinds=(DialogueLineKind.SPEECH,) * 6,
        challenge_header="▶ 샤일록의 선택",
        canonical_challenge_text="딸의 이름이 법정에 소환됐다.",
        choice_ids=("defend_jessica", "reject_private_matter", "speechless"),
        canonical_choice_texts={
            "defend_jessica": "제시카는 내 딸이오. 이 법정이 그 상처를 다시 후벼 파는 것을 두고 볼 이유는 없소.",
            "reject_private_matter": "내 집안의 일을 이 법정의 저울에 함께 올리지 마시오.",
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
        scene_id="jessica_duet",
        speaker="JESSICA",
        speaker_label="제시카",
        brief="Jessica and Lorenzo in Belmont garden — parallel cutaway before the final courtroom judgment.",
        canonical_lines=(
            "벨몬트의 정원. 달빛이 낮게 깔린다. 제시카와 로렌조가 나란히 앉아 있다.",
            "이런 밤이었지 — 트로일러스가 트로이의 성벽 위에서 크레시다를 향한 그리움에 한숨짓던 것도.",
            "이런 밤이었죠 — 디도가 버들가지를 들고 해변에 서서, 떠나버린 연인을 향해 손짓하던 것도.",
            "이런 밤이었지 — 메데이아가 마법의 약초를 모아, 늙은 아이손을 다시 젊게 했던 것도.",
            "...그리고 이런 밤이었죠. 제가 아버지의 집에서 도망쳐 나온 것도.",
            "제시카...?",
            "당신은 계속 옛날 연인들 얘기를 하지만, 로렌조 — 그들은 전부 버림받았거나, 버리고 떠났어요.",
            "우리 이야기도 그렇게 끝날까요?",
            "그런 뜻이 아니었어—",
            "알아요. 하지만 저는... 오늘 밤 계속 아버지 생각이 나요.",
            "지금쯤 법정은 어떻게 됐을까요.",
            "악사들을 불러 음악을 청하지. 그럼 마음이 좀 놓일 거야.",
            "멀리서 악사들이 현을 고르는 소리가 들린다. 곧 부드러운 선율이 정원에 퍼진다.",
            "...저는 아름다운 음악을 들으면 마음이 편치 않아요.",
            "의아하군. 왜지?",
            "모르겠어요. 그냥... 이렇게 평온한 순간일수록, 제 안의 무언가가 더 시끄러워져요.",
        ),
        canonical_line_kinds=(
            DialogueLineKind.NARRATION,
            DialogueLineKind.SPEECH,
            DialogueLineKind.SPEECH,
            DialogueLineKind.SPEECH,
            DialogueLineKind.SPEECH,
            DialogueLineKind.SPEECH,
            DialogueLineKind.SPEECH,
            DialogueLineKind.SPEECH,
            DialogueLineKind.SPEECH,
            DialogueLineKind.SPEECH,
            DialogueLineKind.SPEECH,
            DialogueLineKind.NARRATION,
            DialogueLineKind.SPEECH,
            DialogueLineKind.SPEECH,
            DialogueLineKind.SPEECH,
            DialogueLineKind.SPEECH,
        ),
        canonical_line_speakers=(
            "NARRATOR",
            "LORENZO",
            "JESSICA",
            "LORENZO",
            "JESSICA",
            "LORENZO",
            "JESSICA",
            "JESSICA",
            "LORENZO",
            "JESSICA",
            "JESSICA",
            "LORENZO",
            "NARRATOR",
            "JESSICA",
            "LORENZO",
            "JESSICA",
        ),
        challenge_header=None,
        canonical_challenge_text=None,
        choice_ids=(),
        canonical_choice_texts={},
    ),
    SceneTemplate(
        scene_id="alien_law_reveal",
        speaker="PORTIA",
        speaker_label="포샤",
        brief="Portia's alien law reversal — life, goods, forced conversion.",
        canonical_lines=(
            "당신은 칼을 거둔다.",
            "포샤가 손을 든다.",
            '"기다리시오, 유대인."',
            '"이 법에는 아직 다른 조항이 남아 있소."',
        ),
        canonical_line_kinds=(
            DialogueLineKind.NARRATION,
            DialogueLineKind.NARRATION,
            DialogueLineKind.SPEECH,
            DialogueLineKind.SPEECH,
        ),
        challenge_header="▶ 샤일록의 선택",
        canonical_challenge_text="외국인이라는 이유로, 법이 이번엔 당신의 목숨까지 가져가려 한다.",
        choice_ids=("plead_for_principal",),
        canonical_choice_texts={
            "plead_for_principal": "원금만이라도... 그것만은 받게 해주시오.",
        },
    ),
    SceneTemplate(
        scene_id="jessica_intervention",
        speaker="JESSICA",
        speaker_label="제시카",
        brief="Jessica bursts into the courtroom to intervene after the alien-law judgment.",
        canonical_lines=("안녕하세요",),
        canonical_line_kinds=(DialogueLineKind.SPEECH,),
        challenge_header=None,
        canonical_challenge_text=None,
        choice_ids=(),
        canonical_choice_texts={},
    ),
)


def get_scene_template(scene_index: int) -> SceneTemplate:
    if scene_index < 0 or scene_index >= len(SCENE_TEMPLATES):
        raise ValueError(f"Unknown scene_index: {scene_index}")
    return SCENE_TEMPLATES[scene_index]


def _line_speaker(
    template: SceneTemplate,
    index: int,
    kind: DialogueLineKind,
) -> str:
    speakers = template.canonical_line_speakers
    if index < len(speakers) and speakers[index]:
        return speakers[index]
    if kind == DialogueLineKind.NARRATION:
        return "NARRATOR"
    return template.speaker


def _canonical_dialogue_lines(template: SceneTemplate) -> tuple[SceneDialogueLine, ...]:
    lines: list[SceneDialogueLine] = []
    for index, (text, kind) in enumerate(
        zip(
            template.canonical_lines,
            template.canonical_line_kinds,
            strict=True,
        )
    ):
        cleaned = sanitize_dialogue_line(text)
        if kind == DialogueLineKind.SPEECH:
            cleaned = sanitize_character_direct_speech(cleaned)
        lines.append(
            SceneDialogueLine(
                text=cleaned,
                kind=kind,
                speaker=_line_speaker(template, index, kind),
            )
        )
    return tuple(lines)


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
