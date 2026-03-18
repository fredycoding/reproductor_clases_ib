# Architecture

## Overview

Desktop application for protected audio distribution and playback.

Stack:

- Python application core
- `customtkinter` UI
- `python-vlc` playback engine
- proprietary `.audx` encrypted container

## Main Components

## 1. Desktop entry

- File: `app.py`
- Starts the official desktop app.

## 2. UI layer

- File: `secure_audio_app/customtkinter_app.py`
- Responsibilities:
  - admin unlock flow
  - MP3 -> AUDX workflow
  - AUDX load and playback controls
  - language switching (ES/EN) using in-code dictionary
  - UI state persistence on close/start

## 3. Crypto and container

- File: `secure_audio_app/crypto.py`
- Responsibilities:
  - Argon2id (fallback: scrypt)
  - AES-256-GCM encryption/decryption
  - strict AUDX parse and validation

## 4. Playback engine

- File: `secure_audio_app/player.py`
- Responsibilities:
  - feed decrypted bytes to VLC via callbacks
  - avoid writing decrypted MP3 to disk

## 5. Tests

- File: `tests/test_crypto.py`
- Covers:
  - encrypt/decrypt roundtrip
  - tamper detection

## Runtime Flow

1. App starts and restores saved state (language, window geometry, mode, volume, output folder).
2. Admin can encrypt MP3 files into AUDX.
3. User opens one AUDX file and enters passphrase.
4. On successful load, key panel is hidden until user opens another AUDX.
5. VLC reads decrypted bytes from memory.
6. Controls available: play/pause, stop, seek, volume.

## Packaging

- Windows: `Reproductor.spec` + `scripts/build_windows.ps1`
- macOS: `scripts/build_macos.sh`
- Linux: `scripts/build_linux.sh`
