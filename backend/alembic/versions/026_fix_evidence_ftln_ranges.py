"""Correct evidence.source_ftln_start/end — most were off by 40 to 640+ ftln
from the actual seeded play_lines rows (spot-checked against the live
corpus by full-text search on each evidence's quote). gaberdine,
venice_charter, and jessica were already correct and are left untouched.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "026_fix_evidence_ftln_ranges"
down_revision: Union[str, None] = "025_add_google_login"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# evidence_id -> (old_start, old_end, new_start, new_end)
_FTLN_FIXES: dict[str, tuple[int, int, int, int]] = {
    "bond": (1003200, 1003220, 1003158, 1003165),
    "bassanio_gold": (4001100, 4001120, 4001085, 4001219),
    "scales": (4001200, 4001210, 4001241, 4001242),
    "hath_not": (3001300, 3001330, 3001057, 3001066),
    "leah_ring": (3001430, 3001450, 3001119, 3001122),
    "whetted_knife": (4001300, 4001320, 4001123, 4001126),
    "bond_wording": (4001850, 4001870, 4001319, 4001321),
    "blood": (4001900, 4001920, 4001339, 4001340),
    "alien_law": (4002000, 4002040, 4001363, 4001369),
}

_UPDATE_SQL = sa.text(
    """
    UPDATE evidence
    SET source_ftln_start = :start, source_ftln_end = :end
    WHERE evidence_id = :evidence_id
    """
)


def upgrade() -> None:
    conn = op.get_bind()
    for evidence_id, (_, _, new_start, new_end) in _FTLN_FIXES.items():
        conn.execute(
            _UPDATE_SQL,
            {"evidence_id": evidence_id, "start": new_start, "end": new_end},
        )


def downgrade() -> None:
    conn = op.get_bind()
    for evidence_id, (old_start, old_end, _, _) in _FTLN_FIXES.items():
        conn.execute(
            _UPDATE_SQL,
            {"evidence_id": evidence_id, "start": old_start, "end": old_end},
        )
