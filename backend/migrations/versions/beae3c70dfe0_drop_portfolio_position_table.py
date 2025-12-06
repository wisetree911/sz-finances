"""drop portfolio_position table

Revision ID: beae3c70dfe0
Revises: 835d78d3b012
Create Date: 2025-12-06 13:35:26.892717

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'beae3c70dfe0'
down_revision: Union[str, Sequence[str], None] = '835d78d3b012'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.drop_table("portfolio_positions")


def downgrade() -> None:
    op.create_table(
        "portfolio_positions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("portfolio_id", sa.Integer(), nullable=False),
        sa.Column("asset_id", sa.Integer(), nullable=False),
        sa.Column("quantity", sa.Numeric(20, 6), nullable=False),
        sa.Column("avg_buy_price", sa.Numeric(20, 6), nullable=False),
        sa.Column("invested_value", sa.Numeric(20, 6), nullable=False),
    )