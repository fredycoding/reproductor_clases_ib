#!/usr/bin/env bash
set -euo pipefail
# Comentario de prueba para validar cambios en Git.

APP_NAME="Reproductor"
ENTRYPOINT="app.py"
FRONTEND_SRC="secure_audio_app/frontend"
FRONTEND_DST="secure_audio_app/frontend"
DIST_DIR="dist"
BUILD_DIR="build"
RELEASE_DIR="release"
APP_BIN_PATH="$DIST_DIR/$APP_NAME.app/Contents/MacOS/$APP_NAME"

# Arch mode:
# - auto (default): arm64 on Apple Silicon, x86_64 on Intel
# - arm64
# - x86_64
# - universal2
ARCH_MODE="${1:-auto}"

if [[ "$(uname -s)" != "Darwin" ]]; then
  echo "ERROR: Este script solo se puede ejecutar en macOS."
  exit 1
fi

if [[ ! -f "$ENTRYPOINT" ]]; then
  echo "ERROR: No se encontro $ENTRYPOINT en la raiz del proyecto."
  exit 1
fi

if [[ ! -d "$FRONTEND_SRC" ]]; then
  echo "ERROR: No se encontro el frontend en $FRONTEND_SRC."
  exit 1
fi

if [[ -z "${VIRTUAL_ENV:-}" ]]; then
  echo "AVISO: No parece que un venv este activo. Se recomienda usar uno para evitar conflictos."
fi

if ! command -v python >/dev/null 2>&1; then
  echo "ERROR: Python no esta disponible en PATH."
  exit 1
fi

if ! command -v hdiutil >/dev/null 2>&1; then
  echo "ERROR: hdiutil no esta disponible."
  exit 1
fi

case "$ARCH_MODE" in
  auto)
    if [[ "$(uname -m)" == "arm64" ]]; then
      TARGET_ARCH="arm64"
    else
      TARGET_ARCH="x86_64"
    fi
    ;;
  arm64|x86_64|universal2)
    TARGET_ARCH="$ARCH_MODE"
    ;;
  *)
    echo "ERROR: Arquitectura invalida '$ARCH_MODE'. Usa: auto | arm64 | x86_64 | universal2"
    exit 1
    ;;
esac

echo "==> Instalando/actualizando herramientas de build..."
python -m pip install --upgrade pip pyinstaller

echo "==> Limpiando salidas previas..."
rm -rf "$BUILD_DIR" "$DIST_DIR" "$RELEASE_DIR"
mkdir -p "$RELEASE_DIR"

echo "==> Generando $APP_NAME.app (target-arch: $TARGET_ARCH)..."
python -m PyInstaller \
  --noconfirm \
  --clean \
  --windowed \
  --name "$APP_NAME" \
  --target-arch "$TARGET_ARCH" \
  --add-data "$FRONTEND_SRC:$FRONTEND_DST" \
  "$ENTRYPOINT"

if [[ ! -x "$APP_BIN_PATH" ]]; then
  echo "ERROR: No se encontro el binario esperado en $APP_BIN_PATH."
  exit 1
fi

echo "==> Arquitectura del binario:"
lipo -info "$APP_BIN_PATH"

DMG_PATH="$RELEASE_DIR/${APP_NAME}-${TARGET_ARCH}.dmg"
echo "==> Creando DMG en $DMG_PATH..."
hdiutil create \
  -volname "$APP_NAME" \
  -srcfolder "$DIST_DIR/$APP_NAME.app" \
  -ov \
  -format UDZO \
  "$DMG_PATH"

echo
echo "Build completado."
echo "App: $DIST_DIR/$APP_NAME.app"
echo "DMG: $DMG_PATH"
