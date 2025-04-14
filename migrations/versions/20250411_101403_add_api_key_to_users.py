"""Add api_key column to users table

Revision ID: 0a3d844c3c53
Revises: 20230701_create_users_table
Create Date: 2025-04-11 10:14:03.986956+00:00

"""
from alembic import op
import sqlalchemy as sa
import uuid

# revision identifiers, used by Alembic.
revision = '0a3d844c3c53'
down_revision = '20230701_create_users_table'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Check if api_key column already exists
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('users')]
    
    if 'api_key' not in columns:
        print("Adding api_key column to users table...")
        op.add_column('users', sa.Column('api_key', sa.String(50), nullable=True))
        print("api_key column added successfully!")
    else:
        print("api_key column already exists, skipping column addition.")


def downgrade() -> None:
    # Remove api_key column if it exists
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('users')]
    
    if 'api_key' in columns:
        print("Removing api_key column from users table...")
        op.drop_column('users', 'api_key')
        print("api_key column removed successfully!")
    else:
        print("api_key column does not exist, skipping column removal.") 