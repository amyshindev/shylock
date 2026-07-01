"""Add scene_dialogues_json to trials."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "002_scene_dialogues"
down_revision: Union[str, None] = "001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("trials", sa.Column("scene_dialogues_json", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("trials", "scene_dialogues_json")
