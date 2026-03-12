# Secure Audio Player

Cross-platform desktop application in Python for encrypting MP3 files into a proprietary `.audx` container and playing them locally through a bundled desktop UI.

## Stack

- Python backend
- `pywebview` for the desktop shell and embedded local web UI
- local HTML/CSS/JavaScript frontend
- `cryptography` + `argon2-cffi` for authenticated encryption and key derivation
- `python-vlc` for playback from memory

## Features

- Encrypt one or more MP3 files into `.audx`
- AES-256-GCM authenticated encryption with per-file random nonce
- Argon2id key derivation with per-file salt, with secure scrypt fallback if Argon2id is unavailable in the runtime
- Playback only from encrypted `.audx` files created by this app
- No export of decrypted files
- No persistent decrypted cache
- Playlist, seek, volume, next/previous, repeat, shuffle, keyboard shortcuts
- No activation token required

## Project Structure

- `app.py`: desktop entry point
- `secure_audio_app/api.py`: bridge exposed to `pywebview`
- `secure_audio_app/crypto.py`: `.audx` format and encryption
- `secure_audio_app/player.py`: in-memory playback layer on VLC
- `secure_audio_app/frontend/`: local embedded UI
- `tests/`: unit tests
- `architecture.md`: system design
- `threat_model.md`: limitations and security goals
- `file_format_spec.md`: `.audx` specification
- `development_plan.md`: implementation phases

## Setup

1. Create a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Ensure VLC is installed on the target machine.
   `python-vlc` needs the native VLC runtime available on Windows, macOS, and Linux.

## Run

```bash
python app.py
```

## Sample Encrypted File Workflow

1. Launch the app.
2. Select one or more MP3 files in the encryption panel.
3. Choose a strong passphrase and an output directory.
4. Encrypt the files into `.audx`.
5. Open the generated `.audx` files in the playlist panel.
6. Enter the same passphrase and play them from the encrypted library.

## Security Notes

- The original MP3 is not required after encryption.
- Playback is designed to decrypt only into memory and stream bytes directly to VLC callbacks.
- The app does not provide a decrypted export feature and does not keep a plaintext cache on disk.
- The project includes malformed file checks and authenticated decryption checks.

## Threat Model Summary

This project protects audio at rest and raises the cost of casual extraction. It does not provide unbreakable DRM.

No desktop player can fully prevent copying once audio is being played. A determined attacker may still capture audio through:

- OS loopback recording
- process instrumentation
- memory inspection
- analog recording

See [threat_model.md](/d:/PROYECTO%20REPRODUCTOR%20CLASES%20PYTHON/threat_model.md#L1) for details.

## Tests

Run the unit tests:

```bash
python -m unittest discover -s tests
```

## Packaging

Use separate builds per operating system. Build on each target OS rather than cross-compiling.

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

## Build Scripts

- [build_windows.ps1](/d:/PROYECTO%20REPRODUCTOR%20CLASES%20PYTHON/scripts/build_windows.ps1)
- [build_macos.sh](/d:/PROYECTO%20REPRODUCTOR%20CLASES%20PYTHON/scripts/build_macos.sh)
- [build_linux.sh](/d:/PROYECTO%20REPRODUCTOR%20CLASES%20PYTHON/scripts/build_linux.sh)
