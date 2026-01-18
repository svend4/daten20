#!/usr/bin/env python3
"""
Database Migration Tool

Migrate data between different database systems:
- SQLite → PostgreSQL
- SQLite → MySQL
- PostgreSQL → MySQL
- etc.

Usage:
    python database_migration_tool.py --source sqlite:///data.db --target postgresql://user:pass@host/db
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import Dict, Any

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.database_universal import UniversalDatabase
from src.core.logger import setup_logger

# Setup logging
logger = setup_logger("migration_tool", level=logging.INFO)


def migrate_database(source_url: str, target_url: str, batch_size: int = 100) -> Dict[str, Any]:
    """
    Migrate data from source database to target database.

    Args:
        source_url: Source database URL
        target_url: Target database URL
        batch_size: Number of records to process at once

    Returns:
        Migration statistics
    """
    stats = {
        "services_migrated": 0,
        "subscriptions_migrated": 0,
        "errors": 0,
    }

    try:
        # Connect to source and target databases
        logger.info(f"Connecting to source database...")
        source_db = UniversalDatabase(database_url=source_url)

        logger.info(f"Connecting to target database...")
        target_db = UniversalDatabase(database_url=target_url)

        # Get source statistics
        source_stats = source_db.get_statistics()
        logger.info(f"Source database has {source_stats['total_services']} services")

        # Migrate services
        logger.info("Starting service migration...")
        offset = 0

        while True:
            # Get batch of services
            services = source_db.list_services(limit=batch_size, offset=offset)

            if not services:
                break

            logger.info(f"Processing batch: {offset} - {offset + len(services)}")

            # Migrate each service
            for service in services:
                try:
                    # Clear ID to create new record
                    old_id = service.id
                    service.id = None

                    # Create in target database
                    new_id = target_db.create_service(service)

                    logger.debug(f"Migrated service {old_id} → {new_id}")
                    stats["services_migrated"] += 1

                except Exception as e:
                    logger.error(f"Failed to migrate service {service.id}: {e}")
                    stats["errors"] += 1

            offset += batch_size

        logger.info(f"Service migration complete: {stats['services_migrated']} migrated")

        # Get target statistics
        target_stats = target_db.get_statistics()
        logger.info(f"Target database now has {target_stats['total_services']} services")

        # Close connections
        source_db.close()
        target_db.close()

        logger.info("Migration completed successfully!")
        return stats

    except Exception as e:
        logger.error(f"Migration failed: {e}", exc_info=True)
        stats["errors"] += 1
        return stats


def verify_migration(source_url: str, target_url: str) -> bool:
    """
    Verify migration by comparing record counts.

    Args:
        source_url: Source database URL
        target_url: Target database URL

    Returns:
        True if verification passed
    """
    try:
        source_db = UniversalDatabase(database_url=source_url)
        target_db = UniversalDatabase(database_url=target_url)

        source_stats = source_db.get_statistics()
        target_stats = target_db.get_statistics()

        logger.info("Verification Results:")
        logger.info(f"  Source services: {source_stats['total_services']}")
        logger.info(f"  Target services: {target_stats['total_services']}")

        if source_stats['total_services'] == target_stats['total_services']:
            logger.info("✓ Verification PASSED")
            return True
        else:
            logger.warning("✗ Verification FAILED - Record counts don't match")
            return False

    except Exception as e:
        logger.error(f"Verification failed: {e}")
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Database Migration Tool for Document Management System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Migrate from SQLite to PostgreSQL
  python database_migration_tool.py \\
      --source sqlite:///data/db/services.db \\
      --target postgresql://user:password@localhost/dms

  # Migrate from SQLite to MySQL
  python database_migration_tool.py \\
      --source sqlite:///data/db/services.db \\
      --target mysql+pymysql://user:password@localhost/dms

  # Migrate with verification
  python database_migration_tool.py \\
      --source sqlite:///data/db/services.db \\
      --target postgresql://user:password@localhost/dms \\
      --verify
        """
    )

    parser.add_argument(
        "--source",
        required=True,
        help="Source database URL (e.g., sqlite:///data.db)"
    )

    parser.add_argument(
        "--target",
        required=True,
        help="Target database URL (e.g., postgresql://user:pass@host/db)"
    )

    parser.add_argument(
        "--batch-size",
        type=int,
        default=100,
        help="Number of records to process at once (default: 100)"
    )

    parser.add_argument(
        "--verify",
        action="store_true",
        help="Verify migration after completion"
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging"
    )

    args = parser.parse_args()

    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Print migration plan
    print("\n" + "="*60)
    print("DATABASE MIGRATION TOOL")
    print("="*60)
    print(f"Source:     {args.source}")
    print(f"Target:     {args.target}")
    print(f"Batch size: {args.batch_size}")
    print("="*60 + "\n")

    # Confirm
    response = input("Proceed with migration? [y/N]: ")
    if response.lower() != 'y':
        print("Migration cancelled.")
        return 1

    # Run migration
    print("\nStarting migration...\n")
    stats = migrate_database(args.source, args.target, args.batch_size)

    # Print results
    print("\n" + "="*60)
    print("MIGRATION RESULTS")
    print("="*60)
    print(f"Services migrated: {stats['services_migrated']}")
    print(f"Subscriptions migrated: {stats['subscriptions_migrated']}")
    print(f"Errors: {stats['errors']}")
    print("="*60 + "\n")

    # Run verification if requested
    if args.verify:
        print("Running verification...\n")
        if verify_migration(args.source, args.target):
            print("✓ Migration verified successfully!")
            return 0
        else:
            print("✗ Migration verification failed!")
            return 1

    return 0 if stats['errors'] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
