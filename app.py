from __future__ import annotations

import os
import sys

import webview

from secure_audio_app.api import AppApi
from secure_audio_app.app_paths import frontend_dir

if sys.platform.startswith("win"):
    # Force PyQt5 backend selection and avoid .NET/pythonnet runtime dependency.
    os.environ.setdefault("QT_API", "pyside6")
    os.environ.setdefault("PYWEBVIEW_GUI", "qt")


def main() -> None:
    api = AppApi()
    index_path = frontend_dir() / "index.html"
    if not index_path.exists():
        _show_windows_error(
            "No se encontro la interfaz web de la app (index.html).\n\n"
            "Reempaqueta incluyendo la carpeta:\n"
            "secure_audio_app\\frontend\n\n"
            "Tip: usa scripts\\build_windows.ps1"
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
    if sys.platform.startswith("win"):
        start_kwargs["gui"] = "qt"

    try:
        webview.start(**start_kwargs)
    except Exception as exc:
        if sys.platform.startswith("win"):
            _show_windows_error(
                "No se pudo iniciar la interfaz grafica.\n\n"
                "Posibles causas:\n"
                "- Build incompleto\n"
                "- Faltan librerias de Qt en el paquete\n"
                "- La app se ejecuta desde una ruta de red\n\n"
                f"Detalle tecnico:\n{exc}\n\n"
                "Solucion recomendada:\n"
                "1) Reconstruir con scripts\\build_windows.ps1\n"
                "2) Copiar la carpeta completa de dist\\Reproductor\n"
                "3) Ejecutar desde disco local"
            )
            raise SystemExit(1) from exc
        raise


def _show_windows_error(message: str) -> None:
    if not sys.platform.startswith("win"):
        return
    try:
        from ctypes import windll

        windll.user32.MessageBoxW(0, message, "Error de inicio", 0x10)
    except Exception:
        pass


if __name__ == "__main__":
    main()

