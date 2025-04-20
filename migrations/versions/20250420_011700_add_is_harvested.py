import sqlalchemy as sa
from alembic import op
from sqlalchemy.sql import text

# revision identifiers, used by Alembic.
revision = "20250420_011700_add_is_harvested"
down_revision = "20250612_115800_update_user_farm"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("farms", sa.Column("is_harvested", sa.Boolean(), nullable=True))


def downgrade() -> None:
    op.drop_column("farms", "is_harvested")
