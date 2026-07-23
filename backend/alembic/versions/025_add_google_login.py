"""Support Google social login: users.google_id, nullable email/password_hash."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "025_add_google_login"
down_revision: Union[str, None] = "024_add_users_and_trial_user_id"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column("users", "email", existing_type=sa.String(255), nullable=True)
    op.alter_column("users", "password_hash", existing_type=sa.Text(), nullable=True)
    op.add_column("users", sa.Column("google_id", sa.String(64), nullable=True))
    op.create_index("ix_users_google_id", "users", ["google_id"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_users_google_id", table_name="users")
    op.drop_column("users", "google_id")
    op.alter_column("users", "password_hash", existing_type=sa.Text(), nullable=False)
    op.alter_column("users", "email", existing_type=sa.String(255), nullable=False)
