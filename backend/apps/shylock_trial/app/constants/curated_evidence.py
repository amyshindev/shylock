"""Curated in-game evidence — shared by memory repo, PG seed, and RAG fallback."""

from shylock_trial.app.constants.scene_choices import get_choice_evidence_id
from shylock_trial.domain.entities.evidence_entity import Evidence

CURATED_EVIDENCE: tuple[Evidence, ...] = (
    Evidence(
        evidence_id="gaberdine",
        quote="You call me misbeliever, cut-throat dog, / And spit upon my Jewish gaberdine.",
        act_scene="1.3",
        icon="gaberdine",
        description="안토니오가 '개'라 부르며 침을 뱉었던 외투. 아직도 얼룩이 남아 있다.",
        source_ftln_range=(1003120, 1003140),
    ),
    Evidence(
        evidence_id="bond",
        quote=(
            "If you repay me not on such a day... let the forfeit be nominated "
            "for an equal pound of your fair flesh, to be cut off and taken "
            "in what part of your body pleaseth me."
        ),
        act_scene="1.3",
        icon="bond",
        description="안토니오와 맺은 계약. 법적으로 완전히 유효하다.",
        source_ftln_range=(1003200, 1003220),
    ),
    Evidence(
        evidence_id="venice_charter",
        quote=(
            "It is enacted in the laws of Venice... if it be proved against an alien "
            "that by direct or indirect attempts he seek the life of any citizen, "
            "the party 'gainst the which he doth contrive shall seize one half his goods."
        ),
        act_scene="4.1",
        icon="venice_charter",
        description="이 도시가 상인들의 도시로 설 수 있는 이유. 계약이 계약으로 지켜지기 때문이다.",
        source_ftln_range=(4001000, 4001040),
    ),
    Evidence(
        evidence_id="bassanio_gold",
        quote=(
            "For thy three thousand ducats here is six... I will pay ten times o'er "
            "on forfeit of my hands, my head, my heart."
        ),
        act_scene="4.1",
        icon="bassanio_gold",
        description="원금의 열 배. 바사니오가 안토니오를 대신해 내미는 돈이다.",
        source_ftln_range=(4001100, 4001120),
    ),
    Evidence(
        evidence_id="scales",
        quote="An equal pound of your fair flesh, to be cut off and taken in what part of your body pleaseth me.",
        act_scene="4.1",
        icon="scales",
        description="계약서에 명시된, 살을 정확히 달기 위한 도구. 그 자체로는 죄가 없다.",
        source_ftln_range=(4001200, 4001210),
    ),
    Evidence(
        evidence_id="hath_not",
        quote="Hath not a Jew eyes? If you prick us, do we not bleed? If you wrong us, shall we not revenge?",
        act_scene="3.1",
        icon="hath_not",
        description="하나의 인간으로서 샤일록이 한 말.",
        source_ftln_range=(3001300, 3001330),
    ),
    Evidence(
        evidence_id="jessica",
        quote="I would my daughter were dead at my foot, and the jewels in her ear.",
        act_scene="3.1",
        icon="jessica",
        description="딸이 도망치며 남긴 흔적. 돈과 보석을 훔쳐갔다.",
        source_ftln_range=(3001400, 3001420),
    ),
    Evidence(
        evidence_id="leah_ring",
        quote=(
            "It was my turquoise! I had it of Leah when I was a bachelor. "
            "I would not have given it for a wilderness of monkeys."
        ),
        act_scene="3.1",
        icon="leah_ring",
        description="죽은 아내 리아가 남긴 반지. 제시카가 훔쳐 달아나 원숭이 한 마리와 바꿔버렸다.",
        source_ftln_range=(3001430, 3001450),
    ),
    Evidence(
        evidence_id="whetted_knife",
        quote=(
            "Why dost thou whet thy knife so earnestly? — "
            "To cut the forfeiture from that bankrupt there."
        ),
        act_scene="4.1",
        icon="whetted_knife",
        description=(
            "재판 내내 조용히 갈아온 칼. 포샤의 선언과 함께, "
            "정의를 집행할 도구는 휘두를 수 없는 물건이 되었다."
        ),
        source_ftln_range=(4001300, 4001320),
    ),
    Evidence(
        evidence_id="bond_wording",
        quote=(
            "This bond doth give thee here no jot of blood; "
            "the words expressly are 'a pound of flesh.'"
        ),
        act_scene="4.1",
        icon="bond_wording",
        description="'살 1파운드.' 문구에는 정확히 그렇게만 쓰여 있다. 더도, 덜도 아니게.",
        source_ftln_range=(4001850, 4001870),
    ),
    Evidence(
        evidence_id="blood",
        quote="Shed thou no blood, nor cut thou less nor more but just a pound of flesh.",
        act_scene="4.1",
        icon="blood",
        description="포샤의 역전 논리. 살은 잘라도 피는 흘리면 안 된다.",
        source_ftln_range=(4001900, 4001920),
    ),
    Evidence(
        evidence_id="alien_law",
        quote=(
            "It is enacted in the laws of Venice, if it be proved against an "
            "alien... Shall seize one half his goods; the other half comes to the "
            "privy coffer of the state."
        ),
        act_scene="4.1",
        icon="alien_law",
        description="베네치아 시민이 아닌 자가 시민의 목숨을 노리면 적용되는 법. 포샤의 두 번째 반전.",
        source_ftln_range=(4002000, 4002040),
    ),
    Evidence(
        evidence_id="ghetto_gate",
        quote="",
        act_scene="(adaptation)",
        icon="ghetto_gate",
        description="밤마다 유대인을 격리 구역에 가두던 제도. 도시가 강제한 구조적 격리. 원작 희곡에는 없는 역사적 각색.",
        source_ftln_range=(0, 0),
    ),
)

CURATED_EVIDENCE_BY_ID: dict[str, Evidence] = {
    item.evidence_id: item for item in CURATED_EVIDENCE
}


def get_curated_evidence_by_id(evidence_id: str) -> Evidence | None:
    return CURATED_EVIDENCE_BY_ID.get(evidence_id)


def get_curated_evidence_for_choice(choice_id: str) -> Evidence | None:
    evidence_id = get_choice_evidence_id(choice_id)
    if evidence_id is None:
        return None
    return get_curated_evidence_by_id(evidence_id)
