# type: ignore

"""Allow alpha2 and alpha3 country codes in activation_v1 table

Revision ID: a9e5d0f9b1cf
Revises: 3bf359e3c86c
Create Date: 2020-05-14 15:14:02.100409

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = 'a9e5d0f9b1cf'
down_revision = '3bf359e3c86c'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint('ck_activation_v1_country_code_3_chars', 'activation_v1')
    op.create_check_constraint(
        'ck_activation_v1_country_code_2_3_chars', 'activation_v1',
        'char_length(country) in (2, 3)')


def downgrade():
    op.drop_constraint('ck_activation_v1_country_code_2_3_chars', 'activation_v1')
    op.create_check_constraint(
        'ck_activation_v1_country_code_3_chars', 'activation_v1', 'char_length(country) = 3')
