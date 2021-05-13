# type: ignore

"""Add image functions

Revision ID: 7f4c0154d6cd
Revises: 33c19f68197d
Create Date: 2019-12-11 14:30:48.877166

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7f4c0154d6cd'
down_revision = '33c19f68197d'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('CREATE FUNCTION get_image_personality(_machine_id text) RETURNS text\n'
               '  LANGUAGE plpgsql IMMUTABLE\n'
               '  AS $$\n'
               '    BEGIN\n'
               '      RETURN (\n'
               "        SELECT reverse(split_part(reverse(image_id), '.', 1)) AS personality\n"
               '          FROM metrics_machine\n'
               '          WHERE metrics_machine.machine_id = _machine_id\n'
               '      ) ;\n'
               '    END;\n'
               '  $$;')
    op.create_index(op.f('ix_metrics_request_v2_image_personality'), 'metrics_request_v2',
                    [sa.text('get_image_personality(machine_id)')], unique=False)
    op.execute('CREATE FUNCTION get_image_product(_machine_id text) RETURNS text\n'
               '  LANGUAGE plpgsql IMMUTABLE\n'
               '  AS $$\n'
               '    BEGIN\n'
               '      RETURN (\n'
               "        SELECT split_part(image_id, '-', 1) AS product\n"
               '          FROM metrics_machine\n'
               '          WHERE metrics_machine.machine_id = _machine_id\n'
               '      ) ;\n'
               '    END;\n'
               '  $$;')
    op.create_index(op.f('ix_metrics_request_v2_image_product'), 'metrics_request_v2',
                    [sa.text('get_image_product(machine_id)')], unique=False)


def downgrade():
    op.execute('DROP FUNCTION get_image_product;')
    op.execute('DROP FUNCTION get_image_personality;')
