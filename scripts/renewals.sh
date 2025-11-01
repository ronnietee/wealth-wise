#!/bin/bash
# Shell script wrapper for renewal processing
# This script loads environment variables from .env and runs the renewal processor
#
# Usage:
#   ./scripts/renewals.sh
#
# For crontab:
#   0 2 * * * /path/to/wealth-wise/scripts/renewals.sh >> /path/to/wealth-wise/logs/renewals.log 2>&1

# Get directory where script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"

# Change to project directory
cd "$PROJECT_DIR" || exit 1

# Load environment variables from .env file
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
else
    echo "ERROR: .env file not found in $PROJECT_DIR"
    exit 1
fi

# Ensure required variables are set
if [ -z "$ADMIN_USERNAME" ] || [ -z "$ADMIN_PASSWORD" ]; then
    echo "ERROR: ADMIN_USERNAME and ADMIN_PASSWORD must be set in .env file"
    exit 1
fi

# Set default APP_URL if not set
export APP_URL="${APP_URL:-http://localhost:5000}"

# Run the renewal processing script
python3 "$SCRIPT_DIR/process_renewals.py"

# Exit with the Python script's exit code
exit $?

