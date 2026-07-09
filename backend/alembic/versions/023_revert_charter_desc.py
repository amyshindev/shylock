"""Revert venice_charter's Korean description to its original flavor text (quote fix from 022 stays)."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "023_revert_charter_desc"
down_revision: Union[str, None] = "022_fix_venice_charter_quote"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_NEW_DESCRIPTION = "이 도시가 상인들의 도시로 설 수 있는 이유. 계약이 계약으로 지켜지기 때문이다."
_OLD_DESCRIPTION = "베네치아에서 장사하는 상인들의 권리와 특권을 규정한 문서. 샤일록은 계약을 거부당하면 이 헌장과 도시의 자유마저 위태로워질 것이라 경고한다."


def upgrade() -> None:
    conn = op.get_bind()
    conn.execute(
        sa.text("UPDATE evidence SET description = :description WHERE evidence_id = 'venice_charter'"),
        {"description": _NEW_DESCRIPTION},
    )


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(
        sa.text("UPDATE evidence SET description = :description WHERE evidence_id = 'venice_charter'"),
        {"description": _OLD_DESCRIPTION},
    )
