"""added photo in competition

Revision ID: 7113206a26b7
Revises: 48a7df4e8798
Create Date: 2024-05-21 15:59:53.451511

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7113206a26b7'
down_revision: Union[str, None] = '48a7df4e8798'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('competitions', sa.Column('photo', sa.String(), nullable=True))
    op.alter_column('coupons', 'discount',
               existing_type=sa.REAL(),
               type_=sa.Float(precision=2),
               existing_nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('coupons', 'discount',
               existing_type=sa.Float(precision=2),
               type_=sa.REAL(),
               existing_nullable=True)
    op.drop_column('competitions', 'photo')
    # ### end Alembic commands ###
