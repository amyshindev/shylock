"""Seed curated evidence rows for RAG fallback and evidence API."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "017_seed_curated_evidence"
down_revision: Union[str, None] = "016_add_portia_reactions_json"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_UPSERT_SQL = sa.text(
    """
    INSERT INTO evidence (
        evidence_id, quote, act_scene, icon, description, source_ftln_start, source_ftln_end
    ) VALUES (
        :evidence_id, :quote, :act_scene, :icon, :description, :source_ftln_start, :source_ftln_end
    )
    ON CONFLICT (evidence_id) DO UPDATE SET
        quote = EXCLUDED.quote,
        act_scene = EXCLUDED.act_scene,
        icon = EXCLUDED.icon,
        description = EXCLUDED.description,
        source_ftln_start = EXCLUDED.source_ftln_start,
        source_ftln_end = EXCLUDED.source_ftln_end
    """
)

_EVIDENCE_ROWS: tuple[dict[str, object], ...] = (
    {
        "evidence_id": "gaberdine",
        "quote": "You call me misbeliever, cut-throat dog, / And spit upon my Jewish gaberdine.",
        "act_scene": "1.3",
        "icon": "gaberdine",
        "description": "안토니오가 '개'라 부르며 침을 뱉었던 외투. 아직도 얼룩이 남아 있다.",
        "source_ftln_start": 1003120,
        "source_ftln_end": 1003140,
    },
    {
        "evidence_id": "bond",
        "quote": (
            "If you repay me not on such a day... let the forfeit be nominated "
            "for an equal pound of your fair flesh, to be cut off and taken "
            "in what part of your body pleaseth me."
        ),
        "act_scene": "1.3",
        "icon": "bond",
        "description": "안토니오와 맺은 계약. 법적으로 완전히 유효하다.",
        "source_ftln_start": 1003200,
        "source_ftln_end": 1003220,
    },
    {
        "evidence_id": "venice_charter",
        "quote": (
            "It is enacted in the laws of Venice... if it be proved against an alien "
            "that by direct or indirect attempts he seek the life of any citizen, "
            "the party 'gainst the which he doth contrive shall seize one half his goods."
        ),
        "act_scene": "4.1",
        "icon": "venice_charter",
        "description": "이 도시가 상인들의 도시로 설 수 있는 이유. 계약이 계약으로 지켜지기 때문이다.",
        "source_ftln_start": 4001000,
        "source_ftln_end": 4001040,
    },
    {
        "evidence_id": "bassanio_gold",
        "quote": (
            "For thy three thousand ducats here is six... I will pay ten times o'er "
            "on forfeit of my hands, my head, my heart."
        ),
        "act_scene": "4.1",
        "icon": "bassanio_gold",
        "description": "원금의 열 배. 바사니오가 안토니오를 대신해 내미는 돈이다.",
        "source_ftln_start": 4001100,
        "source_ftln_end": 4001120,
    },
    {
        "evidence_id": "scales",
        "quote": "An equal pound of your fair flesh, to be cut off and taken in what part of your body pleaseth me.",
        "act_scene": "4.1",
        "icon": "scales",
        "description": "계약서에 명시된, 살을 정확히 달기 위한 도구. 그 자체로는 죄가 없다.",
        "source_ftln_start": 4001200,
        "source_ftln_end": 4001210,
    },
    {
        "evidence_id": "hath_not",
        "quote": "Hath not a Jew eyes? If you prick us, do we not bleed? If you wrong us, shall we not revenge?",
        "act_scene": "3.1",
        "icon": "hath_not",
        "description": "하나의 인간으로서 샤일록이 한 말.",
        "source_ftln_start": 3001300,
        "source_ftln_end": 3001330,
    },
    {
        "evidence_id": "jessica",
        "quote": "I would my daughter were dead at my foot, and the jewels in her ear.",
        "act_scene": "3.1",
        "icon": "jessica",
        "description": "딸이 도망치며 남긴 흔적. 돈과 보석을 훔쳐갔다.",
        "source_ftln_start": 3001400,
        "source_ftln_end": 3001420,
    },
    {
        "evidence_id": "leah_ring",
        "quote": (
            "It was my turquoise! I had it of Leah when I was a bachelor. "
            "I would not have given it for a wilderness of monkeys."
        ),
        "act_scene": "3.1",
        "icon": "leah_ring",
        "description": "죽은 아내 리아가 남긴 반지. 제시카가 훔쳐 달아나 원숭이 한 마리와 바꿔버렸다.",
        "source_ftln_start": 3001430,
        "source_ftln_end": 3001450,
    },
    {
        "evidence_id": "blood",
        "quote": "Shed thou no blood, nor cut thou less nor more but just a pound of flesh.",
        "act_scene": "4.1",
        "icon": "blood",
        "description": "포샤의 역전 논리. 살은 잘라도 피는 흘리면 안 된다.",
        "source_ftln_start": 4001900,
        "source_ftln_end": 4001920,
    },
    {
        "evidence_id": "alien_law",
        "quote": (
            "It is enacted in the laws of Venice, if it be proved against an "
            "alien... Shall seize one half his goods; the other half comes to the "
            "privy coffer of the state."
        ),
        "act_scene": "4.1",
        "icon": "alien_law",
        "description": "베네치아 시민이 아닌 자가 시민의 목숨을 노리면 적용되는 법. 포샤의 두 번째 반전.",
        "source_ftln_start": 4002000,
        "source_ftln_end": 4002040,
    },
    {
        "evidence_id": "ghetto_gate",
        "quote": "",
        "act_scene": "(adaptation)",
        "icon": "ghetto_gate",
        "description": "밤마다 유대인을 격리 구역에 가두던 제도. 도시가 강제한 구조적 격리. 원작 희곡에는 없는 역사적 각색.",
        "source_ftln_start": 0,
        "source_ftln_end": 0,
    },
)


def upgrade() -> None:
    conn = op.get_bind()
    for row in _EVIDENCE_ROWS:
        conn.execute(_UPSERT_SQL, row)


def downgrade() -> None:
    op.execute(
        sa.text(
            "DELETE FROM evidence WHERE evidence_id IN ("
            "'gaberdine','bond','venice_charter','bassanio_gold','scales',"
            "'hath_not','jessica','leah_ring','blood','alien_law','ghetto_gate'"
            ")"
        )
    )
