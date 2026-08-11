"""Remove the "alien_law" curated evidence item.

Never tied to any in-game choice (CHOICE_EVIDENCE never mapped a choice to
it — alien_law_reveal is a scripted, choice-less scene), and the scene's own
item HUD deliberately stays empty (see BattleScreen.tsx / scene-item-gate.ts:
only hath_not_moment gets a HUD item, by design). Kept around only as a
browsable "inspect" evidence; removed at the game designer's request.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "033_remove_alien_law_evidence"
down_revision: Union[str, None] = "032_antonio_bassanio_friend_of"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_EVIDENCE_ID = "alien_law"
_ROW = {
    "evidence_id": _EVIDENCE_ID,
    "quote": (
        "It is enacted in the laws of Venice, if it be proved against an "
        "alien... Shall seize one half his goods; the other half comes to "
        "the privy coffer of the state."
    ),
    "act_scene": "4.1",
    "icon": "alien_law",
    "description": "베네치아 시민이 아닌 자가 시민의 목숨을 노리면 적용되는 법. 포샤의 두 번째 반전.",
    "source_ftln_start": 4001363,
    "source_ftln_end": 4001369,
}


def upgrade() -> None:
    conn = op.get_bind()
    conn.execute(
        sa.text("DELETE FROM evidence WHERE evidence_id = :evidence_id"),
        {"evidence_id": _EVIDENCE_ID},
    )


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(
        sa.text(
            """
            INSERT INTO evidence
                (evidence_id, quote, act_scene, icon, description,
                 source_ftln_start, source_ftln_end)
            VALUES
                (:evidence_id, :quote, :act_scene, :icon, :description,
                 :source_ftln_start, :source_ftln_end)
            """
        ),
        _ROW,
    )
