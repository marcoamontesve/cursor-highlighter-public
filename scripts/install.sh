#!/usr/bin/env bash
# Installs cursor-highlighter: creates/updates the venv, installs it in
# editable mode, and publishes the .desktop file so it shows up in KDE's
# application launcher.
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="$REPO_DIR/.venv"
APPS_DIR="$HOME/.local/share/applications"

if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv --system-site-packages "$VENV_DIR"
fi

"$VENV_DIR/bin/python3" -m pip install -e "$REPO_DIR" --no-build-isolation

mkdir -p "$APPS_DIR"
sed "s#%INSTALL_PREFIX%#$REPO_DIR#g" "$REPO_DIR/packaging/cursor-highlighter.desktop" \
    > "$APPS_DIR/cursor-highlighter.desktop"

if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database "$APPS_DIR"
fi

echo "Done. Look for 'Cursor Highlighter' in your launcher, or run: $VENV_DIR/bin/cursor-highlighter"
