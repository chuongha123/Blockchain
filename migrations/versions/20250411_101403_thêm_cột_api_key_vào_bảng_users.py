"""Thêm cột api_key vào bảng users

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
    # Kiểm tra xem cột api_key đã tồn tại chưa
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('users')]
    
    if 'api_key' not in columns:
        print("Đang thêm cột api_key vào bảng users...")
        op.add_column('users', sa.Column('api_key', sa.String(50), nullable=True))
        print("Cột api_key đã được thêm thành công!")
    else:
        print("Cột api_key đã tồn tại, bỏ qua bước thêm cột.")


def downgrade() -> None:
    # Xóa cột api_key nếu tồn tại
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('users')]
    
    if 'api_key' in columns:
        print("Đang xóa cột api_key từ bảng users...")
        op.drop_column('users', 'api_key')
        print("Cột api_key đã được xóa thành công!")
    else:
        print("Cột api_key không tồn tại, bỏ qua bước xóa cột.") 