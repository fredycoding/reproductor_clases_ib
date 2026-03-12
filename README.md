# Secure Audio Player

Aplicacion de escritorio multiplataforma en Python para encriptar archivos MP3 en un contenedor propietario `.audx` y reproducirlos localmente con una interfaz embebida.

## Tecnologias

- Backend en Python
- `pywebview` para la ventana de escritorio con UI web local
- Frontend local en HTML/CSS/JavaScript
- `cryptography` + `argon2-cffi` para cifrado autenticado y derivacion de clave
- `python-vlc` para reproduccion desde memoria

## Caracteristicas

- Encriptacion de uno o varios MP3 a `.audx`
- Cifrado autenticado `AES-256-GCM` con nonce aleatorio por archivo
- Derivacion de clave con `Argon2id` y fallback seguro a `scrypt` si `Argon2id` no esta disponible
- Reproduccion solo desde archivos `.audx`
- Sin exportacion de audio desencriptado
- Sin cache persistente de audio desencriptado
- Reproductor completo: play/pause, stop, seek, volumen, anterior/siguiente, repeat, shuffle y atajos de teclado
- Modo administrador protegido con codigo
- Frontend bilingue: espanol e ingles (selector `ES/EN`)
- No requiere internet para uso normal

## Estructura del proyecto

- `app.py`: punto de entrada de escritorio
- `secure_audio_app/api.py`: puente entre frontend y backend (`pywebview`)
- `secure_audio_app/crypto.py`: cifrado/descifrado y formato `.audx`
- `secure_audio_app/player.py`: capa de reproduccion en memoria con VLC
- `secure_audio_app/frontend/`: interfaz local
- `tests/`: pruebas unitarias
- `architecture.md`: arquitectura
- `threat_model.md`: modelo de amenazas
- `file_format_spec.md`: especificacion del formato `.audx`
- `development_plan.md`: plan de desarrollo

## Instalacion

1. Crear un entorno virtual (recomendado).
2. Instalar dependencias:

```bash
pip install -r requirements.txt
```

3. Verificar que VLC nativo este instalado en el sistema.
   `python-vlc` depende de la libreria VLC del SO (Windows/macOS/Linux).

## Ejecucion

```bash
python app.py
```

## Flujo de uso

1. Abrir la aplicacion (inicia en modo usuario).
2. Cambiar idioma con `ES/EN` si lo deseas.
3. Pulsar `Ingresar al admin` y escribir el codigo de administrador.
4. En modo administrador:
   seleccionar MP3, definir clave y carpeta de salida, luego encriptar a `.audx`.
5. Volver a modo usuario:
   abrir archivos `.audx`, escribir clave de reproduccion y reproducir.

## Seguridad

- El MP3 original no se necesita despues de encriptar.
- La reproduccion se hace con desencriptado en memoria.
- No existe una funcion para exportar el audio desencriptado.
- Se validan archivos malformados e integridad/autenticidad al descifrar.

Limitacion importante:
ninguna app de escritorio puede garantizar prevencion absoluta de copia cuando el audio ya se esta reproduciendo. Un atacante tecnico aun podria capturar audio por loopback del sistema, instrumentacion del proceso o tecnicas analogicas.

Consulta detalles en [threat_model.md](/d:/PROYECTO%20REPRODUCTOR%20CLASES%20PYTHON/threat_model.md#L1).

## Pruebas

```bash
python -m unittest discover -s tests
```

## Empaquetado

Generar build en cada SO destino (no cross-build).

### Windows

```powershell
pip install pyinstaller
pyinstaller --noconfirm --windowed --name SecureAudioPlayer --add-data "secure_audio_app\\frontend;secure_audio_app\\frontend" app.py
```

### macOS

```bash
pip install pyinstaller
pyinstaller --noconfirm --windowed --name SecureAudioPlayer --add-data "secure_audio_app/frontend:secure_audio_app/frontend" app.py
```

### Linux

```bash
pip install pyinstaller
pyinstaller --noconfirm --windowed --name SecureAudioPlayer --add-data "secure_audio_app/frontend:secure_audio_app/frontend" app.py
```

## Scripts de build

- [build_windows.ps1](/d:/PROYECTO%20REPRODUCTOR%20CLASES%20PYTHON/scripts/build_windows.ps1)
- [build_macos.sh](/d:/PROYECTO%20REPRODUCTOR%20CLASES%20PYTHON/scripts/build_macos.sh)
- [build_linux.sh](/d:/PROYECTO%20REPRODUCTOR%20CLASES%20PYTHON/scripts/build_linux.sh)
