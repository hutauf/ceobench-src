#!/bin/bash
# NovaMind Bench — Quick Install
#
# Downloads the correct binary for your platform and makes it executable.
#
# Usage:
#   bash install.sh
#   # or
#   curl -fsSL <repo-url>/install.sh | bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BIN_DIR="$SCRIPT_DIR/bin"

PLATFORM=$(uname -s | tr '[:upper:]' '[:lower:]')
ARCH=$(uname -m)
BINARY_NAME="novamind-server-${PLATFORM}-${ARCH}"
BINARY_PATH="$BIN_DIR/$BINARY_NAME"

echo "NovaMind Bench — Install"
echo "========================"
echo "Platform: $PLATFORM ($ARCH)"

if [ -f "$BINARY_PATH" ]; then
    chmod +x "$BINARY_PATH"
    chmod +x "$SCRIPT_DIR/novamind-operation"
    echo "✅ Binary found: $BINARY_PATH"
    echo "✅ CLI ready: $SCRIPT_DIR/novamind-operation"
    echo ""
    echo "Add to PATH:"
    echo "  export PATH=\"$SCRIPT_DIR:\$PATH\""
    echo ""
    echo "Quick start:"
    echo "  novamind-operation new-session --days 365"
    echo "  novamind-operation next-day"
else
    echo "❌ Binary not found for your platform: $BINARY_NAME"
    echo "   Available binaries:"
    ls "$BIN_DIR"/ 2>/dev/null || echo "   (none found in $BIN_DIR/)"
    echo ""
    echo "   You may need to build from source or download the correct binary."
    exit 1
fi
