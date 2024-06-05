"""Add acquiring models

Revision ID: 87b793f35b89
Revises: 
Create Date: 2024-04-13 08:12:25.061773

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '87b793f35b89'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('acquiring_paymentattempts',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('acquiring_paymentmethods',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column('confirmable', sa.Boolean(), server_default='False', nullable=False),
        sa.Column('payment_attempt_id', sa.String(), nullable=False),
        sa.ForeignKeyConstraint(['payment_attempt_id'], ['acquiring_paymentattempts.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('acquiring_paymentoperations',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column('type', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('payment_method_id', sa.String(), nullable=False),
        sa.ForeignKeyConstraint(['payment_method_id'], ['acquiring_paymentmethods.id'], ),
        sa.Index('ix_acquiring_paymentoperations_status', 'status'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table('acquiring_blockevents',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('block_name', sa.String(), nullable=False),
        sa.Column('payment_method_id', sa.String(), nullable=False),
        sa.ForeignKeyConstraint(['payment_method_id'], ['acquiring_paymentmethods.id'], ),
        sa.Index('ix_acquiring_blockevents_status', 'status'),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table('acquiring_transactions',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('external_id', sa.String(), nullable=False),
        sa.Column('timestamp', sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column('raw_data', sa.String(), nullable=False),
        sa.Column('provider_name', sa.String(), nullable=False),
        sa.Column('payment_method_id', sa.String(), nullable=False),
        sa.ForeignKeyConstraint(['payment_method_id'], ['acquiring_paymentmethods.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade() -> None:
    op.drop_table('acquiring_transactions')
    op.drop_table('acquiring_blockevents')
    op.drop_table('acquiring_paymentoperations')
    op.drop_table('acquiring_paymentmethods')
    op.drop_table('acquiring_paymentattempts')
