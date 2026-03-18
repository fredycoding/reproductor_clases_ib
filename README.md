# Reproductor Audio (CustomTkinter)

Aplicacion de escritorio en Python para crear y reproducir audio protegido en formato `.audx`.

- Manual de uso rapido: [MANUAL_USUARIO.md](MANUAL_USUARIO.md)
- Guia de desarrollador (build/distribucion): [GUIA_DESARROLLADOR_BUILD.md](GUIA_DESARROLLADOR_BUILD.md)
- Arquitectura tecnica: [architecture.md](architecture.md)
- Especificacion del contenedor: [file_format_spec.md](file_format_spec.md)
- Modelo de amenazas: [threat_model.md](threat_model.md)

## 1) Que hace la aplicacion

La app tiene 2 modos:

1. `Admin`: convierte `.mp3` a `.audx` con clave.
2. `Usuario`: abre un `.audx`, valida clave y reproduce audio.

## 2) Estado actual de la interfaz

- Interfaz nativa con `customtkinter` (sin PyWeb ni PyQt).
- Selector de idioma `ES/EN` integrado en el codigo.
- Controles de reproduccion activos:
  - `Play/Pausa`
  - `Detener`
  - `Barra de avance`
  - `Volumen`
- Ya no existen botones `Anterior` y `Siguiente`.

Comportamiento clave:

- Al cargar un `.audx` correctamente, el panel de clave (texto + input + boton `Cargar audio`) se oculta.
- Ese panel vuelve a mostrarse cuando el usuario pulsa `Abrir audio AUDX` y selecciona otro archivo.

## 3) Seguridad (resumen)

- Cifrado autenticado `AES-256-GCM`.
- KDF `Argon2id` (fallback a `scrypt` si aplica).
- Reproduccion desde memoria con VLC (sin dump persistente en disco).
- Limpieza de buffers cuando se libera pista.

## 4) Requisitos

- Python 3.10+
- Dependencias en [requirements.txt](requirements.txt)
- VLC instalado en el sistema (requerido por `python-vlc`)

Instalacion:

```bash
pip install -r requirements.txt
```

## 5) Ejecutar en desarrollo

```bash
python app.py
```

## 6) Pruebas

```bash
python -m unittest discover -s tests
```

## 7) Build Windows (PyInstaller)

```powershell
cd "D:\PROYECTO REPRODUCTOR CLASES PYTHON"
py -3.10 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
.\scripts\build_windows.ps1
```

Salida esperada:

- `dist\Reproductor\Reproductor.exe`

## 8) Persistencia de estado al cerrar

La app guarda automaticamente estado en:

- `C:\Users\<usuario>\.secure_audio_player\state.json`

Se guarda:

- idioma (`es` / `en`)
- tamano y posicion de ventana
- modo activo (`user` / `admin`)
- volumen
- ultima carpeta de salida (admin)

## 9) Archivos principales

- [app.py](app.py)
- [secure_audio_app/customtkinter_app.py](secure_audio_app/customtkinter_app.py)
- [secure_audio_app/crypto.py](secure_audio_app/crypto.py)
- [secure_audio_app/player.py](secure_audio_app/player.py)
- [Reproductor.spec](Reproductor.spec)
- [scripts/build_windows.ps1](scripts/build_windows.ps1)
- [scripts/build_macos.sh](scripts/build_macos.sh)
- [scripts/build_linux.sh](scripts/build_linux.sh)
