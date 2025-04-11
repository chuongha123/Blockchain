#!/usr/bin/env python3
"""Script to manage database migration"""

import argparse
import os
import subprocess

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
    create_parser.add_argument("--auto", action="store_true", help="Auto-generate migration based on model")
    
    # Update command
    upgrade_parser = subparsers.add_parser("upgrade", help="Update database")
    upgrade_parser.add_argument("revision", nargs="?", default="head", help="Version to upgrade to (default: head)")
    
    # Rollback command
    downgrade_parser = subparsers.add_parser("downgrade", help="Downgrade database")
    downgrade_parser.add_argument("revision", help="Version to roll back to, or number of revisions to go back (e.g.: -1)")
    
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