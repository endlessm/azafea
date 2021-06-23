# type: ignore

"""Remove region and city and add constraints on latitude and longitude

Revision ID: 81cf792f49b2
Revises: 3ce72dccdef8
Create Date: 2021-06-17 12:49:31.415945

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '81cf792f49b2'
down_revision = '3ce72dccdef8'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column('activation_v1', 'city')
    op.drop_column('activation_v1', 'region')

    op.execute(
        'UPDATE activation_v1 \n'
        'SET latitude = CASE WHEN latitude=90 THEN 89.5 ELSE floor(latitude)+0.5 END, \n'
        '   longitude = CASE WHEN longitude=180 THEN 179.5 ELSE floor(longitude)+0.5 END;'
    )

    op.execute(
        'ALTER TABLE activation_v1 \n'
        'ADD CONSTRAINT latitude_precision_reduced CHECK (latitude = floor(latitude)+0.5);'
    )
    op.execute(
        'ALTER TABLE activation_v1 \n'
        'ADD CONSTRAINT longitude_precision_reduced CHECK (latitude = floor(latitude)+0.5);'
    )


def downgrade():
    op.add_column(
        'activation_v1', sa.Column('region', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column(
        'activation_v1', sa.Column('city', sa.VARCHAR(), autoincrement=False, nullable=True))
