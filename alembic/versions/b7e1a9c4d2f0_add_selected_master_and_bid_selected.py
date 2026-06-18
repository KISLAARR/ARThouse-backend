"""add selected master to projects and SELECTED bid status

Revision ID: b7e1a9c4d2f0
Revises: d841452b54a5
Create Date: 2026-06-18 12:00:00.000000

Добавляет:
  - marketplace_projects.selected_master_id (FK users, ON DELETE SET NULL)
  - marketplace_projects.selected_master_name
  - значение 'SELECTED' в enum masterbidstatus (выбранный заказчиком отклик)
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b7e1a9c4d2f0'
down_revision: Union[str, Sequence[str], None] = 'd841452b54a5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        'marketplace_projects',
        sa.Column('selected_master_id', sa.Integer(), nullable=True)
    )
    op.add_column(
        'marketplace_projects',
        sa.Column('selected_master_name', sa.String(length=160), nullable=True)
    )
    op.create_foreign_key(
        'fk_marketplace_projects_selected_master_id_users',
        'marketplace_projects',
        'users',
        ['selected_master_id'],
        ['id'],
        ondelete='SET NULL'
    )

    # Новое значение enum. SQLAlchemy хранит ИМЯ члена enum ('SELECTED').
    # ADD VALUE нельзя выполнять внутри транзакции (до PG12) — autocommit_block.
    with op.get_context().autocommit_block():
        op.execute("ALTER TYPE masterbidstatus ADD VALUE IF NOT EXISTS 'SELECTED'")


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        'fk_marketplace_projects_selected_master_id_users',
        'marketplace_projects',
        type_='foreignkey'
    )
    op.drop_column('marketplace_projects', 'selected_master_name')
    op.drop_column('marketplace_projects', 'selected_master_id')
    # Удаление значения из enum в PostgreSQL не поддерживается — оставляем 'SELECTED'.
