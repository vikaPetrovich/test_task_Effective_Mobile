"""update user profile fields

Revision ID: e31623ae8e30
Revises: 6e2442fde028
Create Date: 2026-05-01 12:01:26.979586

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "e31623ae8e30"
down_revision: Union[str, Sequence[str], None] = "6e2442fde028"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("first_name", sa.String(), nullable=True))
    op.add_column("users", sa.Column("last_name", sa.String(), nullable=True))
    op.add_column("users", sa.Column("middle_name", sa.String(), nullable=True))

    op.add_column("users", sa.Column("created_at", sa.DateTime(), nullable=True))
    op.add_column("users", sa.Column("updated_at", sa.DateTime(), nullable=True))
    op.add_column("users", sa.Column("deleted_at", sa.DateTime(), nullable=True))

    op.execute("UPDATE users SET created_at = NOW() WHERE created_at IS NULL")
    op.execute("UPDATE users SET updated_at = NOW() WHERE updated_at IS NULL")

    op.alter_column("users", "created_at", nullable=False)
    op.alter_column("users", "updated_at", nullable=False)

    op.drop_column("users", "username")


def downgrade() -> None:
    op.add_column(
        "users",
        sa.Column("username", sa.String(), nullable=True),
    )

    op.execute("UPDATE users SET username = email WHERE username IS NULL")

    op.alter_column("users", "username", nullable=False)

    op.drop_column("users", "deleted_at")
    op.drop_column("users", "updated_at")
    op.drop_column("users", "created_at")
    op.drop_column("users", "middle_name")
    op.drop_column("users", "last_name")
    op.drop_column("users", "first_name")