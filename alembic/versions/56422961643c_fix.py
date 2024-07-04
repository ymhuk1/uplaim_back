"""fix

Revision ID: 56422961643c
Revises: 6f96a0142212
Create Date: 2024-07-04 08:29:57.569830

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import Inspector

# revision identifiers, used by Alembic.
revision: str = '56422961643c'
down_revision: Union[str, None] = '6f96a0142212'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


revision: str = '56422961643c'
down_revision: Union[str, None] = '6f96a0142212'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = Inspector.from_engine(bind)
    columns = [column['name'] for column in inspector.get_columns('payment_methods')]

    # Check if 'client_id' column exists before adding it
    if 'client_id' not in columns:
        op.add_column('payment_methods', sa.Column('client_id', sa.Integer(), nullable=True))

    # Other auto-generated commands
    op.alter_column('coupons', 'discount',
               existing_type=sa.REAL(),
               type_=sa.Float(precision=2),
               existing_nullable=True)
    op.alter_column('payment_methods', 'method_type',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.create_foreign_key(None, 'payment_methods', 'clients', ['client_id'], ['id'])


def downgrade() -> None:
    # Auto-generated commands for downgrade
    op.drop_constraint(None, 'payment_methods', type_='foreignkey')
    op.alter_column('payment_methods', 'method_type',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.drop_column('payment_methods', 'client_id')
    op.alter_column('coupons', 'discount',
               existing_type=sa.Float(precision=2),
               type_=sa.REAL(),
               existing_nullable=True)
