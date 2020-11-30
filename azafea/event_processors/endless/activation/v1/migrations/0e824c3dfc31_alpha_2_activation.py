# type: ignore

"""Allow only alpha2 country codes in activation_v1 table

Revision ID: 0e824c3dfc31
Revises: a9e5d0f9b1cf
Create Date: 2020-05-14 17:36:27.539762

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = '0e824c3dfc31'
down_revision = 'a9e5d0f9b1cf'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint('ck_activation_v1_ck_activation_v1_country_code_2_3_chars', 'activation_v1')
    op.create_check_constraint(
        op.f('ck_activation_v1_country_code_2_chars'), 'activation_v1', 'char_length(country) = 2')


def downgrade():
    op.drop_constraint('ck_activation_v1_country_code_2_chars', 'activation_v1')
    op.create_check_constraint(
        'ck_activation_v1_country_code_2_3_chars', 'activation_v1',
        'char_length(country) in (2, 3)')
