"""added field push in client

Revision ID: 3dd55d0ccfac
Revises: e0e43bfffb4c
Create Date: 2024-07-23 08:42:49.631045

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3dd55d0ccfac'
down_revision: Union[str, None] = 'e0e43bfffb4c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('coupons', 'discount',
               existing_type=sa.REAL(),
               type_=sa.Float(precision=2),
               existing_nullable=True)
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
    op.alter_column('coupons', 'discount',
               existing_type=sa.Float(precision=2),
               type_=sa.REAL(),
               existing_nullable=True)
    # ### end Alembic commands ###
