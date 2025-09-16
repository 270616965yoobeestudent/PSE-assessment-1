#!/usr/bin/env bash
set -euo pipefail

# Build a self-extracting PEX that supports native extensions.

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
DIST_DIR="$ROOT_DIR/dist"
PYTHON_BIN=${PYTHON_BIN:-python3}

mkdir -p "$DIST_DIR"
OUT_PEX="$DIST_DIR/cgps.pex"
rm -f "$OUT_PEX"

if ! "$PYTHON_BIN" -c "import pex" >/dev/null 2>&1; then
  echo "ERROR: 'pex' is not installed for $PYTHON_BIN. Install it with:"
  echo "       $PYTHON_BIN -m pip install pex"
  exit 1
fi

echo "Building PEX with $PYTHON_BIN ..."
"$PYTHON_BIN" -m pex \
  -r "$ROOT_DIR/requirements.txt" \
  "$ROOT_DIR" \
  -e cgps.__main__:main \
  -o "$OUT_PEX"

echo "Created $OUT_PEX"
echo "Run with: $OUT_PEX"

