# type: ignore

"""Add cc automatic updates event

Revision ID: 7e12d8f42f28
Revises: 961fbbaf2cf7
Create Date: 2020-10-22 22:54:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '7e12d8f42f28'
down_revision = '961fbbaf2cf7'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('control_center_automatic_updates',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('user_id', sa.BigInteger(), nullable=False),
                    sa.Column('occured_at', sa.DateTime(timezone=True), nullable=False),
                    sa.Column('allow_downloads_when_metered', sa.Boolean(), nullable=False),
                    sa.Column('automatic_updates_enabled', sa.Boolean(), nullable=False),
                    sa.Column('tariff_enabled', sa.Boolean(), nullable=False),
                    sa.Column('tariff_variant',
                              postgresql.JSONB(astext_type=sa.Text()), nullable=False),
                    sa.Column('request_id', sa.Integer(), nullable=True),
                    sa.ForeignKeyConstraint(
                        ['request_id'], ['metrics_request_v2.id'],
                        name=op.f(
                            'fk_control_center_automatic_updates_request_id_metrics_request_v2'
                        )),
                    sa.PrimaryKeyConstraint(
                        'id',
                        name=op.f('pk_control_center_automatic_updates')))
    op.create_index(op.f('ix_control_center_automatic_updates_request_id'),
                    'control_center_automatic_updates', ['request_id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_control_center_automatic_updates_request_id'),
                  table_name='control_center_automatic_updates')
    op.drop_table('control_center_automatic_updates')
