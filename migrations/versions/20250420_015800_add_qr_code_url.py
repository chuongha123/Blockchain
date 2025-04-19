import sqlalchemy as sa
from alembic import op
from sqlalchemy.sql import text

# revision identifiers, used by Alembic.
revision = "20250420_015800_add_qr_code_url"
down_revision = "20250420_011700_add_is_harvested"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("farms", sa.Column("qr_code_url", sa.String(255), nullable=True))


def downgrade() -> None:
    op.drop_column("farms", "qr_code_url")
