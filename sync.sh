#!/bin/bash
# Sync conversation data from Claude Code and build the index

set -e

cd "$(dirname "$0")"

rsync -av --include='*/' --include='*.jsonl' --exclude='*' ~/.claude/projects/ data/projects/

uv run python build_index.py
