#!/usr/bin/env python3
"""
Database Optimization Utility

Applies all recommended database optimizations:
- Creates missing indexes
- Runs ANALYZE for query planner
- Runs VACUUM to reclaim space
- Generates performance report

Usage:
    python scripts/optimize_database.py
    python scripts/optimize_database.py --db-path /path/to/database.db
    python scripts/optimize_database.py --analyze-only
"""

import argparse
import logging
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.query_optimizer import QueryOptimizer, optimize_database_full
from src.utils.constants import DATABASE_FILE

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Database optimization utility')
    parser.add_argument(
        '--db-path',
        default=DATABASE_FILE,
        help='Path to database file (default: %(default)s)'
    )
    parser.add_argument(
        '--analyze-only',
        action='store_true',
        help='Only run ANALYZE, skip VACUUM and index creation'
    )
    parser.add_argument(
        '--indexes-only',
        action='store_true',
        help='Only create indexes, skip ANALYZE and VACUUM'
    )
    parser.add_argument(
        '--report',
        action='store_true',
        help='Generate and display performance report'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without making changes'
    )

    args = parser.parse_args()

    logger.info("=" * 60)
    logger.info("Database Optimization Utility")
    logger.info("=" * 60)
    logger.info(f"Database path: {args.db_path}")

    if args.dry_run:
        logger.info("DRY RUN MODE - No changes will be made")

    optimizer = QueryOptimizer(args.db_path)

    # Get initial stats
    logger.info("\nInitial Database Statistics:")
    logger.info("-" * 60)
    stats = optimizer.get_database_stats()
    logger.info(f"Database size: {stats['database_size_mb']:.2f} MB")
    logger.info(f"Wasted space: {stats['wasted_space_mb']:.2f} MB ({stats['wasted_percentage']:.1f}%)")
    logger.info(f"Total rows: {stats['total_rows']:,}")
    logger.info("\nTables:")
    for table, count in stats['tables'].items():
        logger.info(f"  - {table}: {count:,} rows")

    # Get existing indexes
    logger.info("\nExisting Indexes:")
    logger.info("-" * 60)
    indexes = optimizer.get_all_indexes()
    for idx in indexes:
        logger.info(f"  - {idx['table']}.{idx['name']} ({', '.join(idx['columns'])})")

    if args.analyze_only:
        logger.info("\nRunning ANALYZE...")
        logger.info("-" * 60)
        if not args.dry_run:
            success = optimizer.analyze_database()
            logger.info(f"ANALYZE: {'SUCCESS' if success else 'FAILED'}")
        else:
            logger.info("Would run: ANALYZE")

    elif args.indexes_only:
        logger.info("\nCreating Additional Indexes...")
        logger.info("-" * 60)
        if not args.dry_run:
            results = optimizer.create_additional_indexes()
            successful = sum(1 for success in results.values() if success)
            logger.info(f"\nCreated {successful}/{len(results)} indexes successfully")
            for name, success in results.items():
                status = "✓" if success else "✗"
                logger.info(f"  {status} {name}")
        else:
            logger.info("Would create indexes:")
            logger.info("  - idx_services_type_region")
            logger.info("  - idx_services_updated")
            logger.info("  - idx_services_created")
            logger.info("  - idx_versions_service_version")
            logger.info("  - idx_financial_created")
            logger.info("  - idx_financial_rate")
            logger.info("  - idx_subscriptions_tenant_status")
            logger.info("  - idx_subscriptions_status_created")
            logger.info("  - idx_services_name_region_type")

    elif args.report:
        logger.info("\nPerformance Report:")
        logger.info("-" * 60)
        report = optimizer.get_performance_report()
        logger.info(f"Total queries analyzed: {report['total_queries']}")
        logger.info(f"Queries using index: {report['queries_using_index']}")
        logger.info(f"Queries without index: {report['queries_without_index']}")
        logger.info(f"Average execution time: {report['average_execution_time']*1000:.2f}ms")

        if report['slowest_queries']:
            logger.info("\nSlowest Queries:")
            for i, q in enumerate(report['slowest_queries'][:5], 1):
                logger.info(f"  {i}. {q.query[:80]}... ({q.execution_time*1000:.2f}ms)")

        if report['suggested_indexes']:
            logger.info("\nSuggested Indexes:")
            for suggestion in report['suggested_indexes']:
                logger.info(f"  - {suggestion}")

    else:
        # Full optimization
        logger.info("\nPerforming Full Optimization...")
        logger.info("-" * 60)

        if not args.dry_run:
            results = optimize_database_full(args.db_path)

            logger.info("\nOptimization Results:")
            logger.info("-" * 60)

            # Indexes
            successful_indexes = sum(1 for success in results['indexes_created'].values() if success)
            logger.info(f"Indexes created: {successful_indexes}/{len(results['indexes_created'])}")

            # ANALYZE
            logger.info(f"ANALYZE: {'SUCCESS' if results['analyze_success'] else 'FAILED'}")

            # VACUUM
            logger.info(f"VACUUM: {'SUCCESS' if results['vacuum_success'] else 'FAILED'}")

            # Final stats
            final_stats = results['database_stats']
            logger.info(f"\nFinal Database Size: {final_stats['database_size_mb']:.2f} MB")
            logger.info(f"Wasted Space: {final_stats['wasted_space_mb']:.2f} MB ({final_stats['wasted_percentage']:.1f}%)")

            # Space saved
            space_saved_mb = stats['database_size_mb'] - final_stats['database_size_mb']
            if space_saved_mb > 0:
                logger.info(f"Space Reclaimed: {space_saved_mb:.2f} MB")

        else:
            logger.info("Would perform:")
            logger.info("  1. Create 9 additional indexes")
            logger.info("  2. Run ANALYZE to update query planner statistics")
            logger.info("  3. Run VACUUM to reclaim space and defragment")

    logger.info("\n" + "=" * 60)
    logger.info("Optimization Complete!")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
