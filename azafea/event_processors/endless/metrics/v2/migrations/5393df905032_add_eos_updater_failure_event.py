# type: ignore

"""Add eos-updater failure event

Revision ID: 5393df905032
Revises: 2b8c64885884
Create Date: 2020-09-09 15:03:12.496378

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5393df905032'
down_revision = '2b8c64885884'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('updater_failure',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('user_id', sa.BigInteger(), nullable=False),
                    sa.Column('occured_at', sa.DateTime(timezone=True), nullable=False),
                    sa.Column('component', sa.Unicode(), nullable=False),
                    sa.Column('error_message', sa.Unicode(), nullable=False),
                    sa.Column('request_id', sa.Integer(), nullable=True),
                    sa.ForeignKeyConstraint(
                        ['request_id'], ['metrics_request_v2.id'],
                        name=op.f(
                            'fk_updater_failure_request_id_metrics_request_v2'
                        )),
                    sa.PrimaryKeyConstraint(
                        'id',
                        name=op.f('pk_updater_failure')))
    op.create_index(op.f('ix_updater_failure_request_id'),
                    'updater_failure', ['request_id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_updater_failure_request_id'),
                  table_name='updater_failure')
    op.drop_table('updater_failure')
