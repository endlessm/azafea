# type: ignore

"""Initial db creation

Revision ID: 0b3c2b3ae466
Revises:
Create Date: 2019-12-04 09:12:47.342337

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0b3c2b3ae466'
down_revision = None
branch_labels = ('ping-1',)
depends_on = None


def upgrade():
    from azafea.model import NullableBoolean

    conn = op.get_bind()
    inspector = sa.inspect(conn)
    tables = inspector.get_table_names()

    if 'ping_configuration_v1' not in tables:
        op.create_table('ping_configuration_v1',
                        sa.Column('id', sa.Integer(), nullable=False),
                        sa.Column('image', sa.Unicode(), nullable=False),
                        sa.Column('vendor', sa.Unicode(), nullable=False),
                        sa.Column('product', sa.Unicode(), nullable=False),
                        sa.Column('dualboot', NullableBoolean(), server_default='unknown',
                                  nullable=False),
                        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
                        sa.PrimaryKeyConstraint('id', name=op.f('pk_ping_configuration_v1')),
                        sa.UniqueConstraint(
                            'image', 'vendor', 'product', 'dualboot',
                            name='uq_ping_configuration_v1_image_vendor_product_dualboot'))
        op.create_index(op.f('ix_ping_configuration_v1_created_at'), 'ping_configuration_v1',
                        ['created_at'], unique=False)
        op.create_table('ping_v1',
                        sa.Column('id', sa.Integer(), nullable=False),
                        sa.Column('config_id', sa.Integer(), nullable=False),
                        sa.Column('release', sa.Unicode(), nullable=False),
                        sa.Column('count', sa.Integer(), nullable=False),
                        sa.Column('country', sa.Unicode(length=3), nullable=True),
                        sa.Column('metrics_enabled', sa.Boolean(), nullable=True),
                        sa.Column('metrics_environment', sa.Unicode(), nullable=True),
                        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
                        sa.CheckConstraint('char_length(country) = 3',
                                           name=op.f('ck_ping_v1_country_code_3_chars')),
                        sa.CheckConstraint('count >= 0', name=op.f('ck_ping_v1_count_positive')),
                        sa.ForeignKeyConstraint(
                            ['config_id'], ['ping_configuration_v1.id'],
                            name=op.f('fk_ping_v1_config_id_ping_configuration_v1')),
                        sa.PrimaryKeyConstraint('id', name=op.f('pk_ping_v1')))
        op.create_index(op.f('ix_ping_v1_config_id'), 'ping_v1', ['config_id'], unique=False)
        op.create_index(op.f('ix_ping_v1_created_at'), 'ping_v1', ['created_at'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_ping_v1_created_at'), table_name='ping_v1')
    op.drop_index(op.f('ix_ping_v1_config_id'), table_name='ping_v1')
    op.drop_table('ping_v1')
    op.drop_index(op.f('ix_ping_configuration_v1_created_at'), table_name='ping_configuration_v1')
    op.drop_table('ping_configuration_v1')
