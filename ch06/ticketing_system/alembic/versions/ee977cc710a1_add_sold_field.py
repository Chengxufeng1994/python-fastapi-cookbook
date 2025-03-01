"""Add sold field

Revision ID: ee977cc710a1
Revises: 2033f52cf6be
Create Date: 2025-03-01 19:07:14.249667

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "ee977cc710a1"
down_revision = "2033f52cf6be"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("tickets", sa.Column("sold", sa.Boolean(), default=False, nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("tickets", "sold")
    # ### end Alembic commands ###
