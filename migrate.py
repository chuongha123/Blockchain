#!/usr/bin/env python3
"""Script hỗ trợ quản lý database migration"""

import argparse
import os
import subprocess

def run_command(command):
    """Chạy lệnh shell và in kết quả"""
    print(f"Đang chạy: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(f"Lỗi: {result.stderr}")
    return result.returncode

def main():
    """Hàm chính để xử lý các lệnh migration"""
    parser = argparse.ArgumentParser(description="Công cụ quản lý database migration")
    
    subparsers = parser.add_subparsers(dest="command", help="Các lệnh migration")
    
    # Lệnh tạo migration
    create_parser = subparsers.add_parser("create", help="Tạo migration mới")
    create_parser.add_argument("message", help="Mô tả migration")
    create_parser.add_argument("--auto", action="store_true", help="Tự động sinh migration dựa trên model")
    
    # Lệnh cập nhật
    upgrade_parser = subparsers.add_parser("upgrade", help="Cập nhật database")
    upgrade_parser.add_argument("revision", nargs="?", default="head", help="Phiên bản để cập nhật tới (mặc định: head)")
    
    # Lệnh quay lại
    downgrade_parser = subparsers.add_parser("downgrade", help="Hạ cấp database")
    downgrade_parser.add_argument("revision", help="Phiên bản để quay lại, hoặc số lượng revision để lùi (ví dụ: -1)")
    
    # Lệnh xem lịch sử
    history_parser = subparsers.add_parser("history", help="Xem lịch sử migration")
    history_parser.add_argument("--verbose", action="store_true", help="Hiển thị chi tiết")
    
    # Lệnh kiểm tra phiên bản hiện tại
    subparsers.add_parser("current", help="Hiển thị phiên bản hiện tại")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Xử lý các lệnh
    if args.command == "create":
        auto_flag = "--autogenerate" if args.auto else ""
        run_command(f"alembic revision {auto_flag} -m \"{args.message}\"")
    
    elif args.command == "upgrade":
        run_command(f"alembic upgrade {args.revision}")
    
    elif args.command == "downgrade":
        run_command(f"alembic downgrade {args.revision}")
    
    elif args.command == "history":
        verbose_flag = "--verbose" if args.verbose else ""
        run_command(f"alembic history {verbose_flag}")
    
    elif args.command == "current":
        run_command("alembic current")

if __name__ == "__main__":
    main() 