from __future__ import annotations

import os
import subprocess
import sys
import traceback
from datetime import datetime
from pathlib import Path


def _startup_log_path() -> Path:
    base = Path.home() / "Library" / "Logs" / "Reproductor"
    base.mkdir(parents=True, exist_ok=True)
    return base / "startup.log"


def _write_startup_log(details: str) -> None:
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with _startup_log_path().open("a", encoding="utf-8") as fh:
            fh.write(f"[{timestamp}] {details}\n")
    except Exception:
        pass


def _report_fatal_startup_error(exc: Exception) -> None:
    details = f"{exc}\n\n{traceback.format_exc()}"
    _write_startup_log(details)
    _show_startup_error(
        "No se pudo iniciar la interfaz grafica.\n\n"
        "Posibles causas:\n"
        "- Build incompleto\n"
        "- Faltan librerias de Qt en el paquete\n"
        "- Faltan dependencias de VLC\n\n"
        f"Detalle tecnico:\n{exc}\n\n"
        f"Log: {_startup_log_path()}"
    )


def _show_startup_error(message: str) -> None:
    if sys.platform.startswith("win"):
        _show_windows_error(message)
        return
    if sys.platform == "darwin":
        _show_macos_error(message)
        return
    print(message, file=sys.stderr)


def _show_windows_error(message: str) -> None:
    try:
        from ctypes import windll

        windll.user32.MessageBoxW(0, message, "Error de inicio", 0x10)
    except Exception:
        pass


def _show_macos_error(message: str) -> None:
    escaped = message.replace("\\", "\\\\").replace('"', '\\"')
    script = f'display alert "Error de inicio" message "{escaped}" as critical'
    try:
        subprocess.run(["osascript", "-e", script], check=False)
    except Exception:
        print(message, file=sys.stderr)


def main() -> None:
    if sys.platform.startswith("win") or sys.platform == "darwin":
        # Force Qt backend for deterministic packaging/runtime behavior.
        os.environ.setdefault("QT_API", "pyside6")
        os.environ.setdefault("PYWEBVIEW_GUI", "qt")

    _write_startup_log(f"Inicio de app en plataforma={sys.platform}")

    try:
        import webview
        from secure_audio_app.api import AppApi
        from secure_audio_app.app_paths import frontend_dir
    except Exception as exc:
        _report_fatal_startup_error(exc)
        raise SystemExit(1) from exc

    api = AppApi()
    index_path = frontend_dir() / "index.html"
    if not index_path.exists():
        _show_startup_error(
            "No se encontro la interfaz web de la app (index.html).\n\n"
            "Reempaqueta incluyendo la carpeta:\n"
            "secure_audio_app/frontend"
        )
        raise SystemExit(1)

    window = webview.create_window(
        title="Reproductor de Audios",
        url=index_path.as_uri(),
        js_api=api,
        width=1280,
        height=860,
        min_size=(1080, 720),
        text_select=False,
    )
    api.set_window(window)
    start_kwargs = {"debug": False}
    if sys.platform.startswith("win") or sys.platform == "darwin":
        start_kwargs["gui"] = "qt"

    try:
        webview.start(**start_kwargs)
    except Exception as exc:
        _report_fatal_startup_error(exc)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        _report_fatal_startup_error(exc)
        raise
