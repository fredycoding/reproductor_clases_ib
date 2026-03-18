# Guia de Desarrollador - Builds de Distribucion

Esta guia describe como generar los artefactos finales de distribucion para Windows, macOS y Linux.

Referencia rapida:

- Script Windows: `scripts/build_windows.ps1`
- Script macOS: `scripts/build_macos.sh`
- Script Linux: `scripts/build_linux.sh`
- Spec oficial Windows: `Reproductor.spec`

## 1) Requisitos generales

- Python 3.10 o superior
- `pip` actualizado
- Dependencias del proyecto: `requirements.txt`
- VLC instalado en el sistema

Comando base (en cualquier sistema):

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## 2) Build Windows (artefacto oficial)

Ejecutar desde PowerShell en la raiz del proyecto:

```powershell
cd "D:\PROYECTO REPRODUCTOR CLASES PYTHON"
py -3.10 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
.\scripts\build_windows.ps1
```

Que hace este script:

- limpia `build/` y `dist/`
- instala/actualiza `pyinstaller`
- valida runtime (`tkinter`, `vlc`, `mutagen`, `cryptography`)
- construye con `Reproductor.spec`

Salida esperada:

- Ejecutable principal: `dist\Reproductor\Reproductor.exe`

Empaquetado recomendado para entregar:

```powershell
Compress-Archive -Path ".\dist\Reproductor\*" -DestinationPath ".\release\Reproductor-Windows.zip" -Force
```

## 3) Build macOS

Desde Terminal en macOS:

```bash
cd /ruta/al/proyecto
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
chmod +x scripts/build_macos.sh
./scripts/build_macos.sh
```

Arquitectura opcional:

```bash
./scripts/build_macos.sh arm64
./scripts/build_macos.sh x86_64
./scripts/build_macos.sh universal2
```

Salida esperada:

- App bundle: `dist/Reproductor.app`

Notas:

- El script valida arquitectura final con `lipo -info`.
- El argumento por defecto es `auto`.

## 4) Build Linux

Desde shell en Linux:

```bash
cd /ruta/al/proyecto
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
chmod +x scripts/build_linux.sh
./scripts/build_linux.sh
```

Salida esperada:

- Carpeta de distribucion PyInstaller en `dist/Reproductor/`

## 5) Validacion minima post-build

Antes de entregar, validar:

1. La app inicia sin consola de error.
2. En modo usuario:
   - abrir `.audx`
   - ingresar clave
   - reproducir audio
3. En modo admin:
   - convertir al menos 1 `.mp3` a `.audx`
4. Verificar idioma `ES/EN`.
5. Verificar guardado de estado al cerrar y reabrir.

## 6) Problemas comunes de build

### Error por dependencias faltantes

Ejecutar:

```bash
python -m pip install --upgrade pip pyinstaller
python -m pip install -r requirements.txt
```

### Runtime de audio no disponible

Verificar instalacion de VLC en la maquina de build y destino.

### SmartScreen en Windows

En entornos corporativos es normal en binarios no firmados.
Se recomienda firma de codigo para despliegue masivo.

## 7) Estructura de entrega recomendada

Windows:

- Entregar zip de `dist\Reproductor\*`
- No entregar solo `Reproductor.exe` aislado

macOS:

- Entregar `Reproductor.app` (o `.dmg` generado externamente)

Linux:

- Entregar carpeta `dist/Reproductor/` completa

## 8) Notas de mantenimiento

- Si cambian imports o recursos, revisar `Reproductor.spec`.
- Mantener esta guia alineada con scripts reales en `scripts/`.
