"""Seed initial users for demo

Revision ID: b58c742cf003
Revises: a58c742cf002
Create Date: 2026-10-26 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from pwdlib import PasswordHash

# revision identifiers, used by Alembic.
revision: str = 'b58c742cf003'
down_revision: Union[str, Sequence[str], None] = 'a58c742cf002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Seed demo users."""
    password_hash = PasswordHash.recommended()

    users_table = sa.table(
        "users",
        sa.column("username", sa.String),
        sa.column("email", sa.String),
        sa.column("password_hash", sa.String),
    )

    demo_users = [
        {"username": "admin", "email": "admin@demo.com", "password_hash": password_hash.hash("admin123")},
        {"username": "john_doe", "email": "john@demo.com", "password_hash": password_hash.hash("password123")},
        {"username": "jane_smith", "email": "jane@demo.com", "password_hash": password_hash.hash("securepass456")},
        {"username": "test_user", "email": "test@demo.com", "password_hash": password_hash.hash("testpass789")},
    ]

    op.bulk_insert(users_table, demo_users)


def downgrade() -> None:
    """Remove demo users."""
    op.execute(sa.text("DELETE FROM users WHERE email LIKE '%@demo.com'"))
