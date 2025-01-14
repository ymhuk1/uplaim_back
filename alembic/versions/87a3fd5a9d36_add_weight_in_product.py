"""add weight in product

Revision ID: 87a3fd5a9d36
Revises: f600d2bcf860
Create Date: 2024-08-16 14:10:25.433282

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '87a3fd5a9d36'
down_revision: Union[str, None] = 'f600d2bcf860'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('coupons', 'discount',
               existing_type=sa.REAL(),
               type_=sa.Float(precision=2),
               existing_nullable=True)
    op.alter_column('orders', 'amount',
               existing_type=sa.REAL(),
               type_=sa.Float(precision=2),
               existing_nullable=True)
    op.alter_column('orders', 'amount_of_delivery',
               existing_type=sa.REAL(),
               type_=sa.Float(precision=2),
               existing_nullable=True)
    op.add_column('products', sa.Column('weight', sa.String(), nullable=True))
    op.alter_column('virtual_account', 'balance',
               existing_type=sa.REAL(),
               type_=sa.Float(precision=2),
               existing_nullable=True)
    op.alter_column('virtual_account', 'up_balance',
               existing_type=sa.REAL(),
               type_=sa.Float(precision=2),
               existing_nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('virtual_account', 'up_balance',
               existing_type=sa.Float(precision=2),
               type_=sa.REAL(),
               existing_nullable=True)
    op.alter_column('virtual_account', 'balance',
               existing_type=sa.Float(precision=2),
               type_=sa.REAL(),
               existing_nullable=True)
    op.drop_column('products', 'weight')
    op.alter_column('orders', 'amount_of_delivery',
               existing_type=sa.Float(precision=2),
               type_=sa.REAL(),
               existing_nullable=True)
    op.alter_column('orders', 'amount',
               existing_type=sa.Float(precision=2),
               type_=sa.REAL(),
               existing_nullable=True)
    op.alter_column('coupons', 'discount',
               existing_type=sa.Float(precision=2),
               type_=sa.REAL(),
               existing_nullable=True)
    # ### end Alembic commands ###
