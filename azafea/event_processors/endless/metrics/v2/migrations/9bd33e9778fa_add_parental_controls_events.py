# type: ignore

"""Add parental controls events

Revision ID: 9bd33e9778fa
Revises: a6e10c2e3f79
Create Date: 2020-04-21 11:09:12.496378

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '9bd33e9778fa'
down_revision = 'a6e10c2e3f79'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('parental_controls_blocked_flatpak_install',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('user_id', sa.BigInteger(), nullable=False),
                    sa.Column('occured_at', sa.DateTime(timezone=True), nullable=False),
                    sa.Column('app', sa.Unicode(), nullable=False),
                    sa.Column('request_id', sa.Integer(), nullable=True),
                    sa.ForeignKeyConstraint(
                        ['request_id'], ['metrics_request_v2.id'],
                        name=op.f(
                            'fk_parental_controls_blocked_flatpak_install_'
                            'request_id_metrics_request_v2'
                        )),
                    sa.PrimaryKeyConstraint(
                        'id',
                        name=op.f('pk_parental_controls_blocked_flatpak_install')))
    op.create_index(op.f('ix_parental_controls_blocked_flatpak_install_request_id'),
                    'parental_controls_blocked_flatpak_install', ['request_id'], unique=False)

    op.create_table('parental_controls_blocked_flatpak_run',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('user_id', sa.BigInteger(), nullable=False),
                    sa.Column('occured_at', sa.DateTime(timezone=True), nullable=False),
                    sa.Column('app', sa.Unicode(), nullable=False),
                    sa.Column('request_id', sa.Integer(), nullable=True),
                    sa.ForeignKeyConstraint(
                        ['request_id'], ['metrics_request_v2.id'],
                        name=op.f(
                            'fk_parental_controls_blocked_flatpak_run_request_id_metrics_request_v2'
                        )),
                    sa.PrimaryKeyConstraint(
                        'id',
                        name=op.f('pk_parental_controls_blocked_flatpak_run')))
    op.create_index(op.f('ix_parental_controls_blocked_flatpak_run_request_id'),
                    'parental_controls_blocked_flatpak_run', ['request_id'], unique=False)

    op.create_table('parental_controls_changed',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('user_id', sa.BigInteger(), nullable=False),
                    sa.Column('occured_at', sa.DateTime(timezone=True), nullable=False),
                    sa.Column('app_filter_is_whitelist', sa.Boolean(), nullable=False),
                    sa.Column('app_filter', sa.ARRAY(sa.Unicode(), dimensions=1), nullable=False),
                    sa.Column('oars_filter',
                              postgresql.JSONB(astext_type=sa.Text()), nullable=False),
                    sa.Column('allow_user_installation', sa.Boolean(), nullable=False),
                    sa.Column('allow_system_installation', sa.Boolean(), nullable=False),
                    sa.Column('is_administrator', sa.Boolean(), nullable=False),
                    sa.Column('is_initial_setup', sa.Boolean(), nullable=False),
                    sa.Column('request_id', sa.Integer(), nullable=True),
                    sa.ForeignKeyConstraint(
                        ['request_id'], ['metrics_request_v2.id'],
                        name=op.f(
                            'fk_parental_controls_changed_request_id_metrics_request_v2'
                        )),
                    sa.PrimaryKeyConstraint('id', name=op.f('pk_parental_controls_changed')))
    op.create_index(op.f('ix_parental_controls_changed_request_id'),
                    'parental_controls_changed', ['request_id'], unique=False)

    op.create_table('parental_controls_enabled',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('user_id', sa.BigInteger(), nullable=False),
                    sa.Column('occured_at', sa.DateTime(timezone=True), nullable=False),
                    sa.Column('enabled', sa.Boolean(), nullable=False),
                    sa.Column('request_id', sa.Integer(), nullable=True),
                    sa.ForeignKeyConstraint(
                        ['request_id'], ['metrics_request_v2.id'],
                        name=op.f(
                            'fk_parental_controls_enabled_request_id_metrics_request_v2'
                        )),
                    sa.PrimaryKeyConstraint('id', name=op.f('pk_parental_controls_enabled')))
    op.create_index(op.f('ix_parental_controls_enabled_request_id'),
                    'parental_controls_enabled', ['request_id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_parental_controls_blocked_flatpak_install_request_id'),
                  table_name='parental_controls_blocked_flatpak_install')
    op.drop_table('parental_controls_blocked_flatpak_install')

    op.drop_index(op.f('ix_parental_controls_blocked_flatpak_run_request_id'),
                  table_name='parental_controls_blocked_flatpak_run')
    op.drop_table('parental_controls_blocked_flatpak_run')

    op.drop_index(op.f('ix_parental_controls_changed_request_id'),
                  table_name='parental_controls_changed')
    op.drop_table('parental_controls_changed')

    op.drop_index(op.f('ix_parental_controls_enabled_request_id'),
                  table_name='parental_controls_enabled')
    op.drop_table('parental_controls_enabled')
