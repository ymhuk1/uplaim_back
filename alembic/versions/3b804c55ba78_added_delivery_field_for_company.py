"""added delivery field for company

Revision ID: 3b804c55ba78
Revises: 3dd55d0ccfac
Create Date: 2024-08-09 11:20:08.370446

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3b804c55ba78'
down_revision: Union[str, None] = '3dd55d0ccfac'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('companies', sa.Column('delivery', sa.Boolean(), nullable=True))
    op.add_column('companies', sa.Column('time_to_delivery', sa.String(), nullable=True))
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
    op.drop_column('companies', 'time_to_delivery')
    op.drop_column('companies', 'delivery')
    # ### end Alembic commands ###