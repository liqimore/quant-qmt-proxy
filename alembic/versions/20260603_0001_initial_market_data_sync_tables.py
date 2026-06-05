"""initial market data sync tables

Revision ID: 20260603_0001
Revises:
Create Date: 2026-06-03

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260603_0001"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "instruments",
        sa.Column("symbol", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("market", sa.String(), nullable=False),
        sa.Column("source", sa.String(), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("symbol"),
    )
    op.create_table(
        "sync_runs",
        sa.Column("run_date", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("instruments_done", sa.Boolean(), nullable=False),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("finished_at", sa.DateTime(), nullable=True),
        sa.Column("error_summary", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("run_date"),
    )
    op.create_table(
        "symbol_downloads",
        sa.Column("run_date", sa.String(), nullable=False),
        sa.Column("symbol", sa.String(), nullable=False),
        sa.Column("period", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("attempt_count", sa.Integer(), nullable=False),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("finished_at", sa.DateTime(), nullable=True),
        sa.Column("error_message", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("run_date", "symbol", "period"),
    )


def downgrade() -> None:
    op.drop_table("symbol_downloads")
    op.drop_table("sync_runs")
    op.drop_table("instruments")
