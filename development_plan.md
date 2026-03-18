# Development Plan

## Current Status

The application is in a consolidated desktop stage with a single UI stack (`customtkinter`).

Completed:

- encrypted `.audx` container flow
- admin and user modes
- in-memory playback with VLC
- packaging scripts for Windows/macOS/Linux
- bilingual UI (ES/EN) with in-code translations
- UI state persistence on close/start

## Active Scope

- keep documentation aligned with current behavior
- improve usability details in user flow
- maintain compatibility and packaging stability

## Validation Checklist

- `python -m py_compile app.py secure_audio_app/customtkinter_app.py`
- `python -m unittest discover -s tests`
- manual smoke test:
  1. MP3 -> AUDX in admin mode
  2. load AUDX in user mode
  3. verify key panel hides after successful load
  4. reopen with `Abrir audio AUDX` and verify key panel returns
