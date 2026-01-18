#!/bin/bash
###############################################################################
# Database Migration Status Checker
#
# This script checks the current status of database migrations and provides
# detailed information about pending migrations, current version, and more.
#
# Usage:
#   ./scripts/check_migrations.sh
###############################################################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Header
echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║        DATABASE MIGRATION STATUS CHECKER                      ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if Alembic is installed
if ! command -v alembic &> /dev/null; then
    echo -e "${RED}✗ Alembic is not installed!${NC}"
    echo -e "${YELLOW}Install it with: pip install alembic${NC}"
    exit 1
fi

# Check if alembic.ini exists
if [ ! -f "alembic.ini" ]; then
    echo -e "${RED}✗ alembic.ini not found!${NC}"
    echo -e "${YELLOW}Run 'alembic init alembic' to initialize.${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Alembic is installed${NC}"
echo ""

# 1. Current Version
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}1. Current Database Version${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
alembic current || echo -e "${YELLOW}⚠ Database not yet stamped with any version${NC}"
echo ""

# 2. Migration Heads
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}2. Current Migration Heads${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
alembic heads || echo -e "${YELLOW}⚠ No migration heads found${NC}"
echo ""

# 3. Migration History (last 10)
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}3. Recent Migration History (last 10)${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
alembic history | head -20 || echo -e "${YELLOW}⚠ No migration history found${NC}"
echo ""

# 4. Pending Migrations Check
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}4. Pending Migrations Check${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

CURRENT=$(alembic current 2>/dev/null | grep -oP '(?<=\(head\) )[a-f0-9]+' || echo "none")
HEAD=$(alembic heads 2>/dev/null | grep -oP '^[a-f0-9]+' | head -1 || echo "none")

if [ "$CURRENT" = "none" ]; then
    echo -e "${YELLOW}⚠ Database is not initialized${NC}"
    echo -e "${YELLOW}  Run: alembic upgrade head${NC}"
elif [ "$CURRENT" != "$HEAD" ]; then
    echo -e "${YELLOW}⚠ Database is not up to date${NC}"
    echo -e "${YELLOW}  Current: $CURRENT${NC}"
    echo -e "${YELLOW}  Latest:  $HEAD${NC}"
    echo -e "${YELLOW}  Run: alembic upgrade head${NC}"
else
    echo -e "${GREEN}✓ Database is up to date${NC}"
    echo -e "${GREEN}  Version: $CURRENT${NC}"
fi
echo ""

# 5. Migration Files Count
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}5. Migration Files${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

MIGRATION_COUNT=$(find alembic/versions -name "*.py" -type f 2>/dev/null | wc -l || echo "0")
echo -e "${GREEN}Total migration files: $MIGRATION_COUNT${NC}"

if [ "$MIGRATION_COUNT" -gt 0 ]; then
    echo -e "\n${BLUE}Recent migration files:${NC}"
    find alembic/versions -name "*.py" -type f -printf "%T@ %f\n" 2>/dev/null | sort -rn | head -5 | cut -d' ' -f2 | sed 's/^/  - /'
fi
echo ""

# 6. Database File Check
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}6. Database File Status${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

DB_PATH=$(grep "^sqlalchemy.url" alembic.ini | sed 's/.*sqlite:\/\/\///' | sed 's/ *$//')

if [ -f "$DB_PATH" ]; then
    DB_SIZE=$(du -h "$DB_PATH" | cut -f1)
    echo -e "${GREEN}✓ Database file exists${NC}"
    echo -e "  Path: $DB_PATH"
    echo -e "  Size: $DB_SIZE"
else
    echo -e "${YELLOW}⚠ Database file does not exist${NC}"
    echo -e "  Expected path: $DB_PATH"
    echo -e "  The database will be created when you run migrations."
fi
echo ""

# Summary
echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                          SUMMARY                               ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"

if [ "$CURRENT" = "none" ]; then
    echo -e "${YELLOW}Status: Database not initialized${NC}"
    echo -e "${YELLOW}Action: Run 'alembic upgrade head' or 'python scripts/migrate.py upgrade'${NC}"
elif [ "$CURRENT" != "$HEAD" ]; then
    echo -e "${YELLOW}Status: Pending migrations${NC}"
    echo -e "${YELLOW}Action: Run 'alembic upgrade head' or 'python scripts/migrate.py upgrade'${NC}"
else
    echo -e "${GREEN}Status: All migrations applied${NC}"
    echo -e "${GREEN}Action: No action needed${NC}"
fi
echo ""

exit 0
