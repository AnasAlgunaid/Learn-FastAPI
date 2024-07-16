"""Added created_at column to users table

Revision ID: db434cb77fa7
Revises: 3d21ecd76d9c
Create Date: 2024-07-13 00:25:36.408889

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "db434cb77fa7"
down_revision: Union[str, None] = "3d21ecd76d9c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "users",
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=True
        ),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("users", "created_at")
    # ### end Alembic commands ###