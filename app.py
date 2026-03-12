from __future__ import annotations

import webview

from secure_audio_app.api import AppApi
from secure_audio_app.app_paths import frontend_dir


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
    webview.start(debug=False)


if __name__ == "__main__":
    main()
