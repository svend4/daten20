#!/usr/bin/env python3
"""
Document Management System - Setup Script

Automated setup and configuration for first-time installation.
"""

import os
import secrets
import subprocess
import sys
from pathlib import Path


def print_header(text):
    """Print formatted header"""
    print(f"\n{'=' * 60}")
    print(f"  {text}")
    print(f"{'=' * 60}\n")


def print_step(step, total, text):
    """Print step progress"""
    print(f"[{step}/{total}] {text}...")


def check_python_version():
    """Check Python version"""
    if sys.version_info < (3, 9):
        print("ERROR: Python 3.9 or higher is required")
        sys.exit(1)
    print(f"✓ Python version: {sys.version.split()[0]}")


def create_directories():
    """Create necessary directories"""
    directories = [
        "data",
        "data/db",
        "data/exports",
        "data/templates",
        "logs",
        "backups",
    ]

    for dir_path in directories:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"✓ Created: {dir_path}")


def create_env_file():
    """Create .env file from template"""
    env_path = Path(".env")

    if env_path.exists():
        response = input(".env file already exists. Overwrite? (y/N): ")
        if response.lower() != "y":
            print("Keeping existing .env file")
            return

    # Generate SECRET_KEY
    secret_key = secrets.token_hex(32)

    # Read template
    template = Path(".env.example").read_text()

    # Replace SECRET_KEY
    env_content = template.replace("SECRET_KEY=your-secret-key-here-change-in-production", f"SECRET_KEY={secret_key}")

    # Write .env
    env_path.write_text(env_content)

    print(f"✓ Created .env file with generated SECRET_KEY")


def install_dependencies():
    """Install Python dependencies"""
    print("Installing dependencies (this may take a few minutes)...")

    try:
        result = subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], capture_output=True)

        result = subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("✓ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install dependencies")
        print("Please run manually: pip install -r requirements.txt")


def initialize_database():
    """Initialize database"""
    from src.core.database import Database

    try:
        db = Database()
        print("✓ Database initialized")
    except Exception as e:
        print(f"✗ Database initialization failed: {e}")


def create_admin_user():
    """Create default admin user"""
    from src.core.auth import Role, get_auth_manager

    print("\nCreate admin user:")
    username = input("  Username [admin]: ") or "admin"
    email = input("  Email [admin@dms.local]: ") or "admin@dms.local"

    import getpass

    password = getpass.getpass("  Password: ")
    password_confirm = getpass.getpass("  Confirm password: ")

    if password != password_confirm:
        print("✗ Passwords do not match")
        return

    auth = get_auth_manager()
    user = auth.create_user(username, email, password, Role.ADMIN)

    if user:
        print(f"✓ Admin user created: {username}")
    else:
        print("✗ Failed to create admin user (may already exist)")


def print_summary():
    """Print setup summary"""
    print_header("Setup Complete!")

    print("Next steps:")
    print()
    print("1. Start the application:")
    print("   python src/web_app.py")
    print()
    print("2. Access:")
    print("   Web UI:    http://localhost:5000")
    print("   API Docs:  http://localhost:5000/apidocs")
    print("   GraphQL:   http://localhost:5000/graphql")
    print()
    print("3. Admin CLI:")
    print("   python dms-admin.py --help")
    print()


def main():
    """Main setup routine"""
    print_header("Document Management System - Setup")

    steps = [
        ("Checking Python version", check_python_version),
        ("Creating directories", create_directories),
        ("Creating .env file", create_env_file),
        ("Installing dependencies", install_dependencies),
        ("Initializing database", initialize_database),
        ("Creating admin user", create_admin_user),
    ]

    total_steps = len(steps)

    for i, (description, func) in enumerate(steps, 1):
        print_step(i, total_steps, description)

        try:
            func()
        except KeyboardInterrupt:
            print("\n\nSetup interrupted by user")
            sys.exit(1)
        except Exception as e:
            print(f"✗ Error: {e}")

    print_summary()


if __name__ == "__main__":
    main()
