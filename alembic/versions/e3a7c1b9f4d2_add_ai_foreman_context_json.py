"""add context_json to ai_foreman_threads

Revision ID: e3a7c1b9f4d2
Revises: b7e1a9c4d2f0
Create Date: 2026-06-18 19:00:00.000000

Состояние диалога ИИ-прораба (object_card + stage + history) хранится
в ai_foreman_threads.context_json (JSONB), чтобы тред помнил контекст.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'e3a7c1b9f4d2'
down_revision: Union[str, Sequence[str], None] = 'b7e1a9c4d2f0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        'ai_foreman_threads',
        sa.Column('context_json', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('ai_foreman_threads', 'context_json')
