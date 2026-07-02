"""Shift trial scene_index after inserting bassanio_plea at index 2."""

from typing import Sequence, Union

from alembic import op

revision: str = "006_bassanio_plea_shift"
down_revision: Union[str, None] = "005_trial_tubal_evidence"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        UPDATE trials
        SET scene_index = scene_index + 1
        WHERE scene_index >= 2
        """
    )


def downgrade() -> None:
    op.execute(
        """
        UPDATE trials
        SET scene_index = scene_index - 1
        WHERE scene_index >= 3
        """
    )
