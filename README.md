# Reproductor Seguro de Audio (CustomTkinter)

Aplicacion de escritorio en Python para preparar y reproducir audios protegidos en formato `.audx`.

- Manual para usuarios finales: [MANUAL_USUARIO.md](MANUAL_USUARIO.md)
- En modo administrador convierte `.mp3` a `.audx`.
- En modo usuario carga y reproduce `.audx`.
- Interfaz de escritorio nativa moderna con `customtkinter` (sin PyWeb/PyQt).

## 1) Objetivo del software

Este proyecto permite distribuir audios en un formato protegido para reproduccion local.

Flujo general:

1. Seleccionar MP3 en zona de administrador.
2. Definir clave de acceso para cifrado.
3. Generar archivos `.audx`.
4. En zona de usuario, abrir `.audx`, ingresar clave y reproducir.

## 2) Caracteristicas principales

- Cifrado autenticado `AES-256-GCM`.
- Derivacion de clave con `Argon2id` (fallback a `scrypt` si aplica).
- Solo acepta MP3 como entrada para cifrado.
- Reproduccion desde memoria usando VLC (sin archivo temporal desencriptado persistente).
- Limpieza de buffers en memoria al liberar pista.
- Control de reproduccion: play/pause, stop, seek, volumen, anterior/siguiente.
- Atajos de teclado (espacio, flechas, N/P).
- Interfaz bilingue (ES/EN).
- Modo administrador protegido por codigo.

## 3) Arquitectura tecnica (resumen)

- `app.py`
  Punto de entrada oficial de escritorio (CustomTkinter).

- `secure_audio_app/customtkinter_app.py`
  Interfaz completa (modo admin/usuario, controles, estado).

- `secure_audio_app/crypto.py`
  Logica de contenedor `.audx`, cifrado/descifrado, validaciones y metadatos.

- `secure_audio_app/player.py`
  Reproductor con `python-vlc` y callbacks de lectura desde memoria.

- `Reproductor.spec`
  Configuracion oficial de PyInstaller para Windows.

## 4) Requisitos

### Sistemas operativos

- Windows 10/11 (flujo oficial de build en este repo).
- macOS / Linux (build local con scripts incluidos).

### Dependencias de sistema

- VLC instalado en el sistema (requerido por `python-vlc`).
- Windows: Microsoft Visual C++ Redistributable x64 (recomendado en equipos destino).

### Python (desarrollo/build)

- Python 3.10+ recomendado.
- Dependencias de [`requirements.txt`](requirements.txt).

Instalacion base:

```bash
pip install -r requirements.txt
```

## 5) Ejecucion en desarrollo

```bash
python app.py
```

## 6) Pruebas

```bash
python -m unittest discover -s tests
```

## 7) Build para Windows (oficial, PowerShell)

```powershell
cd "D:\PROYECTO REPRODUCTOR CLASES PYTHON"
py -3.10 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
.\scripts\build_windows.ps1
```

Salida esperada:

- `dist\Reproductor\Reproductor.exe`

## 8) Build para macOS

```bash
cd /ruta/al/proyecto
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
chmod +x scripts/build_macos.sh
./scripts/build_macos.sh
```

## 9) Build para Linux

```bash
chmod +x scripts/build_linux.sh
./scripts/build_linux.sh
```

## 10) Distribucion Windows

Empaqueta la carpeta completa generada en `dist\Reproductor`:

```powershell
Compress-Archive -Path ".\dist\Reproductor\*" -DestinationPath ".\release\Reproductor-Windows.zip" -Force
```

## 11) Formato `.audx`

Referencia formal: [file_format_spec.md](file_format_spec.md)

## 12) Seguridad y limites

El proyecto reduce exposicion de audio en claro.

Modelo detallado: [threat_model.md](threat_model.md)

## 13) Archivos clave del repositorio

- [app.py](app.py)
- [Reproductor.spec](Reproductor.spec)
- [scripts/build_windows.ps1](scripts/build_windows.ps1)
- [scripts/build_macos.sh](scripts/build_macos.sh)
- [scripts/build_linux.sh](scripts/build_linux.sh)
- [secure_audio_app/customtkinter_app.py](secure_audio_app/customtkinter_app.py)
- [secure_audio_app/crypto.py](secure_audio_app/crypto.py)
- [secure_audio_app/player.py](secure_audio_app/player.py)
- [architecture.md](architecture.md)
- [file_format_spec.md](file_format_spec.md)
- [threat_model.md](threat_model.md)



