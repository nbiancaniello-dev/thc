"""Seed dragon_ball_ids for demo users

Revision ID: f1c3a9d4b7e2
Revises: e0a2f6b02283
Create Date: 2026-10-27 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'f1c3a9d4b7e2'
down_revision: Union[str, Sequence[str], None] = 'e0a2f6b02283'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Assign Dragon Ball character ids to the demo users."""
    users_table = sa.table(
        "users",
        sa.column("email", sa.String),
        sa.column("dragon_ball_ids", postgresql.ARRAY(sa.Integer())),
    )

    # 1 = Goku, 2 = Vegeta, 3 = Piccolo; test@demo.com keeps NULL (no characters)
    demo_dragon_ball_ids = {
        "admin@demo.com": [1, 2, 3],
        "john@demo.com": [1],
        "jane@demo.com": [2, 3],
    }

    for email, dragon_ball_ids in demo_dragon_ball_ids.items():
        op.execute(
            users_table.update()
            .where(users_table.c.email == email)
            .values(dragon_ball_ids=dragon_ball_ids)
        )


def downgrade() -> None:
    """Clear Dragon Ball character ids from the demo users."""
    op.execute(sa.text("UPDATE users SET dragon_ball_ids = NULL WHERE email LIKE '%@demo.com'"))
