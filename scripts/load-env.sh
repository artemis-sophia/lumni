#!/bin/bash
# Helper script to load .env file into current shell
# Usage: source scripts/load-env.sh
# Then you can use $GITHUB_TOKEN and other env vars

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

if [ ! -f "$PROJECT_ROOT/.env" ]; then
    echo "ERROR: .env file not found in $PROJECT_ROOT" >&2
    return 1 2>/dev/null || exit 1
fi

# Load .env file
set -a
source "$PROJECT_ROOT/.env"
set +a

echo "Loaded environment variables from .env"
echo "   GITHUB_TOKEN: ${GITHUB_TOKEN:0:20}..."
echo ""
echo "You can now use environment variables like \$GITHUB_TOKEN in your commands"

