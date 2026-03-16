#!/usr/bin/env bash
set -Eeuo pipefail

on_error() {
  local exit_code=$?
  local line_no=$1
  echo "ERROR: fallo en linea ${line_no}. Comando: ${BASH_COMMAND} (codigo ${exit_code})"
  exit $exit_code
}
trap 'on_error $LINENO' ERR
# Comentario de prueba para validar cambios en Git.

APP_NAME="Reproductor"
ENTRYPOINT="app.py"
FRONTEND_SRC="secure_audio_app/frontend"
FRONTEND_DST="secure_audio_app/frontend"
DIST_DIR="dist"
BUILD_DIR="build"
RELEASE_DIR="release"
APP_BIN_PATH="$DIST_DIR/$APP_NAME.app/Contents/MacOS/$APP_NAME"
PYI_EXTRA_ARGS=()

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

if command -v python3 >/dev/null 2>&1; then
  PY_BIN="python3"
elif command -v python >/dev/null 2>&1; then
  PY_BIN="python"
else
  echo "ERROR: Python no esta disponible en PATH."
  exit 1
fi

if ! command -v hdiutil >/dev/null 2>&1; then
  echo "ERROR: hdiutil no esta disponible."
  exit 1
fi

if [[ ! -d "/Applications/VLC.app" ]]; then
  echo "AVISO: VLC.app no se detecto en /Applications."
  echo "       Este build NO incluye libvlc dentro del .app; en la Mac destino se requiere VLC instalado."
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
"$PY_BIN" -m pip install --upgrade pip pyinstaller

if [[ -f "requirements.txt" ]]; then
  if [[ "$TARGET_ARCH" == "universal2" ]]; then
    echo "==> Modo universal2 en Intel: instalando dependencias compatibles..."
    export ARCHFLAGS="-arch x86_64 -arch arm64"
    export _PYTHON_HOST_PLATFORM="macosx-13.0-universal2"
    export MACOSX_DEPLOYMENT_TARGET="${MACOSX_DEPLOYMENT_TARGET:-13.0}"

    echo " - Reinstalando cffi como universal2 (source build)..."
    "$PY_BIN" -m pip install --force-reinstall --no-binary cffi cffi

    echo " - Instalando requirements sin argon2-cffi (incompatible universal2 en este entorno)..."
    TMP_REQ="$(mktemp)"
    grep -Ev '^[[:space:]]*argon2-cffi([[:space:]]|[<>=!~]|$)' requirements.txt > "$TMP_REQ"
    "$PY_BIN" -m pip install -r "$TMP_REQ"
    rm -f "$TMP_REQ"

    echo " - Eliminando Argon2 residual del venv para evitar binarios no-universales..."
    "$PY_BIN" -m pip uninstall -y argon2-cffi argon2-cffi-bindings || true

    PYI_EXTRA_ARGS+=(
      --exclude-module argon2
      --exclude-module argon2.low_level
      --exclude-module _argon2_cffi_bindings
    )

    echo "AVISO: Este build universal2 queda sin Argon2id; usara scrypt."
  else
    echo "==> Instalando dependencias runtime desde requirements.txt..."
    "$PY_BIN" -m pip install -r requirements.txt
  fi
fi

echo "==> Validando imports criticos antes de empaquetar..."
"$PY_BIN" - <<'PY'
import importlib
import sys

required = [
    "webview",
    "qtpy",
    "PySide6",
    "secure_audio_app.api",
    "secure_audio_app.app_paths",
]
missing = []
for name in required:
    try:
        importlib.import_module(name)
    except Exception as exc:
        missing.append((name, exc))

if missing:
    print("ERROR: faltan modulos requeridos para build:", file=sys.stderr)
    for name, exc in missing:
        print(f" - {name}: {exc}", file=sys.stderr)
    raise SystemExit(1)

print("OK: imports criticos disponibles")
PY


if [[ "$TARGET_ARCH" == "universal2" ]]; then
  echo "==> Validando extensiones nativas para universal2..."
  CFFI_SO="$("$PY_BIN" - <<'PY'
