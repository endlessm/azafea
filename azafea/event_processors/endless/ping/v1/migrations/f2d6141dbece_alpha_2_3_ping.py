# type: ignore

"""Allow alpha2 and alpha3 country codes in ping_v1 table

Revision ID: f2d6141dbece
Revises: 439e90a6874a
Create Date: 2020-05-14 15:13:41.564538

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = 'f2d6141dbece'
down_revision = '439e90a6874a'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint('ck_ping_v1_country_code_3_chars', 'ping_v1')
    op.create_check_constraint(
        'ck_ping_v1_country_code_2_3_chars', 'ping_v1', 'char_length(country) in (2, 3)')


def downgrade():
    op.drop_constraint('ck_ping_v1_country_code_2_3_chars', 'ping_v1')
    op.create_check_constraint(
        'ck_ping_v1_country_code_3_chars', 'ping_v1', 'char_length(country) = 3')
