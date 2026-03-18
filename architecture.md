# Architecture

## Overview

The application is a local-first desktop player for encrypted audio containers.

It uses:

- Python backend for cryptography and media orchestration.
- `customtkinter` for the desktop UI.
- `python-vlc` for playback from in-memory decrypted bytes.
- A proprietary `.audx` container with authenticated encryption.

## Components

### 1. Desktop Entry

- File: `app.py`
- Starts the Tkinter desktop application.

### 2. Desktop UI

- File: `secure_audio_app/customtkinter_app.py`
- Provides:
  - admin unlock flow
  - MP3 to AUDX encryption workflow
  - AUDX loading and playback controls
  - player state polling and keyboard shortcuts

### 3. Crypto and File Format

- File: `secure_audio_app/crypto.py`
- Implements:
  - Argon2id (fallback to scrypt)
  - AES-256-GCM encryption
  - strict AUDX parsing and validation

### 4. Playback Engine

- File: `secure_audio_app/player.py`
- Uses VLC callbacks to serve decrypted bytes from memory.
- Avoids writing decrypted MP3 content to disk.

### 5. Tests

- File: `tests/test_crypto.py`
- Validates encryption/decryption and tamper detection.

## Runtime Flow

1. App starts Tkinter UI.
2. Admin can encrypt MP3 files into AUDX.
3. User selects one AUDX file and enters passphrase.
4. Audio is decrypted in memory.
5. VLC consumes bytes via Python callbacks.
6. Buffers are wiped when media changes/stops.

## Packaging

- Windows: `Reproductor.spec` + `scripts/build_windows.ps1`
- macOS: `scripts/build_macos.sh`
- Linux: `scripts/build_linux.sh`

