#!/bin/bash
# build.sh — Build a standalone badge executable with PyInstaller.
# Run from the repo root on the Pi. Output: dist/badge

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

uv sync --extra dev

uv run pyinstaller \
    --onefile \
    --name badge \
    --add-data "fonts:fonts" \
    --add-data "img:img" \
    --hidden-import spidev \
    --hidden-import lgpio \
    --hidden-import gpiozero.pins.lgpio \
    src/cli.py

echo ""
echo "Built: dist/badge"
echo "Run:   ./dist/badge --help"
