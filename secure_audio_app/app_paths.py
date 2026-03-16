from __future__ import annotations

import os
import sys
from pathlib import Path

try:
    from platformdirs import user_data_dir
except ModuleNotFoundError:
    user_data_dir = None


APP_NAME = "SecureAudioPlayer"
APP_AUTHOR = "LocalSecureAudio"


def project_root() -> Path:
    if getattr(sys, "frozen", False):
        # PyInstaller may expose app resources via _MEIPASS (onefile/onedir internals).
        return Path(getattr(sys, "_MEIPASS", Path(sys.executable).resolve().parent))
    return Path(__file__).resolve().parent.parent


def frontend_dir() -> Path:
    relative = Path("secure_audio_app") / "frontend"

    candidates = [project_root() / relative]

    if getattr(sys, "frozen", False):
        exe_dir = Path(sys.executable).resolve().parent
        candidates.extend(
            [
                exe_dir / relative,
                exe_dir.parent / "Resources" / relative,
                Path(getattr(sys, "_MEIPASS", exe_dir)) / relative,
            ]
        )

    for candidate in candidates:
        if (candidate / "index.html").exists():
            return candidate

    # Return first candidate as deterministic fallback for diagnostics.
    return candidates[0]


def user_data_path() -> Path:
    if user_data_dir is not None:
        path = Path(user_data_dir(APP_NAME, APP_AUTHOR))
    else:
        home = Path.home()
        if os.name == "nt":
            base = Path(os.environ.get("APPDATA", home))
        else:
            base = home / ".local" / "share"
        path = base / APP_NAME
    path.mkdir(parents=True, exist_ok=True)
    return path
