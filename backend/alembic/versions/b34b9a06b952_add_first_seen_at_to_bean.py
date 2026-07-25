"""Create initial tables and add first_seen_at to Bean

Revision ID: b34b9a06b952
Revises: 
Create Date: 2026-07-25 13:28:24.747725

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector


# revision identifiers, used by Alembic.
revision: str = 'b34b9a06b952'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    tables = inspector.get_table_names()

    if 'stores' not in tables:
        op.create_table(
            'stores',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('name', sa.String(length=256), nullable=False),
            sa.Column('url', sa.String(length=2048), nullable=True),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('name')
        )

    if 'beans' not in tables:
        op.create_table(
            'beans',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('store_id', sa.Integer(), nullable=False),
            sa.Column('name', sa.String(length=256), nullable=False),
            sa.Column('url', sa.String(length=2048), nullable=False),
            sa.Column('image', sa.String(length=2048), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
            sa.Column('first_seen_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
            sa.Column('last_seen', sa.DateTime(timezone=True), nullable=True),
            sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
            sa.ForeignKeyConstraint(['store_id'], ['stores.id'], ),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('store_id', 'name', name='_store_name_uc')
        )
    else:
        columns = [c['name'] for c in inspector.get_columns('beans')]
        if 'first_seen_at' not in columns:
            with op.batch_alter_table('beans', schema=None) as batch_op:
                batch_op.add_column(sa.Column('first_seen_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False))

    if 'variants' not in tables:
        op.create_table(
            'variants',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('grams', sa.Integer(), nullable=False),
            sa.Column('price', sa.Numeric(precision=10, scale=2), nullable=True),
            sa.Column('price_per_gram', sa.Numeric(precision=10, scale=3), nullable=True),
            sa.Column('bean_id', sa.Integer(), nullable=False),
            sa.ForeignKeyConstraint(['bean_id'], ['beans.id'], ),
            sa.PrimaryKeyConstraint('id')
        )


def downgrade() -> None:
    op.drop_table('variants')
    op.drop_table('beans')
    op.drop_table('stores')
