"""Drop portia_stances_json — stance tagging replaced by persona-based prompting."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "020_drop_portia_stances_json"
down_revision: Union[str, None] = "019_seed_blood_reveal_items"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column("trials", "portia_stances_json")


def downgrade() -> None:
    op.add_column(
        "trials",
        sa.Column("portia_stances_json", sa.Text(), nullable=True),
    )
