# type: ignore

"""Initial db creation

Revision ID: 3666122efd41
Revises:
Create Date: 2019-12-03 15:38:47.707263

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector


# revision identifiers, used by Alembic.
revision = '3666122efd41'
down_revision = None
branch_labels = ('activation-1',)
depends_on = None


def upgrade():
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    tables = inspector.get_table_names()

    if 'activation_v1' not in tables:
        op.create_table('activation_v1',
                        sa.Column('id', sa.Integer(), nullable=False),
                        sa.Column('image', sa.Unicode(), nullable=False),
                        sa.Column('vendor', sa.Unicode(), nullable=False),
                        sa.Column('product', sa.Unicode(), nullable=False),
                        sa.Column('release', sa.Unicode(), nullable=False),
                        sa.Column('serial', sa.Unicode(), nullable=True),
                        sa.Column('dualboot', sa.Boolean(), nullable=True),
                        sa.Column('live', sa.Boolean(), nullable=True),
                        sa.Column('mac_hash', sa.BigInteger(), nullable=True),
                        sa.Column('country', sa.Unicode(length=3), nullable=True),
                        sa.Column('region', sa.Unicode(), nullable=True),
                        sa.Column('city', sa.Unicode(), nullable=True),
                        sa.Column('latitude', sa.Numeric(), nullable=True),
                        sa.Column('longitude', sa.Numeric(), nullable=True),
                        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
                        sa.CheckConstraint('char_length(country) = 3',
                                           name=op.f('ck_activation_v1_country_code_3_chars')),
                        sa.PrimaryKeyConstraint('id', name=op.f('pk_activation_v1')))
        op.create_index(op.f('ix_activation_v1_created_at'), 'activation_v1', ['created_at'],
                        unique=False)


def downgrade():
    op.drop_index(op.f('ix_activation_v1_created_at'), table_name='activation_v1')
    op.drop_table('activation_v1')
