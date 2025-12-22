#!/bin/bash
# Cleanup gitignored files and rebuild the index

set -e

cd "$(dirname "$0")"

# Delete gitignored files except .venv
git clean -fdX -e .venv

# Rebuild the index
uv run python build_index.py
