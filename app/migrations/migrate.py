"""
Script quản lý migration - chạy tất cả các migration theo thứ tự
Hướng dẫn sử dụng:
    python -m app.migrations.migrate [upgrade|downgrade] [migration_name]
    
Nếu không cung cấp migration_name, tất cả các migration sẽ được thực hiện
"""

import os
import sys
import importlib
import inspect
from datetime import datetime

# Thứ tự các migration được thực hiện
MIGRATIONS = [
    'create_user_farm_relation',
    # Thêm các migration khác ở đây theo thứ tự
]

def run_migrations(command, migration_name=None):
    """Chạy tất cả các migration theo thứ tự"""
    
    if migration_name and migration_name not in MIGRATIONS:
        print(f"Lỗi: Migration '{migration_name}' không tồn tại.")
        return False
    
    migrations_to_run = [migration_name] if migration_name else MIGRATIONS
    
    for migration in migrations_to_run:
        print(f"\n{'='*50}")
        print(f"Đang chạy migration: {migration} ({command})")
        print(f"Thời gian: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}")
        print(f"{'='*50}\n")
        
        try:
            # Import module migration
            module_path = f'app.migrations.{migration}'
            module = importlib.import_module(module_path)
            
            # Kiểm tra xem module có hàm upgrade/downgrade không
            if not hasattr(module, command):
                print(f"Lỗi: Migration '{migration}' không có hàm '{command}'")
                continue
            
            # Lấy và thực thi hàm
            func = getattr(module, command)
            if not inspect.isfunction(func):
                print(f"Lỗi: '{command}' trong '{migration}' không phải là hàm")
                continue
                
            # Thực hiện migration
            result = func()
            
            if result:
                print(f"Migration '{migration}' ({command}) đã hoàn tất thành công.")
            else:
                print(f"Migration '{migration}' ({command}) thất bại.")
                return False
                
        except ImportError:
            print(f"Lỗi: Không thể import migration '{migration}'")
            return False
        except Exception as e:
            print(f"Lỗi không xác định khi chạy migration '{migration}' ({command}): {str(e)}")
            return False
    
    return True

def print_help():
    """In hướng dẫn sử dụng"""
    print("""
Hướng dẫn sử dụng migration:
    python -m app.migrations.migrate [upgrade|downgrade] [migration_name]
    
Các tham số:
    upgrade         Nâng cấp cơ sở dữ liệu
    downgrade       Hạ cấp cơ sở dữ liệu (rollback)
    migration_name  (Tùy chọn) Tên của migration cụ thể
    
Các migration có sẵn:
    """)
    for migration in MIGRATIONS:
        print(f"    - {migration}")
    print("\nNếu không cung cấp migration_name, tất cả các migration sẽ được thực hiện theo thứ tự.")

if __name__ == "__main__":
    args = sys.argv[1:]
    
    if not args or args[0] in ['-h', '--help', 'help']:
        print_help()
        sys.exit(0)
        
    command = args[0].lower()
    if command not in ['upgrade', 'downgrade']:
        print(f"Lỗi: Lệnh không hợp lệ '{command}'. Sử dụng 'upgrade' hoặc 'downgrade'")
        print_help()
        sys.exit(1)
    
    migration_name = args[1] if len(args) > 1 else None
    
    success = run_migrations(command, migration_name)
    
    if success:
        print("\nTất cả các migration đã hoàn tất thành công.")
    else:
        print("\nQuá trình migration bị dừng do lỗi.")
        sys.exit(1) 