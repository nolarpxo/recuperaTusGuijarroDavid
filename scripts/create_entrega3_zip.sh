#!/usr/bin/env bash

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

cd "$PROJECT_ROOT"

zip -r entrega3.zip . \
  -x ".venv/*" \
     "__pycache__/*" \
     "*/__pycache__/*" \
     ".idea/*" \
     ".git/*" \
     ".claude/*" \
     ".codex/*" \
     "AGENTS.md" \
     "informes/*" \
     "entrega3.zip"
