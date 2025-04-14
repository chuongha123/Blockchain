"""Create users table

Revision ID: 20230701_create_users_table
Revises: 
Create Date: 2023-07-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func


# revision identifiers, used by Alembic.
revision = '20230701_create_users_table'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Check if users table already exists
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    tables = inspector.get_table_names()
    
    if 'users' not in tables:
        print("Creating users table...")
        op.create_table(
            'users',
            sa.Column('id', sa.Integer, primary_key=True, index=True),
            sa.Column('email', sa.String(255), unique=True, index=True, nullable=False),
            sa.Column('username', sa.String(50), unique=True, index=True, nullable=False),
            sa.Column('hashed_password', sa.String(255), nullable=False),
            sa.Column('is_active', sa.Boolean, default=True),
            sa.Column('role', sa.String(100), default='user'),
            sa.Column('link_product', sa.String(255), nullable=True),
            sa.Column('created_at', sa.DateTime, server_default=func.now()),
            sa.Column('updated_at', sa.DateTime, server_default=func.now(), onupdate=func.now())
        )
        print("Users table created successfully!")
    else:
        print("Users table already exists, skipping table creation.")


def downgrade() -> None:
    op.drop_table('users') 