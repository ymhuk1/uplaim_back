"""update date_end in competition to Date

Revision ID: 652bf9c8dc9c
Revises: fe5f02cbcd46
Create Date: 2024-05-30 15:28:12.981107

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '652bf9c8dc9c'
down_revision: Union[str, None] = 'fe5f02cbcd46'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('competitions', 'date_end',
               existing_type=postgresql.TIMESTAMP(),
               type_=sa.Date(),
               existing_nullable=True)
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
    op.alter_column('competitions', 'date_end',
               existing_type=sa.Date(),
               type_=postgresql.TIMESTAMP(),
               existing_nullable=True)
    # ### end Alembic commands ###
