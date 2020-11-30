# type: ignore

"""Allow only alpha2 country codes in ping_v1 table

Revision ID: 9214d7c1d7d9
Revises: f2d6141dbece
Create Date: 2020-05-14 17:24:17.029109

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = '9214d7c1d7d9'
down_revision = 'f2d6141dbece'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint('ck_ping_v1_ck_ping_v1_country_code_2_3_chars', 'ping_v1')
    op.create_check_constraint(
        op.f('ck_ping_v1_country_code_2_chars'), 'ping_v1', 'char_length(country) = 2')


def downgrade():
    op.drop_constraint('ck_ping_v1_country_code_2_chars', 'ping_v1')
    op.create_check_constraint(
        'ck_ping_v1_country_code_2_3_chars', 'ping_v1', 'char_length(country) in (2, 3)')
