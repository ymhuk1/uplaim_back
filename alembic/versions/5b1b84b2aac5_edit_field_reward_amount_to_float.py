"""edit field reward.amount to Float

Revision ID: 5b1b84b2aac5
Revises: f7895ee7f969
Create Date: 2024-05-29 19:08:31.939942

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5b1b84b2aac5'
down_revision: Union[str, None] = 'f7895ee7f969'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('coupons', 'discount',
               existing_type=sa.REAL(),
               type_=sa.Float(precision=2),
               existing_nullable=True)
    op.alter_column('reward', 'amount',
               existing_type=sa.INTEGER(),
               type_=sa.Float(precision=2),
               existing_nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('reward', 'amount',
               existing_type=sa.Float(precision=2),
               type_=sa.INTEGER(),
               existing_nullable=True)
    op.alter_column('coupons', 'discount',
               existing_type=sa.Float(precision=2),
               type_=sa.REAL(),
               existing_nullable=True)
    # ### end Alembic commands ###
