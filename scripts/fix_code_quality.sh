#!/bin/bash
# Auto-fix code quality issues
# Usage: ./scripts/fix_code_quality.sh

set -e

echo "================================"
echo "Auto-fixing Code Quality Issues"
echo "================================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 1. Format with black
echo "1. Formatting with black..."
black src/ tests/ *.py
echo -e "${GREEN}✓${NC} Code formatted"
echo ""

# 2. Sort imports with isort
echo "2. Sorting imports with isort..."
isort src/ tests/ *.py
echo -e "${GREEN}✓${NC} Imports sorted"
echo ""

# 3. Remove trailing whitespace
echo "3. Removing trailing whitespace..."
find src/ tests/ -name "*.py" -type f -exec sed -i 's/[[:space:]]*$//' {} \;
echo -e "${GREEN}✓${NC} Trailing whitespace removed"
echo ""

# 4. Fix common flake8 issues (optional)
echo "4. Checking for remaining issues..."
echo ""

# Show remaining flake8 issues
echo "Remaining flake8 issues:"
flake8 src/ tests/ --count --statistics --exit-zero | tail -20
echo ""

echo -e "${GREEN}✓ Auto-fixes complete!${NC}"
echo ""
echo "Next steps:"
echo "  1. Run ./scripts/code_quality_check.sh to verify"
echo "  2. Review and fix remaining flake8 issues manually"
echo "  3. Commit changes: git add . && git commit -m 'style: auto-fix code quality'"
