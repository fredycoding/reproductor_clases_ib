# Development Plan

## Phase 1: Foundation

- Create project structure
- Add application paths and config helpers
- Add architecture, threat model, and file format specification
- Add initial README and requirements

Validation:

- import checks
- path resolution tests

## Phase 2: Cryptography and Container Format

- Implement `.audx` container serialization
- Implement Argon2id + AES-256-GCM encryption/decryption
- Add strict parsing and malformed file checks
- Add metadata extraction from MP3 files

Validation:

- round-trip tests
- tamper tests
- malformed header tests

## Phase 3: Playback Engine

- Implement in-memory byte stream for VLC callbacks
- Add playlist and transport controls
- Add repeat and shuffle behavior
- Add safe buffer cleanup paths

Validation:

- player state tests where possible
- static checks

## Phase 4: Desktop UI

- Build local frontend with playlist and transport UI
- Connect frontend to Python API through pywebview
- Add keyboard shortcuts and user feedback

Validation:

- manual end-to-end test on local machine

## Phase 5: Packaging and Documentation

- Add PyInstaller build commands
- Document Windows/macOS/Linux packaging steps
- Finalize README with workflow and threat model summary

Validation:

- syntax compile
- run unit tests
