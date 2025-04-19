import sqlalchemy as sa
from alembic import op
from sqlalchemy.sql import text

# revision identifiers, used by Alembic.
revision = "20250612_115800_update_user_farm"
down_revision = "20250612_add_farm_tables"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Add user_id column to farms table
    op.add_column("farms", sa.Column("user_id", sa.Integer(), nullable=True))

    # 2. Add foreign key to farms table
    op.create_foreign_key(
        "fk_farms_users", "farms", "users", ["user_id"], ["id"], ondelete="SET NULL"
    )

    # 3. Update data based on link_product field
    # Note: In Alembic, we typically don't perform data operations
    # but can use execute() to run SQL directly
    connection = op.get_bind()

    # Get all users with link_product
    result = connection.execute(
        text("SELECT id, link_product FROM users WHERE link_product IS NOT NULL")
    )
    users_with_link = result.fetchall()

    # For each user, update the corresponding farm
    for user_id, link_product in users_with_link:
        connection.execute(
            text(f"UPDATE farms SET user_id = :user_id WHERE id = :farm_id"),
            {"user_id": user_id, "farm_id": link_product},
        )

    print(f"Updated {len(users_with_link)} farms with corresponding user_id")


def downgrade() -> None:
    # 1. Drop foreign key
    op.drop_constraint("fk_farms_users", "farms", type_="foreignkey")

    # 2. Drop user_id column
    op.drop_column("farms", "user_id")

    # Note: We don't restore link_product data because it remains unchanged
