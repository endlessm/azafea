# type: ignore

"""On channel, add columns for site and image_id with indexes

Revision ID: 05e5217f019f
Revises: 8258af8f3571
Create Date: 2021-07-23 14:43:43.320811

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "05e5217f019f"
down_revision = "77dfcebf5290"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("channel_v3", sa.Column("image_product", sa.Unicode(), nullable=True))
    op.add_column("channel_v3", sa.Column("image_branch", sa.Unicode(), nullable=True))
    op.add_column("channel_v3", sa.Column("image_arch", sa.Unicode(), nullable=True))
    op.add_column(
        "channel_v3", sa.Column("image_platform", sa.Unicode(), nullable=True)
    )
    op.add_column(
        "channel_v3", sa.Column("image_timestamp", sa.DateTime(), nullable=True)
    )
    op.add_column(
        "channel_v3", sa.Column("image_personality", sa.Unicode(), nullable=True)
    )
    op.add_column("channel_v3", sa.Column("site_id", sa.Unicode(), nullable=True))
    op.add_column("channel_v3", sa.Column("site_city", sa.Unicode(), nullable=True))
    op.add_column("channel_v3", sa.Column("site_state", sa.Unicode(), nullable=True))
    op.add_column("channel_v3", sa.Column("site_street", sa.Unicode(), nullable=True))
    op.add_column("channel_v3", sa.Column("site_country", sa.Unicode(), nullable=True))
    op.add_column("channel_v3", sa.Column("site_facility", sa.Unicode(), nullable=True))
    op.create_index(
        op.f("ix_channel_v3_image_arch"), "channel_v3", ["image_arch"], unique=False
    )
    op.create_index(
        op.f("ix_channel_v3_image_branch"), "channel_v3", ["image_branch"], unique=False
    )
    op.create_index(
        op.f("ix_channel_v3_image_personality"),
        "channel_v3",
        ["image_personality"],
        unique=False,
    )
    op.create_index(
        op.f("ix_channel_v3_image_platform"),
        "channel_v3",
        ["image_platform"],
        unique=False,
    )
    op.create_index(
        op.f("ix_channel_v3_image_product"),
        "channel_v3",
        ["image_product"],
        unique=False,
    )
    op.create_index(
        op.f("ix_channel_v3_image_timestamp"),
        "channel_v3",
        ["image_timestamp"],
        unique=False,
    )
    op.create_index(
        "ix_channel_v3_site_city",
        "channel_v3",
        ["site_city"],
        unique=False,
        postgresql_where=sa.text("site_city IS NOT NULL"),
    )
    op.create_index(
        "ix_channel_v3_site_country",
        "channel_v3",
        ["site_country"],
        unique=False,
        postgresql_where=sa.text("site_country IS NOT NULL"),
    )
    op.create_index(
        "ix_channel_v3_site_facility",
        "channel_v3",
        ["site_facility"],
        unique=False,
        postgresql_where=sa.text("site_facility IS NOT NULL"),
    )
    op.create_index(
        "ix_channel_v3_site_id",
        "channel_v3",
        ["site_id"],
        unique=False,
        postgresql_where=sa.text("site_id IS NOT NULL"),
    )
    op.create_index(
        "ix_channel_v3_site_state",
        "channel_v3",
        ["site_state"],
        unique=False,
        postgresql_where=sa.text("site_state IS NOT NULL"),
    )
    op.create_index(
        "ix_channel_v3_site_street",
        "channel_v3",
        ["site_street"],
        unique=False,
        postgresql_where=sa.text("site_street IS NOT NULL"),
    )

    op.execute(
        """
        UPDATE channel_v3 c
        SET
          site_city = c.site->>'city',
          site_state = c.site->>'state',
          site_street = c.site->>'street',
          site_country = c.site->>'country',
          site_facility = c.site->>'facility',
          site_id = c.site->>'id'
      """
    )


def downgrade():
    op.drop_index(
        "ix_channel_v3_site_street",
        table_name="channel_v3",
        postgresql_where=sa.text("site_street IS NOT NULL"),
    )
    op.drop_index(
        "ix_channel_v3_site_state",
        table_name="channel_v3",
        postgresql_where=sa.text("site_state IS NOT NULL"),
    )
    op.drop_index(
        "ix_channel_v3_site_id",
        table_name="channel_v3",
        postgresql_where=sa.text("site_id IS NOT NULL"),
    )
    op.drop_index(
        "ix_channel_v3_site_facility",
        table_name="channel_v3",
        postgresql_where=sa.text("site_facility IS NOT NULL"),
    )
    op.drop_index(
        "ix_channel_v3_site_country",
        table_name="channel_v3",
        postgresql_where=sa.text("site_country IS NOT NULL"),
    )
    op.drop_index(
        "ix_channel_v3_site_city",
        table_name="channel_v3",
        postgresql_where=sa.text("site_city IS NOT NULL"),
    )
    op.drop_index(op.f("ix_channel_v3_image_timestamp"), table_name="channel_v3")
    op.drop_index(op.f("ix_channel_v3_image_product"), table_name="channel_v3")
    op.drop_index(op.f("ix_channel_v3_image_platform"), table_name="channel_v3")
    op.drop_index(op.f("ix_channel_v3_image_personality"), table_name="channel_v3")
    op.drop_index(op.f("ix_channel_v3_image_branch"), table_name="channel_v3")
    op.drop_index(op.f("ix_channel_v3_image_arch"), table_name="channel_v3")
    op.drop_column("channel_v3", "site_facility")
    op.drop_column("channel_v3", "site_country")
    op.drop_column("channel_v3", "site_street")
    op.drop_column("channel_v3", "site_state")
    op.drop_column("channel_v3", "site_city")
    op.drop_column("channel_v3", "site_id")
    op.drop_column("channel_v3", "image_personality")
    op.drop_column("channel_v3", "image_timestamp")
    op.drop_column("channel_v3", "image_platform")
    op.drop_column("channel_v3", "image_arch")
    op.drop_column("channel_v3", "image_branch")
    op.drop_column("channel_v3", "image_product")
