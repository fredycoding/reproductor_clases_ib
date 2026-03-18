#!/usr/bin/env bash
set -euo pipefail

pip install --upgrade pip pyinstaller
pip install -r requirements.txt

python - <<'PY'
import tkinter, vlc, mutagen, cryptography
print("Runtime Tkinter OK")
PY

pyinstaller --noconfirm --clean --windowed --name Reproductor app.py
