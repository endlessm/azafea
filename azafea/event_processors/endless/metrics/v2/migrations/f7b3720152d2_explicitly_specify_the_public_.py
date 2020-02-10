# type: ignore

"""Explicitly specify the public tablespace for functions, and declare them parallel-safe

Revision ID: f7b3720152d2
Revises: 7f4c0154d6cd
Create Date: 2020-01-21 12:56:28.341377

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f7b3720152d2'
down_revision = '7f4c0154d6cd'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_index('ix_metrics_request_v2_image_personality')
    op.execute('CREATE OR REPLACE FUNCTION get_image_personality(_machine_id text) RETURNS text\n'
               '  LANGUAGE plpgsql IMMUTABLE PARALLEL SAFE\n'
               '  AS $$\n'
               '    BEGIN\n'
               '      RETURN (\n'
               "        SELECT reverse(split_part(reverse(image_id), '.', 1)) AS personality\n"
               '          FROM public.metrics_machine\n'
               '          WHERE metrics_machine.machine_id = _machine_id\n'
               '      ) ;\n'
               '    END;\n'
               '  $$;')
    op.create_index(op.f('ix_metrics_request_v2_image_personality'), 'metrics_request_v2',
                    [sa.text('get_image_personality(machine_id)')], unique=False)

    op.drop_index('ix_metrics_request_v2_image_product')
    op.execute('CREATE OR REPLACE FUNCTION get_image_product(_machine_id text) RETURNS text\n'
               '  LANGUAGE plpgsql IMMUTABLE PARALLEL SAFE\n'
               '  AS $$\n'
               '    BEGIN\n'
               '      RETURN (\n'
               "        SELECT split_part(image_id, '-', 1) AS product\n"
               '          FROM public.metrics_machine\n'
               '          WHERE metrics_machine.machine_id = _machine_id\n'
               '      ) ;\n'
               '    END;\n'
               '  $$;')
    op.create_index(op.f('ix_metrics_request_v2_image_product'), 'metrics_request_v2',
                    [sa.text('get_image_product(machine_id)')], unique=False)


def downgrade():
    op.drop_index('ix_metrics_request_v2_image_personality')
    op.execute('CREATE OR REPLACE FUNCTION get_image_personality(_machine_id text) RETURNS text\n'
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

    op.drop_index('ix_metrics_request_v2_image_product')
    op.execute('CREATE OR REPLACE FUNCTION get_image_product(_machine_id text) RETURNS text\n'
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
