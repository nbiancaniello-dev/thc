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

    demo_users = [
        ('admin', 'admin@demo.com', password_hash.hash('admin123')),
        ('john_doe', 'john@demo.com', password_hash.hash('password123')),
        ('jane_smith', 'jane@demo.com', password_hash.hash('securepass456')),
        ('test_user', 'test@demo.com', password_hash.hash('testpass789')),
    ]

    for username, email, password_hash_val in demo_users:
        op.execute(
            sa.text(
                "INSERT INTO users (username, email, password_hash) VALUES (:username, :email, :password_hash)"
            ),
            {"username": username, "email": email, "password_hash": password_hash_val}
        )


def downgrade() -> None:
    """Remove demo users."""
    op.execute(sa.text("DELETE FROM users WHERE email LIKE '%@demo.com'"))
