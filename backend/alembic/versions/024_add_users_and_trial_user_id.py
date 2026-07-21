"""Add users table and nullable trials.user_id for game login."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "024_add_users_and_trial_user_id"
down_revision: Union[str, None] = "023_revert_charter_desc"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("nickname", sa.String(64), nullable=False),
        sa.Column("password_hash", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.add_column(
        "trials",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_index("ix_trials_user_id", "trials", ["user_id"])
    op.create_foreign_key(
        "fk_trials_user_id_users",
        "trials",
        "users",
        ["user_id"],
        ["user_id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("fk_trials_user_id_users", "trials", type_="foreignkey")
    op.drop_index("ix_trials_user_id", table_name="trials")
    op.drop_column("trials", "user_id")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
