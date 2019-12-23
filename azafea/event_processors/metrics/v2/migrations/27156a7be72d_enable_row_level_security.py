# type: ignore

"""Enable row-level security

Revision ID: 27156a7be72d
Revises: 7f4c0154d6cd
Create Date: 2019-12-23 10:29:06.431725

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = '27156a7be72d'
down_revision = '7f4c0154d6cd'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('ALTER TABLE metrics_request_v2 ENABLE ROW LEVEL SECURITY')


def downgrade():
    op.execute('ALTER TABLE metrics_request_v2 DISABLE ROW LEVEL SECURITY')
