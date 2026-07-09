"""Correct venice_charter evidence: quote the actual charter passage, not the alien-law statute."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "022_fix_venice_charter_quote"
down_revision: Union[str, None] = "021_fix_jessica_letter_evidence"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_NEW_ROW: dict[str, object] = {
    "evidence_id": "venice_charter",
    "quote": (
        "To have the due and forfeit of my bond. / "
        "If you deny it, let the danger light / "
        "Upon your charter and your city's freedom!"
    ),
    "act_scene": "4.1",
    "icon": "venice_charter",
    "description": "베네치아에서 장사하는 상인들의 권리와 특권을 규정한 문서. 샤일록은 계약을 거부당하면 이 헌장과 도시의 자유마저 위태로워질 것이라 경고한다.",
    "source_ftln_start": 4001038,
    "source_ftln_end": 4001040,
}

_OLD_ROW: dict[str, object] = {
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
}

_UPDATE_SQL = sa.text(
    """
    UPDATE evidence SET
        quote = :quote,
        act_scene = :act_scene,
        icon = :icon,
        description = :description,
        source_ftln_start = :source_ftln_start,
        source_ftln_end = :source_ftln_end
    WHERE evidence_id = :evidence_id
    """
)


def upgrade() -> None:
    conn = op.get_bind()
    conn.execute(_UPDATE_SQL, _NEW_ROW)


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(_UPDATE_SQL, _OLD_ROW)
