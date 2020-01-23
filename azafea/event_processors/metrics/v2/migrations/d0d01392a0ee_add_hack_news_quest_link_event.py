# type: ignore

"""Add Hack news quest link event

Revision ID: d0d01392a0ee
Revises: f7b3720152d2
Create Date: 2020-01-23 10:52:42.207139

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd0d01392a0ee'
down_revision = 'f7b3720152d2'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('hack_clubhouse_news_quest_link',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('user_id', sa.BigInteger(), nullable=False),
                    sa.Column('occured_at', sa.DateTime(timezone=True), nullable=False),
                    sa.Column('character', sa.Unicode(), nullable=False),
                    sa.Column('quest', sa.Unicode(), nullable=False),
                    sa.Column('request_id', sa.Integer(), nullable=True),
                    sa.ForeignKeyConstraint(
                        ['request_id'], ['metrics_request_v2.id'],
                        name=op.f(
                            'fk_hack_clubhouse_news_quest_link_request_id_metrics_request_v2')),
                    sa.PrimaryKeyConstraint('id', name=op.f('pk_hack_clubhouse_news_quest_link')))
    op.create_index(op.f('ix_hack_clubhouse_news_quest_link_request_id'),
                    'hack_clubhouse_news_quest_link', ['request_id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_hack_clubhouse_news_quest_link_request_id'),
                  table_name='hack_clubhouse_news_quest_link')
    op.drop_table('hack_clubhouse_news_quest_link')
