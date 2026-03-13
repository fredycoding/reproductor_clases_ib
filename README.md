# Reproductor Seguro de Audio (Secure Audio Player)

Aplicacion de escritorio en Python para preparar y reproducir una biblioteca de audio protegida.

- Manual para usuarios finales: [MANUAL_USUARIO.md](MANUAL_USUARIO.md)
- En modo administrador convierte archivos `.mp3` a contenedores cifrados `.audx`.
- En modo usuario carga y reproduce `.audx` sin exponer una opcion de exportacion de audio desencriptado.
- La interfaz es local (HTML/CSS/JS embebida en app de escritorio con `pywebview`).

## 1) Objetivo del software

Este proyecto esta pensado para distribuir audios en un formato protegido para reproduccion local.

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
- Modos de repeticion (`off`, `all`, `one`) y `shuffle`.
- Interfaz bilingue (ES/EN).
- Modo administrador protegido por codigo.

## 3) Arquitectura tecnica (resumen)

- `app.py`
  Punto de entrada de escritorio. Inicializa `pywebview`, crea ventana y carga el frontend local.

- `secure_audio_app/api.py`
  API puente entre frontend y backend (desbloqueo admin, seleccion de archivos, cifrado y comandos de reproductor).

- `secure_audio_app/crypto.py`
  Logica de contenedor `.audx`, cifrado/descifrado, validaciones y metadatos.

- `secure_audio_app/player.py`
  Reproductor con `python-vlc` y callbacks de lectura desde memoria.

- `secure_audio_app/frontend/`
  Interfaz local (`index.html`, `styles.css`, `app.js`).

- `Reproductor.spec`
  Configuracion oficial de PyInstaller para Windows.

## 4) Requisitos

## Sistema operativo

- Windows (flujo de build y distribucion principal actual).

## Runtime / dependencias de sistema

- VLC instalado en el sistema (requerido por `python-vlc`).
- Microsoft Visual C++ Redistributable x64 (recomendado en equipos destino).

## Python (desarrollo/build)

- Python 3.10+
- Dependencias de [`requirements.txt`](requirements.txt)

Instalacion:

```bash
pip install -r requirements.txt
```

## 5) Ejecucion en desarrollo

```bash
python app.py
```

## 6) Uso funcional paso a paso

## Zona de administrador

1. Abrir la app.
2. Entrar a administrador con el codigo correspondiente.
3. Seleccionar uno o varios `.mp3`.
4. Elegir carpeta de salida.
5. Escribir clave (minimo 10 caracteres).
6. Ejecutar "Preparar biblioteca" para generar `.audx`.

## Zona de usuario

1. Pulsar "Abrir biblioteca".
2. Seleccionar uno o varios `.audx`.
3. Ingresar clave de reproduccion.
4. Cargar biblioteca y reproducir.

## 7) Formato `.audx`

El contenedor guarda:

- Encabezado JSON validado (algoritmo, KDF, salt, nonce, metadatos, etc.).
- Payload cifrado y autenticado.

Referencia formal: [file_format_spec.md](file_format_spec.md)

## 8) Seguridad y limites

El proyecto implementa medidas para reducir exposicion de audio en claro, pero no existe proteccion absoluta en una app de escritorio.

Riesgos que siempre pueden existir en escenarios avanzados:

- Captura de salida de audio por loopback del sistema.
- Instrumentacion del proceso en tiempo de ejecucion.
- Captura analogica externa.

Modelo detallado: [threat_model.md](threat_model.md)

## 9) Pruebas

```bash
python -m unittest discover -s tests
```

## 10) Build para Windows (oficial)

Usar el script oficial:

```powershell
.\scripts\build_windows.ps1
```

Este script:

1. Limpia `build/` y `dist/`.
2. Instala/actualiza dependencias.
3. Valida backend Qt (`PySide6`).
4. Genera ejecutable con `Reproductor.spec`.

Salida esperada:

- `dist\Reproductor\Reproductor.exe`

## 11) Distribucion a usuarios finales

Para usuarios no tecnicos, compartir la carpeta completa generada en `dist\Reproductor` (no solo el `.exe`).

Recomendado:

1. Comprimir `dist\Reproductor` en `.zip`.
2. En el equipo destino, extraer en una ruta local (por ejemplo `C:\Reproductor`).
3. Ejecutar `Reproductor.exe` con doble clic.

## 12) Troubleshooting rapido

## SmartScreen al abrir `.exe`

Es normal en ejecutables nuevos sin firma digital. Para reducir alertas en distribucion publica, firmar el binario.

## Pantalla en blanco o no abre UI

Verificar que el frontend este presente en el paquete (`secure_audio_app\frontend`) y reconstruir con el script oficial.

## Error de runtime en PC destino

- Ejecutar desde disco local (no red).
- Copiar carpeta completa de `dist\Reproductor`.
- Verificar VC++ x64 y VLC instalado.

## 13) Archivos clave del repositorio

- [app.py](app.py)
- [Reproductor.spec](Reproductor.spec)
- [scripts/build_windows.ps1](scripts/build_windows.ps1)
- [secure_audio_app/api.py](secure_audio_app/api.py)
- [secure_audio_app/crypto.py](secure_audio_app/crypto.py)
- [secure_audio_app/player.py](secure_audio_app/player.py)
- [secure_audio_app/frontend/index.html](secure_audio_app/frontend/index.html)
- [architecture.md](architecture.md)
- [file_format_spec.md](file_format_spec.md)
- [threat_model.md](threat_model.md)

