#!/usr/bin/env python3
"""Script to manage database migration"""

import argparse
import subprocess
import sys


def run_command(command):
    """Run shell command and print the results"""
    print(f"Running: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(f"Error: {result.stderr}")
    return result.returncode


def main():
    """Main function to handle migration commands"""
    parser = argparse.ArgumentParser(description="Database migration management tool")

    subparsers = parser.add_subparsers(dest="command", help="Migration commands")

    # Create migration command
    create_parser = subparsers.add_parser("create", help="Create new migration")
    create_parser.add_argument("message", help="Migration description")
    create_parser.add_argument(
        "--auto", action="store_true", help="Auto-generate migration based on model"
    )

    # Update command
    upgrade_parser = subparsers.add_parser("upgrade", help="Update database")
    upgrade_parser.add_argument(
        "revision",
        nargs="?",
        default="head",
        help="Version to upgrade to (default: head)",
    )

    # Rollback command
    downgrade_parser = subparsers.add_parser("downgrade", help="Downgrade database")
    downgrade_parser.add_argument(
        "revision",
        help="Version to roll back to, or number of revisions to go back (e.g.: -1)",
    )

    # View history command
    history_parser = subparsers.add_parser("history", help="View migration history")
    history_parser.add_argument("--verbose", action="store_true", help="Show details")

    # Check current version command
    subparsers.add_parser("current", help="Show current version")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Process commands
    if args.command == "create":
        auto_flag = "--autogenerate" if args.auto else ""
        run_command(f'alembic revision {auto_flag} -m "{args.message}"')

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
    # Lấy tham số dòng lệnh
    if len(sys.argv) < 2:
        print("Usage: python migrate.py [upgrade|downgrade|heads|current|history|merge|<revision>]")
        sys.exit(1)

    action = sys.argv[1]

    # Các lệnh Alembic tương ứng
    commands = {
        "upgrade": "alembic upgrade head",
        "downgrade": "alembic downgrade -1",
        "heads": "alembic heads",
        "current": "alembic current",
        "history": "alembic history",
        "merge": "alembic merge heads",
        "heads-verbose": "alembic heads --verbose"
    }

    if action in commands:
        cmd = commands[action]
    elif action.startswith("up:"):
        # Nâng cấp đến revision cụ thể
        revision = action[3:]
        cmd = f"alembic upgrade {revision}"
    elif action.startswith("down:"):
        # Hạ cấp đến revision cụ thể
        revision = action[5:]
        cmd = f"alembic downgrade {revision}"
    else:
        # Xử lý các trường hợp đặc biệt
        if action == "upgrade-heads":
            cmd = "alembic upgrade heads"
        else:
            # Coi như là revision ID
            cmd = f"alembic upgrade {action}"

    # Thực thi lệnh
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True)

    # Kiểm tra kết quả
    if result.returncode != 0:
        print(f"FAILED: {cmd}")
        # Hiển thị thông tin về các revision hiện tại để giúp debug
        print("\nCurrent migration status:")
        subprocess.run("alembic current", shell=True)
        print("\nHeads information:")
        subprocess.run("alembic heads --verbose", shell=True)

        if "Multiple head revisions are present" in str(result.stderr):
            print("\nFix suggestion: Run 'python migrate.py upgrade-heads' to upgrade all heads")
            print("Or run 'python migrate.py heads-verbose' to see all available heads.")
    else:
        print(f"SUCCESS: {cmd}")
