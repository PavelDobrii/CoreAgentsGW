"""init routes"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20240601_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "user_profiles",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("context", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "route_drafts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("city", sa.String(length=255), nullable=False),
        sa.Column("language", sa.String(length=32), nullable=False),
        sa.Column("duration_min", sa.Integer(), nullable=False),
        sa.Column("transport_mode", sa.String(length=32), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="draft"),
        sa.Column("payload_json", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_route_drafts_user_id", "route_drafts", ["user_id"])

    op.create_table(
        "route_points",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("route_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("route_drafts.id", ondelete="CASCADE")),
        sa.Column("poi_id", sa.Text(), nullable=False),
        sa.Column("source_poi_id", sa.Text(), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("lat", sa.Float(), nullable=False),
        sa.Column("lng", sa.Float(), nullable=False),
        sa.Column("category", sa.String(length=120), nullable=False),
        sa.Column("order_index", sa.Integer(), nullable=False),
        sa.Column("eta_min_walk", sa.Integer(), nullable=True),
        sa.Column("eta_min_drive", sa.Integer(), nullable=True),
        sa.Column("listen_sec", sa.Integer(), nullable=True),
    )
    op.create_index("ix_route_points_route_order", "route_points", ["route_id", "order_index"])


def downgrade() -> None:
    op.drop_index("ix_route_points_route_order", table_name="route_points")
    op.drop_table("route_points")
    op.drop_index("ix_route_drafts_user_id", table_name="route_drafts")
    op.drop_table("route_drafts")
    op.drop_table("user_profiles")
