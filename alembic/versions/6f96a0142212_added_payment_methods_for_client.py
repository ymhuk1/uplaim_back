"""added payment_methods for client

Revision ID: 6f96a0142212
Revises: d8262412516f
Create Date: 2024-06-30 18:20:31.218610

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '6f96a0142212'
down_revision: Union[str, None] = 'd8262412516f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('coupons', 'discount',
               existing_type=sa.REAL(),
               type_=sa.Float(precision=2),
               existing_nullable=True)

    # Check if the payment_methods table exists before making changes to it
    conn = op.get_bind()
    table_exists = conn.execute(
        sa.text("SELECT EXISTS (SELECT FROM pg_tables WHERE schemaname = 'public' AND tablename = 'payment_methods');")
    ).scalar()

    if not table_exists:
        # Create the payment_methods table if it doesn't exist
        op.create_table(
            'payment_methods',
            sa.Column('id', sa.Integer, primary_key=True),
            sa.Column('method_type', sa.String(), nullable=False),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.Column('updated_at', sa.DateTime(), nullable=True)
        )

    # Now add the new columns to the payment_methods table
    op.add_column('payment_methods', sa.Column('card_number', sa.String(), nullable=True))
    op.add_column('payment_methods', sa.Column('expiry_data', sa.String(), nullable=True))
    op.add_column('payment_methods', sa.Column('cvv', sa.String(), nullable=True))
    op.add_column('payment_methods', sa.Column('sbp_phone', sa.String(), nullable=True))
    op.add_column('payment_methods', sa.Column('bik', sa.String(), nullable=True))
    op.add_column('payment_methods', sa.Column('visible', sa.Boolean(), nullable=True))
    op.add_column('payment_methods', sa.Column('is_primary', sa.Boolean(), nullable=True))
    # op.add_column('payment_methods', sa.Column('created_at', sa.DateTime(), nullable=True))
    # op.add_column('payment_methods', sa.Column('updated_at', sa.DateTime(), nullable=True))


    # Drop the indexes if they exist
    if conn.execute(sa.text("SELECT 1 FROM pg_indexes WHERE indexname = 'ix_payment_methods_id'")).scalar():
        op.drop_index('ix_payment_methods_id', table_name='payment_methods')
    if conn.execute(sa.text("SELECT 1 FROM pg_indexes WHERE indexname = 'ix_payment_methods_method_type'")).scalar():
        op.drop_index('ix_payment_methods_method_type', table_name='payment_methods')

    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index('ix_payment_methods_method_type', 'payment_methods', ['method_type'], unique=False)
    op.create_index('ix_payment_methods_id', 'payment_methods', ['id'], unique=False)
    op.drop_column('payment_methods', 'updated_at')
    op.drop_column('payment_methods', 'created_at')
    op.drop_column('payment_methods', 'is_primary')
    op.drop_column('payment_methods', 'visible')
    op.drop_column('payment_methods', 'bik')
    op.drop_column('payment_methods', 'sbp_phone')
    op.drop_column('payment_methods', 'cvv')
    op.drop_column('payment_methods', 'expiry_data')
    op.drop_column('payment_methods', 'card_number')
    op.alter_column('coupons', 'discount',
               existing_type=sa.Float(precision=2),
               type_=sa.REAL(),
               existing_nullable=True)
    op.create_table('card_payments',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('card_number', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('cvv', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('card_holder', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('expiry_date', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('payment_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('updated_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['payment_id'], ['payment_methods.id'], name='card_payments_payment_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='card_payments_pkey')
    )
    op.create_index('ix_card_payments_id', 'card_payments', ['id'], unique=False)
    op.create_table('sbp_payments',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('phone_number', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('payment_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('updated_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['payment_id'], ['payment_methods.id'], name='sbp_payments_payment_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='sbp_payments_pkey')
    )
    op.create_index('ix_sbp_payments_id', 'sbp_payments', ['id'], unique=False)
    # ### end Alembic commands ###