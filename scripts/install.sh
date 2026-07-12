#!/usr/bin/env bash
# Instala cursor-highlighter: crea/actualiza el venv, lo instala en modo editable
# y publica el .desktop para que aparezca en el lanzador de aplicaciones de KDE.
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

echo "Listo. Buscá 'Cursor Highlighter' en el lanzador, o corré: $VENV_DIR/bin/cursor-highlighter"
