"""Create sponsorships for many to many

Revision ID: bbe7546b39ed
Revises: ae2c96f0314c
Create Date: 2025-03-01 19:56:56.230659

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "bbe7546b39ed"
down_revision = "ae2c96f0314c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "sponsors",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_table(
        "sponsorships",
        sa.Column("event_id", sa.Integer(), nullable=False),
        sa.Column("sponsor_id", sa.Integer(), nullable=False),
        sa.Column("amount", sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(
            ["event_id"],
            ["events.id"],
        ),
        sa.ForeignKeyConstraint(
            ["sponsor_id"],
            ["sponsors.id"],
        ),
        sa.PrimaryKeyConstraint("event_id", "sponsor_id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("sponsorships")
    op.drop_table("sponsors")
    # ### end Alembic commands ###
