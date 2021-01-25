# type: ignore

"""Add machine location columns

Revision ID: 991574509c57
Revises: 98078d059259
Create Date: 2020-12-03 12:33:17.219965

"""
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql.expression import text
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '991574509c57'
down_revision = '98078d059259'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('metrics_machine', sa.Column('location', JSONB(), nullable=True))
    op.add_column('metrics_machine', sa.Column('location_city', sa.Unicode(), nullable=True))
    op.add_column('metrics_machine', sa.Column('location_country', sa.Unicode(), nullable=True))
    op.add_column('metrics_machine', sa.Column('location_facility', sa.Unicode(), nullable=True))
    op.add_column('metrics_machine', sa.Column('location_id', sa.Unicode(), nullable=True))
    op.add_column('metrics_machine', sa.Column('location_state', sa.Unicode(), nullable=True))
    op.add_column('metrics_machine', sa.Column('location_street', sa.Unicode(), nullable=True))
    op.create_index(
        op.f('ix_metrics_machine_location_city'), 'metrics_machine', ['location_city'],
        postgresql_where=text("location_city is not null"))
    op.create_index(
        op.f('ix_metrics_machine_location_country'), 'metrics_machine', ['location_country'],
        postgresql_where=text("location_country is not null"))
    op.create_index(
        op.f('ix_metrics_machine_location_facility'), 'metrics_machine', ['location_facility'],
        postgresql_where=text("location_facility is not null"))
    op.create_index(
        op.f('ix_metrics_machine_location_id'), 'metrics_machine', ['location_id'],
        postgresql_where=text("location_id is not null"))
    op.create_index(
        op.f('ix_metrics_machine_location_state'), 'metrics_machine', ['location_state'],
        postgresql_where=text("location_state is not null"))
    op.create_index(
        op.f('ix_metrics_machine_location_street'), 'metrics_machine', ['location_street'],
        postgresql_where=text("location_street is not null"))
    op.execute('''
      INSERT INTO
        metrics_machine
        (
          location,
          location_street,
          location_state,
          location_id,
          location_facility,
          location_country,
          location_city,
          machine_id
        )
        (
          SELECT
            location,
            location_street,
            location_state,
            location_id,
            location_facility,
            location_country,
            location_city,
            machine_id
          FROM (
            SELECT
              info AS location,
              info->'street' AS location_street,
              info->'state' AS location_state,
              info->'id' AS location_id,
              info->'facility' AS location_facility,
              info->'country' AS location_country,
              info->'city' AS location_city,
              machine_id,
              rank() OVER (PARTITION BY machine_id ORDER BY occured_at DESC) AS rank
            FROM
              location_event
            JOIN
              metrics_request_v2
            ON
              request_id=metrics_request_v2.id
            ORDER BY occured_at
          ) AS ranked_location
          WHERE
            rank = 1
        )
        ON CONFLICT ON CONSTRAINT
          uq_metrics_machine_machine_id
        DO UPDATE SET
          location=excluded.location,
          location_street=excluded.location_street,
          location_state=excluded.location_state,
          location_id=excluded.location_id,
          location_facility=excluded.location_facility,
          location_country=excluded.location_country,
          location_city=excluded.location_country;
    ''')


def downgrade():
    op.drop_index(op.f('ix_metrics_machine_location_street'), table_name='metrics_machine')
    op.drop_index(op.f('ix_metrics_machine_location_state'), table_name='metrics_machine')
    op.drop_index(op.f('ix_metrics_machine_location_id'), table_name='metrics_machine')
    op.drop_index(op.f('ix_metrics_machine_location_facility'), table_name='metrics_machine')
    op.drop_index(op.f('ix_metrics_machine_location_country'), table_name='metrics_machine')
    op.drop_index(op.f('ix_metrics_machine_location_city'), table_name='metrics_machine')
    op.drop_column('metrics_machine', 'location_street')
    op.drop_column('metrics_machine', 'location_state')
    op.drop_column('metrics_machine', 'location_id')
    op.drop_column('metrics_machine', 'location_facility')
    op.drop_column('metrics_machine', 'location_country')
    op.drop_column('metrics_machine', 'location_city')
    op.drop_column('metrics_machine', 'location')
