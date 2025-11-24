#!/bin/bash
# Run post_processors tests in a fresh subprocess to avoid PyO3 reinitialization issues
# Get the project root directory (parent of dev/)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

# Use python from PATH (which will be the nox session's python or the active venv)
python -m pytest python/tests/test_post_processors_reference.py -v --cov=post_processors --cov-report=term-missing --cov-report=html:htmlcov_post_processors
