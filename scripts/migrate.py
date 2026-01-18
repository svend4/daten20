#!/usr/bin/env python3
"""
Database Migration Management Script

Provides convenient commands for managing database migrations using Alembic.
This script wraps Alembic commands and provides additional utilities for
common migration tasks.

Usage:
    python scripts/migrate.py upgrade       # Upgrade to latest
    python scripts/migrate.py downgrade -1  # Downgrade one step
    python scripts/migrate.py status        # Show current migration status
    python scripts/migrate.py history       # Show migration history
    python scripts/migrate.py create "description"  # Create new migration
"""

import argparse
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Colors for terminal output
class Colors:
    """ANSI color codes for terminal output."""

    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def print_header(text):
    """Print colored header."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text:^60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 60}{Colors.ENDC}\n")


def print_success(text):
    """Print success message."""
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")


def print_error(text):
    """Print error message."""
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")


def print_warning(text):
    """Print warning message."""
    print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")


def print_info(text):
    """Print info message."""
    print(f"{Colors.OKCYAN}ℹ {text}{Colors.ENDC}")


def run_alembic_command(command, args=None):
    """
    Run Alembic command with error handling.

    Args:
        command: Alembic command to run
        args: Additional arguments for the command

    Returns:
        Tuple of (success, output)
    """
    cmd = ["alembic", command]
    if args:
        cmd.extend(args)

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        return result.returncode == 0, result.stdout + result.stderr
    except Exception as e:
        return False, str(e)


def upgrade(target="head"):
    """
    Upgrade database to a later version.

    Args:
        target: Target revision (default: head = latest)
    """
    print_header("Database Upgrade")
    print_info(f"Upgrading database to: {target}")

    success, output = run_alembic_command("upgrade", [target])

    if success:
        print_success("Database upgraded successfully!")
        print(output)
    else:
        print_error("Database upgrade failed!")
        print(output)
        sys.exit(1)


def downgrade(target="-1"):
    """
    Revert database to a previous version.

    Args:
        target: Target revision (default: -1 = one step back)
    """
    print_header("Database Downgrade")
    print_warning(f"Downgrading database to: {target}")
    print_warning("This operation will revert schema changes!")

    response = input(f"{Colors.WARNING}Are you sure? (yes/no): {Colors.ENDC}").strip().lower()
    if response != "yes":
        print_info("Downgrade cancelled.")
        return

    success, output = run_alembic_command("downgrade", [target])

    if success:
        print_success("Database downgraded successfully!")
        print(output)
    else:
        print_error("Database downgrade failed!")
        print(output)
        sys.exit(1)


def status():
    """Show current database migration status."""
    print_header("Migration Status")

    success, output = run_alembic_command("current")

    if success:
        print_success("Current migration status:")
        print(output)
    else:
        print_error("Failed to get migration status!")
        print(output)


def history(verbose=False):
    """
    Show migration history.

    Args:
        verbose: Show verbose output with ranges
    """
    print_header("Migration History")

    args = ["-v"] if verbose else []
    success, output = run_alembic_command("history", args)

    if success:
        print(output)
    else:
        print_error("Failed to get migration history!")
        print(output)


def create_migration(description, autogenerate=True):
    """
    Create a new migration.

    Args:
        description: Migration description
        autogenerate: Use autogenerate to detect schema changes
    """
    print_header("Create New Migration")
    print_info(f"Creating migration: {description}")

    args = ["-m", description]
    if autogenerate:
        args.insert(0, "--autogenerate")

    success, output = run_alembic_command("revision", args)

    if success:
        print_success("Migration created successfully!")
        print(output)

        # Extract migration file path from output
        for line in output.split("\n"):
            if "Generating" in line and ".py" in line:
                print_info(f"Migration file: {line.split('Generating')[1].strip()}")
    else:
        print_error("Failed to create migration!")
        print(output)
        sys.exit(1)


def heads():
    """Show current available heads in the version tree."""
    print_header("Migration Heads")

    success, output = run_alembic_command("heads")

    if success:
        print(output)
    else:
        print_error("Failed to get migration heads!")
        print(output)


def stamp(revision="head"):
    """
    Stamp database with a given revision without running migrations.

    Args:
        revision: Revision to stamp (default: head)
    """
    print_header("Stamp Database")
    print_warning(f"Stamping database to revision: {revision}")
    print_warning("This will NOT run migrations, only update version!")

    response = input(f"{Colors.WARNING}Are you sure? (yes/no): {Colors.ENDC}").strip().lower()
    if response != "yes":
        print_info("Stamp cancelled.")
        return

    success, output = run_alembic_command("stamp", [revision])

    if success:
        print_success("Database stamped successfully!")
        print(output)
    else:
        print_error("Failed to stamp database!")
        print(output)
        sys.exit(1)


def check_alembic_installed():
    """Check if Alembic is installed."""
    try:
        subprocess.run(["alembic", "--version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def main():
    """Main entry point."""
    if not check_alembic_installed():
        print_error("Alembic is not installed!")
        print_info("Install it with: pip install alembic")
        sys.exit(1)

    parser = argparse.ArgumentParser(
        description="Database Migration Management",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s upgrade              Upgrade to latest version
  %(prog)s upgrade +1           Upgrade one version
  %(prog)s downgrade -1         Downgrade one version
  %(prog)s status               Show current status
  %(prog)s history              Show migration history
  %(prog)s history --verbose    Show detailed history
  %(prog)s create "add_users_table"  Create new migration
  %(prog)s heads                Show current heads
  %(prog)s stamp head           Stamp to current version
        """,
    )

    parser.add_argument("command", help="Command to execute")
    parser.add_argument("args", nargs="*", help="Command arguments")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--autogenerate", action="store_true", default=True, help="Use autogenerate (default: True)")
    parser.add_argument("--no-autogenerate", action="store_true", help="Don't use autogenerate")

    args = parser.parse_args()

    # Map commands to functions
    commands = {
        "upgrade": lambda: upgrade(args.args[0] if args.args else "head"),
        "downgrade": lambda: downgrade(args.args[0] if args.args else "-1"),
        "status": status,
        "current": status,  # Alias
        "history": lambda: history(args.verbose),
        "create": lambda: create_migration(
            args.args[0] if args.args else "migration", not args.no_autogenerate
        ),
        "revision": lambda: create_migration(
            args.args[0] if args.args else "migration", not args.no_autogenerate
        ),  # Alias
        "heads": heads,
        "stamp": lambda: stamp(args.args[0] if args.args else "head"),
    }

    # Execute command
    if args.command in commands:
        try:
            commands[args.command]()
        except KeyboardInterrupt:
            print_warning("\nOperation cancelled by user.")
            sys.exit(1)
    else:
        print_error(f"Unknown command: {args.command}")
        print_info(f"Available commands: {', '.join(commands.keys())}")
        sys.exit(1)


if __name__ == "__main__":
    main()
