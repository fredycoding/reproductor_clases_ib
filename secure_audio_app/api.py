from __future__ import annotations

import hashlib
import hmac
import json
from dataclasses import asdict
from typing import Any

import webview

from .crypto import AuthenticationError, AudxCrypto, InvalidContainerError, SecureAudioError
from .player import SecureVlcPlayer

ADMIN_CODE_SHA256 = "c9bc710759f356523ecc7669b32e94c88b2c6e55496dc75fa23247156e72ca09"


class AppApi:
    def __init__(self) -> None:
        self.crypto = AudxCrypto()
        self.player: SecureVlcPlayer | None = None
        self.player_init_error: str | None = None
        try:
            self.player = SecureVlcPlayer(self.crypto)
        except Exception as exc:
            self.player_init_error = (
                "Motor de audio no disponible (VLC/libvlc). "
                "Instala VLC en el sistema para habilitar reproduccion. "
                f"Detalle: {exc}"
            )
        self.window: webview.Window | None = None
        self.pending_encrypt_files: list[str] = []
        self.admin_unlocked = False

    def set_window(self, window: webview.Window) -> None:
        self.window = window

    def bootstrap(self) -> dict[str, Any]:
        return {
            "ok": True,
            "version": "1.0.0",
            "admin": {
                "has_pin": True,
                "unlocked": self.admin_unlocked,
            },
            "audio": {
                "ready": self.player is not None,
                "error": self.player_init_error or "",
            },
        }

    def admin_status(self) -> dict[str, Any]:
        return {
            "ok": True,
            "admin": {
                "has_pin": True,
                "unlocked": self.admin_unlocked,
            },
            "audio": {
                "ready": self.player is not None,
                "error": self.player_init_error or "",
            },
        }

    def admin_unlock(self, admin_code: str) -> dict[str, Any]:
        try:
            candidate = hashlib.sha256(admin_code.strip().encode("utf-8")).hexdigest()
            if not hmac.compare_digest(candidate, ADMIN_CODE_SHA256):
                raise SecureAudioError("Codigo de administrador incorrecto.")
            self.admin_unlocked = True
            return {"ok": True, "admin": {"has_pin": True, "unlocked": True}}
        except SecureAudioError as exc:
            return {"ok": False, "error": str(exc)}

    def admin_lock(self) -> dict[str, Any]:
        self.admin_unlocked = False
        self.pending_encrypt_files = []
        return {"ok": True, "admin": {"has_pin": True, "unlocked": False}}

    def browse_mp3_files(self) -> dict[str, Any]:
        try:
            self._require_admin_unlocked()
            selected = self._require_window().create_file_dialog(
                webview.OPEN_DIALOG,
                allow_multiple=True,
                file_types=("MP3 files (*.mp3)",),
            )
            self.pending_encrypt_files = list(selected or [])
            return {"ok": True, "files": self.pending_encrypt_files}
        except (SecureAudioError, RuntimeError) as exc:
            return {"ok": False, "error": str(exc)}

    def choose_output_dir(self) -> dict[str, Any]:
        try:
            self._require_admin_unlocked()
            selected = self._require_window().create_file_dialog(webview.FOLDER_DIALOG)
            return {"ok": True, "directory": selected[0] if selected else ""}
        except (SecureAudioError, RuntimeError) as exc:
            return {"ok": False, "error": str(exc)}

    def encrypt_selected_files(self, password: str, output_dir: str) -> dict[str, Any]:
        try:
            self._require_admin_unlocked()
            if not self.pending_encrypt_files:
                raise SecureAudioError("No MP3 files selected.")
            if not output_dir:
                raise SecureAudioError("An output directory is required.")
            created = [
                str(self.crypto.encrypt_file(source_path=file_path, password=password, output_dir=output_dir))
                for file_path in self.pending_encrypt_files
            ]
            return {"ok": True, "created": created}
        except (SecureAudioError, OSError) as exc:
            return {"ok": False, "error": str(exc)}

    def browse_encrypted_files(self) -> dict[str, Any]:
        selected = self._require_window().create_file_dialog(
            webview.OPEN_DIALOG,
            allow_multiple=True,
            file_types=("AUDX files (*.audx)",),
        )
        return {"ok": True, "files": list(selected or [])}

    def load_playlist(self, files_json: str, password: str) -> dict[str, Any]:
        try:
            player = self._require_player()
            files = json.loads(files_json)
            entries = player.load_playlist(files, password)
            return {
                "ok": True,
                "playlist": [asdict(entry) for entry in entries],
                "state": asdict(player.snapshot()),
            }
        except (json.JSONDecodeError, InvalidContainerError, AuthenticationError, SecureAudioError, OSError) as exc:
            return {"ok": False, "error": str(exc)}

    def playback_command(self, command: str, value: Any = None) -> dict[str, Any]:
        try:
            player = self._require_player()
            if command == "play":
                state = player.play_index(int(value))
            elif command == "toggle":
                state = player.toggle_play_pause()
            elif command == "pause":
                state = player.pause()
            elif command == "stop":
                state = player.stop()
            elif command == "next":
                state = player.next_track()
            elif command == "previous":
                state = player.previous_track()
            elif command == "seek":
                state = player.seek(float(value))
            elif command == "volume":
                state = player.set_volume(int(value))
            elif command == "repeat":
                state = player.set_repeat_mode(str(value))
            elif command == "shuffle":
                state = player.set_shuffle(bool(value))
            else:
                raise SecureAudioError("Unsupported playback command.")
            return {"ok": True, "state": asdict(state)}
        except (ValueError, SecureAudioError, IndexError) as exc:
            return {"ok": False, "error": str(exc)}

    def poll_state(self) -> dict[str, Any]:
        try:
            player = self._require_player()
            return {"ok": True, "state": asdict(player.snapshot())}
        except SecureAudioError as exc:
            return {"ok": False, "error": str(exc)}

    def _require_window(self) -> webview.Window:
        if self.window is None:
            raise RuntimeError("Application window is not ready.")
        return self.window

    def _require_admin_unlocked(self) -> None:
        if not self.admin_unlocked:
            raise SecureAudioError("Debes desbloquear la zona de administrador con el codigo.")

    def _require_player(self) -> SecureVlcPlayer:
        if self.player is None:
            if self.player_init_error:
                raise SecureAudioError(self.player_init_error)
            raise SecureAudioError("Motor de audio no disponible.")
        return self.player