import sysconfig
from pathlib import Path
purelib = Path(sysconfig.get_paths()["purelib"])
matches = sorted(purelib.glob("_cffi_backend*.so"))
print(matches[0] if matches else "")
PY
)"

  if [[ -z "$CFFI_SO" || ! -f "$CFFI_SO" ]]; then
    echo "ERROR: no se encontro _cffi_backend*.so en el entorno virtual."
    exit 1
  fi

  CFFI_ARCHS="$(lipo -archs "$CFFI_SO" 2>/dev/null || true)"
  echo " - _cffi_backend: ${CFFI_ARCHS:-desconocido}"
  if [[ "$CFFI_ARCHS" != *"x86_64"* || "$CFFI_ARCHS" != *"arm64"* ]]; then
    echo "ERROR: _cffi_backend no es universal2 (falta x86_64 o arm64)."
    echo "Solucion recomendada:"
    echo "  1) Crear venv con Python.org universal2 (3.12 recomendado)."
    echo "  2) Reinstalar requirements y pyinstaller en ese venv."
    echo "  3) Reintentar build universal2."
    echo "Alternativa inmediata: compilar x86_64 con: bash scripts/build_macos.sh x86_64"
    exit 1
  fi
fi

echo "==> Limpiando salidas previas..."
rm -rf "$BUILD_DIR" "$DIST_DIR" "$RELEASE_DIR"
mkdir -p "$RELEASE_DIR" "$BUILD_DIR"

echo "==> Generando $APP_NAME.app (target-arch: $TARGET_ARCH)..."
"$PY_BIN" -m PyInstaller \
  --noconfirm \
  --clean \
  --windowed \
  --name "$APP_NAME" \
  --target-arch "$TARGET_ARCH" \
  --hidden-import webview \
  --hidden-import secure_audio_app.api \
  --hidden-import secure_audio_app.app_paths \
  --hidden-import webview.platforms.qt \
  --collect-submodules webview \
  --hidden-import qtpy \
  --hidden-import PySide6 \
  --hidden-import PySide6.QtWebEngineCore \
  --hidden-import PySide6.QtWebEngineWidgets \
  --add-data "$FRONTEND_SRC:$FRONTEND_DST" \
  "${PYI_EXTRA_ARGS[@]}" \
  "$ENTRYPOINT"

if [[ ! -x "$APP_BIN_PATH" ]]; then
  echo "ERROR: No se encontro el binario esperado en $APP_BIN_PATH."
  exit 1
fi

FRONTEND_IN_APP="$(find "$DIST_DIR/$APP_NAME.app/Contents" -type f -path "*/$FRONTEND_DST/index.html" -print -quit || true)"
if [[ -z "$FRONTEND_IN_APP" ]]; then
  echo "ERROR: No se encontro index.html dentro de la app empaquetada."
  echo "Buscado con patron: */$FRONTEND_DST/index.html"
  echo "Contenido candidato en Contents:"
  find "$DIST_DIR/$APP_NAME.app/Contents" -maxdepth 3 -type d | sed 's/^/ - /'
  exit 1
fi

echo "==> Frontend detectado en: $FRONTEND_IN_APP"

echo "==> Arquitectura del binario:"
lipo -info "$APP_BIN_PATH"
echo "==> Tamano de la app empaquetada:"
du -sh "$DIST_DIR/$APP_NAME.app"

DMG_BASE="$RELEASE_DIR/${APP_NAME}-${TARGET_ARCH}"
DMG_PATH="${DMG_BASE}.dmg"
DMG_TMP="$BUILD_DIR/${APP_NAME}-${TARGET_ARCH}.tmp.dmg"
DMG_STAGE="$BUILD_DIR/dmg-root"

echo "==> Preparando contenido del DMG..."
rm -rf "$DMG_STAGE"
mkdir -p "$DMG_STAGE"
cp -R "$DIST_DIR/$APP_NAME.app" "$DMG_STAGE/"
ln -s /Applications "$DMG_STAGE/Applications"

echo "==> Creando imagen temporal..."
hdiutil create \
  -volname "$APP_NAME" \
  -srcfolder "$DMG_STAGE" \
  -ov \
  -fs HFS+ \
  -format UDRW \
  "$DMG_TMP"

echo "==> Comprimiendo DMG final..."
hdiutil convert "$DMG_TMP" -format UDZO -o "$DMG_BASE"
rm -f "$DMG_TMP"

echo "==> Verificando DMG..."
hdiutil verify "$DMG_PATH"

echo
echo "Build completado."
echo "App: $DIST_DIR/$APP_NAME.app"
echo "DMG: $DMG_PATH"
echo "==> Tamano final del DMG:"
du -sh "$DMG_PATH"
echo "==> Recomendacion: copia la app a /Applications antes de abrirla."




