from __future__ import annotations

import os
from pathlib import Path

try:
    from platformdirs import user_data_dir
except ModuleNotFoundError:
    user_data_dir = None


APP_NAME = "SecureAudioPlayer"
APP_AUTHOR = "LocalSecureAudio"


def project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def frontend_dir() -> Path:
    return project_root() / "secure_audio_app" / "frontend"


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
