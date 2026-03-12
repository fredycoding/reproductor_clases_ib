from __future__ import annotations

import os
import sys

import webview

from secure_audio_app.api import AppApi
from secure_audio_app.app_paths import frontend_dir

if sys.platform.startswith("win"):
    # Force Edge WebView2 backend selection before pywebview initializes GUI backends.
    os.environ.setdefault("PYWEBVIEW_GUI", "edgechromium")


def main() -> None:
    api = AppApi()
    index_path = frontend_dir() / "index.html"
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
        # Force Edge WebView2 backend on Windows to avoid pythonnet/winforms dependency.
        start_kwargs["gui"] = "edgechromium"
    try:
        webview.start(**start_kwargs)
    except Exception as exc:
        message = str(exc)
        if sys.platform.startswith("win") and (
            "Python.Runtime.Loader.Initialize" in message
            or "pythonnet" in message.lower()
            or "clr_loader" in message.lower()
            or "winforms" in message.lower()
        ):
            _show_windows_error(
                "No se pudo iniciar la interfaz grafica.\n\n"
                "Posibles causas en el equipo destino:\n"
                "- Falta .NET Framework 4.8\n"
                "- Falta Microsoft Visual C++ Redistributable x64\n"
                "- La app se ejecuta desde una ruta de red\n\n"
                "Solucion recomendada:\n"
                "1) Copiar la carpeta completa de la app a disco local\n"
                "2) Instalar .NET Framework 4.8 y VC++ x64\n"
                "3) Ejecutar nuevamente"
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
