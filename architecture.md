# Architecture

## Overview

The application is a local-first desktop player for encrypted audio containers. It uses:

- Python backend for cryptography, playlist control, and media orchestration.
- `pywebview` as a native desktop shell hosting a bundled local HTML/CSS/JS frontend.
- `python-vlc` for cross-platform playback using in-memory decrypted audio streams.
- A proprietary `.audx` container format with authenticated encryption and strict validation.

## High-Level Components

### 1. Desktop Shell

- Entry point: `app.py`
- Creates the application window with `pywebview`
- Registers a Python API bridge exposed to the frontend

### 2. Frontend

- Local static assets under `secure_audio_app/frontend/`
- Renders a modern player interface
- Handles playlist interactions, keyboard shortcuts, seek/volume/repeat/shuffle, and encryption flow
- Talks to Python through `pywebview.api`

### 3. Application API Layer

- File: `secure_audio_app/api.py`
- Exposes safe methods to the frontend:
  - file encryption
  - encrypted library loading
  - playback control
  - state polling
- Validates inputs and converts internal exceptions into user-friendly errors

### 4. Crypto and File Format

- File: `secure_audio_app/crypto.py`
- Implements:
  - Argon2id key derivation
  - AES-256-GCM authenticated encryption
  - per-file random salt and nonce
  - strict `.audx` parsing and integrity verification
- The container stores:
  - signed header fields
  - encrypted metadata + payload
  - authentication tag handled by AES-GCM

### 5. Playback Engine

- File: `secure_audio_app/player.py`
- Uses VLC media callbacks to serve decrypted bytes from memory
- Avoids writing decrypted MP3 content to disk
- Manages:
  - playlist
  - repeat/shuffle
  - position
  - volume
  - track transitions

### 6. Persistence

- Application data stored under a per-user app directory via `platformdirs`
- Includes:
  - preferences
  - logs if enabled later
- No decrypted audio cache is persisted

### 7. Tests

- Unit tests validate:
  - encrypt/decrypt round trips
  - file tamper detection
  - malformed header handling

## Runtime Flow

1. App starts and resolves local paths.
2. Frontend loads immediately.
3. User encrypts MP3 files into `.audx`.
4. User opens `.audx` files only.
5. Selected track is decrypted into memory just-in-time.
6. VLC reads bytes through Python callbacks.
7. Buffers are cleared when playback changes or stops where feasible.

## Design Choices

- `AES-256-GCM` was selected because it is mature, authenticated, and well-supported.
- `Argon2id` is the preferred KDF. If the local runtime lacks `argon2-cffi`, the app falls back to `scrypt`, which still meets the security requirement.
- `pywebview` provides a desktop-native shell while preserving a modern frontend development model.
- `VLC` is used for broad codec and platform compatibility.

## Packaging Strategy

- Package with `PyInstaller`
- Bundle:
  - frontend assets
  - VLC runtime requirements as needed per platform
  - application icon/resources
- Build separately on:
  - Windows
  - macOS
  - Linux

Cross-building is not assumed.
