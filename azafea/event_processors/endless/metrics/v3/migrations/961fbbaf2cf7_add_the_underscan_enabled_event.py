# type: ignore

"""Add the underscan enabled event

Revision ID: 961fbbaf2cf7
Revises: 5393df905032
Create Date: 2020-09-16 16:15:11.496377

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '961fbbaf2cf7'
down_revision = '5393df905032'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('underscan_enabled',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('user_id', sa.BigInteger(), nullable=False),
                    sa.Column('occured_at', sa.DateTime(timezone=True), nullable=False),
                    sa.Column('request_id', sa.Integer(), nullable=True),
                    sa.ForeignKeyConstraint(
                        ['request_id'], ['metrics_request_v2.id'],
                        name=op.f('fk_underscan_enabled_request_id_metrics_request_v2')),
                    sa.PrimaryKeyConstraint('id', name=op.f('pk_underscan_enabled'))
                    )
    op.create_index(op.f('ix_underscan_enabled_request_id'), 'underscan_enabled', ['request_id'],
                    unique=False)


def downgrade():
    op.drop_index(op.f('ix_underscan_enabled_request_id'), table_name='underscan_enabled')
    op.drop_table('underscan_enabled')
