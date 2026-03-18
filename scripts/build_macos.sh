#!/usr/bin/env bash
set -Eeuo pipefail

APP_NAME="Reproductor"
ENTRYPOINT="app.py"
DIST_DIR="dist"
BUILD_DIR="build"
RELEASE_DIR="release"
APP_BIN_PATH="$DIST_DIR/$APP_NAME.app/Contents/MacOS/$APP_NAME"
ARCH_MODE="${1:-auto}"

if [[ "$(uname -s)" != "Darwin" ]]; then
  echo "ERROR: Este script solo se puede ejecutar en macOS."
  exit 1
fi

if command -v python3 >/dev/null 2>&1; then
  PY_BIN="python3"
else
  PY_BIN="python"
fi

case "$ARCH_MODE" in
  auto)
    if [[ "$(uname -m)" == "arm64" ]]; then TARGET_ARCH="arm64"; else TARGET_ARCH="x86_64"; fi
    ;;
  arm64|x86_64|universal2)
    TARGET_ARCH="$ARCH_MODE"
    ;;
  *)
    echo "ERROR: Arquitectura invalida '$ARCH_MODE'. Usa: auto | arm64 | x86_64 | universal2"
    exit 1
    ;;
esac

echo "==> Instalando dependencias..."
"$PY_BIN" -m pip install --upgrade pip pyinstaller
"$PY_BIN" -m pip install -r requirements.txt

echo "==> Validando runtime Tkinter..."
"$PY_BIN" - <<'PY'
import tkinter, vlc, mutagen, cryptography
print("Runtime Tkinter OK")
PY

echo "==> Limpiando salidas previas..."
rm -rf "$BUILD_DIR" "$DIST_DIR" "$RELEASE_DIR"
mkdir -p "$RELEASE_DIR"

echo "==> Generando app..."
"$PY_BIN" -m PyInstaller --noconfirm --clean --windowed --name "$APP_NAME" --target-arch "$TARGET_ARCH" "$ENTRYPOINT"

if [[ ! -x "$APP_BIN_PATH" ]]; then
  echo "ERROR: No se encontro el binario esperado en $APP_BIN_PATH."
  exit 1
fi

echo "==> Arquitectura del binario:"
lipo -info "$APP_BIN_PATH"

echo "Build completado: $DIST_DIR/$APP_NAME.app"
