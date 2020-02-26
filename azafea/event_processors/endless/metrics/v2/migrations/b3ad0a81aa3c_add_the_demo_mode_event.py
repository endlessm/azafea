# type: ignore

"""Add the demo mode event

Revision ID: b3ad0a81aa3c
Revises: d99f33473540
Create Date: 2020-02-24 13:08:11.496377

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b3ad0a81aa3c'
down_revision = 'd99f33473540'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('entered_demo_mode',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('user_id', sa.BigInteger(), nullable=False),
                    sa.Column('occured_at', sa.DateTime(timezone=True), nullable=False),
                    sa.Column('request_id', sa.Integer(), nullable=True),
                    sa.ForeignKeyConstraint(
                        ['request_id'], ['metrics_request_v2.id'],
                        name=op.f('fk_entered_demo_mode_request_id_metrics_request_v2')),
                    sa.PrimaryKeyConstraint('id', name=op.f('pk_entered_demo_mode'))
                    )
    op.create_index(op.f('ix_entered_demo_mode_request_id'), 'entered_demo_mode', ['request_id'],
                    unique=False)


def downgrade():
    op.drop_index(op.f('ix_entered_demo_mode_request_id'), table_name='entered_demo_mode')
    op.drop_table('entered_demo_mode')
