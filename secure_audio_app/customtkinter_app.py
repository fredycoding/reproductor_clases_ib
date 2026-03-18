
from __future__ import annotations

import hashlib
import hmac
import json
import threading
import tkinter as tk
import traceback
from pathlib import Path
from tkinter import filedialog
from typing import Any, Callable

import customtkinter as ctk

from .crypto import AuthenticationError, AudxCrypto, InvalidContainerError, SecureAudioError
from .player import PlaylistEntry, PlayerState, SecureVlcPlayer

ADMIN_CODE_SHA256 = "c9bc710759f356523ecc7669b32e94c88b2c6e55496dc75fa23247156e72ca09"


class CustomTkSecureAudioApp:
    TEXTS: dict[str, dict[str, str]] = {
        "es": {
            "title": "Reproductor Audio",
            "lang": "Idioma",
            "mode_user": "Usuario",
            "mode_admin": "Admin",
            "enter_admin": "Ingresar al admin",
            "lock_admin": "Bloquear admin",
            "admin_code": "Codigo admin",
            "unlock": "Desbloquear",
            "summary": "Resumen",
            "summary_user": "Carga un archivo AUDX y reproduce.",
            "summary_admin": "Convierte MP3 a AUDX con clave segura.",
            "zone_user": "Zona de usuario",
            "zone_admin": "Zona de administrador",
            "switching": "Cambiando audio...",
            "no_track": "Sin pista seleccionada",
            "mp3_files": "Archivos MP3",
            "select_mp3": "Seleccionar MP3",
            "prepare": "Preparar biblioteca",
            "access_key": "Clave de acceso",
            "output_folder": "Carpeta de salida",
            "browse": "Examinar",
            "selected_audio": "Audio seleccionado",
            "open_audx": "Abrir audio AUDX",
            "playback_key": "Clave de reproduccion",
            "load_audio": "Cargar audio",
            "loaded_audio": "Audio cargado",
            "no_audio_loaded": "Ningun audio cargado",
            "previous": "Anterior",
            "play_pause": "Play/Pausa",
            "stop": "Detener",
            "next": "Siguiente",
            "volume": "Volumen",
            "ready": "Listo",
            "engine_error": "Motor de audio no disponible: {error}",
            "must_unlock": "Debes desbloquear admin",
            "bad_admin_code": "Codigo de admin incorrecto",
            "admin_unlocked": "Admin desbloqueado",
            "admin_locked": "Admin bloqueado",
            "dialog_select_mp3": "Seleccionar MP3",
            "dialog_output": "Carpeta de salida",
            "dialog_open_audx": "Abrir audio AUDX",
            "mp3_selected": "MP3 seleccionados: {count}",
            "no_mp3": "No hay MP3 seleccionados",
            "need_output": "Debes elegir carpeta de salida",
            "processing": "Procesando biblioteca...",
            "processed": "Archivos procesados: {count}",
            "audx_selected": "Archivo seleccionado. Ingresa clave y carga audio.",
            "need_audx": "Primero selecciona un AUDX",
            "need_key": "Ingresa clave de reproduccion",
            "loading_audio": "Cargando audio...",
            "audio_loaded": "Audio cargado",
            "generic_error": "Error: {error}",
        },
        "en": {
            "title": "Reproductor Audio",
            "lang": "Language",
            "mode_user": "User",
            "mode_admin": "Admin",
            "enter_admin": "Enter admin",
            "lock_admin": "Lock admin",
            "admin_code": "Admin code",
            "unlock": "Unlock",
            "summary": "Summary",
            "summary_user": "Load an AUDX file and play it.",
            "summary_admin": "Convert MP3 to AUDX with secure key.",
            "zone_user": "User zone",
            "zone_admin": "Administrator zone",
            "switching": "Switching audio...",
            "no_track": "No track selected",
            "mp3_files": "MP3 files",
            "select_mp3": "Select MP3",
            "prepare": "Prepare library",
            "access_key": "Access key",
            "output_folder": "Output folder",
            "browse": "Browse",
            "selected_audio": "Selected audio",
            "open_audx": "Open AUDX audio",
            "playback_key": "Playback key",
            "load_audio": "Load audio",
            "loaded_audio": "Loaded audio",
            "no_audio_loaded": "No audio loaded",
            "previous": "Previous",
            "play_pause": "Play/Pause",
            "stop": "Stop",
            "next": "Next",
            "volume": "Volume",
            "ready": "Ready",
            "engine_error": "Audio engine unavailable: {error}",
            "must_unlock": "You must unlock admin",
            "bad_admin_code": "Invalid admin code",
            "admin_unlocked": "Admin unlocked",
            "admin_locked": "Admin locked",
            "dialog_select_mp3": "Select MP3",
            "dialog_output": "Output folder",
            "dialog_open_audx": "Open AUDX audio",
            "mp3_selected": "MP3 selected: {count}",
            "no_mp3": "No MP3 selected",
            "need_output": "You must choose output folder",
            "processing": "Processing library...",
            "processed": "Files processed: {count}",
            "audx_selected": "File selected. Enter key and load audio.",
            "need_audx": "Select an AUDX file first",
            "need_key": "Enter playback key",
            "loading_audio": "Loading audio...",
            "audio_loaded": "Audio loaded",
            "generic_error": "Error: {error}",
        },
    }

    def __init__(self, root: ctk.CTk) -> None:
        self.root = root
        self.state_data = self._load_state()
        self.language = self.state_data.get("language", "es")
        if self.language not in self.TEXTS:
            self.language = "es"

        self.root.title(self._t("title"))
        self.root.minsize(1080, 720)

        self.admin_unlocked = False
        self.current_mode = "user"
        self.selected_mp3_files: list[str] = []
        self.pending_audx_file = ""
        self.playlist: list[PlaylistEntry] = []
        self.current_state: PlayerState | None = None
        self._suspend_volume_event = False

        self.crypto = AudxCrypto()
        self.player: SecureVlcPlayer | None = None
        self.player_init_error = ""
        try:
            self.player = SecureVlcPlayer(self.crypto)
        except Exception as exc:
            self.player_init_error = self._t("engine_error", error=exc)

        self._build_ui()
        self.root.after(0, self._set_startup_window_mode)
        self._bind_shortcuts()
        self._set_mode(self.state_data.get("last_mode", "user"))
        if self.player_init_error:
            self._set_status(self.player_init_error, is_error=True)
        else:
            self._set_status(self._t("ready"))

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self._poll_state()

    def _t(self, key: str, **kwargs: Any) -> str:
        text = self.TEXTS.get(self.language, self.TEXTS["es"]).get(key, key)
        return text.format(**kwargs) if kwargs else text

    def _state_file_path(self) -> Path:
        base = Path.home() / ".secure_audio_player"
        base.mkdir(parents=True, exist_ok=True)
        return base / "state.json"

    def _load_state(self) -> dict[str, Any]:
        try:
            path = self._state_file_path()
            if not path.exists():
                return {}
            data = json.loads(path.read_text(encoding="utf-8"))
            return data if isinstance(data, dict) else {}
        except Exception:
            return {}

    def _save_state(self) -> None:
        output_value = self.output_entry.get().strip() if hasattr(self, "output_entry") else ""
        if output_value == self._t("output_folder"):
            output_value = ""
        data = {
            "language": self.language,
            "window_geometry": self.root.geometry(),
            "last_mode": self.current_mode,
            "volume": int(float(self.volume_slider.get())) if hasattr(self, "volume_slider") else 80,
            "output_folder": output_value,
        }
        try:
            self._state_file_path().write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception:
            pass

    def _on_close(self) -> None:
        self._save_state()
        self.root.destroy()

    def _set_startup_window_mode(self) -> None:
        self.root.update_idletasks()
        self.root.attributes("-fullscreen", False)
        try:
            self.root.state("normal")
        except Exception:
            pass

        saved_geometry = self.state_data.get("window_geometry", "")
        if isinstance(saved_geometry, str) and saved_geometry:
            try:
                self.root.geometry(saved_geometry)
                self.root.update_idletasks()
                return
            except Exception:
                pass

        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        window_w = min(1720, max(1280, int(screen_w * 0.88)))
        window_h = min(860, max(680, int(screen_h * 0.78)))
        pos_x = max(0, (screen_w - window_w) // 2)
        pos_y = max(0, (screen_h - window_h) // 2)
        self.root.geometry(f"{window_w}x{window_h}+{pos_x}+{pos_y}")
        self.root.update_idletasks()

    def _mode_label(self, mode: str) -> str:
        return self._t("mode_admin") if mode == "admin" else self._t("mode_user")

    def _mode_from_label(self, value: str) -> str:
        return "admin" if value == self._t("mode_admin") else "user"

    def _build_ui(self) -> None:
        ctk.set_appearance_mode("dark")
        ctk.set_widget_scaling(1.15)
        ctk.set_window_scaling(1.08)
        ctk.set_default_color_theme("blue")

        shell = ctk.CTkFrame(self.root, fg_color="#060B17")
        shell.pack(fill="both", expand=True, padx=12, pady=12)
        shell.grid_columnconfigure(1, weight=1)
        shell.grid_rowconfigure(0, weight=1)

        self.sidebar = ctk.CTkFrame(shell, width=320, fg_color="#0A1328", corner_radius=18)
        self.sidebar.grid(row=0, column=0, sticky="nsw", padx=(0, 12))
        self.sidebar.grid_propagate(False)

        self.main = ctk.CTkFrame(shell, fg_color="#091225", corner_radius=18)
        self.main.grid(row=0, column=1, sticky="nsew")
        self.main.grid_columnconfigure(0, weight=1)
        self.main.grid_rowconfigure(1, weight=1)

        self._build_sidebar()
        self._build_main()
        self._apply_language()

    def _build_sidebar(self) -> None:
        self.brand_label = ctk.CTkLabel(self.sidebar, text="AUDIO PLAYER // I.B.", font=ctk.CTkFont("Arial", 28, "bold"), text_color="#F6FAFF")
        self.brand_label.pack(anchor="w", padx=18, pady=(18, 12))

        lang_box = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        lang_box.pack(fill="x", padx=18, pady=(0, 8))
        self.language_label = ctk.CTkLabel(lang_box, text="", text_color="#D7E4FF", font=ctk.CTkFont("Arial", 13, "bold"))
        self.language_label.pack(anchor="w", pady=(0, 4))
        self.language_segment = ctk.CTkSegmentedButton(
            lang_box,
            values=["ES", "EN"],
            command=self._on_language_change,
            fg_color="#15294A",
            selected_color="#2E6FFF",
            selected_hover_color="#5A8DFF",
            unselected_color="#0F2341",
            unselected_hover_color="#203B69",
            text_color="#F6FAFF",
            font=ctk.CTkFont("Arial", 13, "bold"),
            height=34,
        )
        self.language_segment.pack(fill="x")
        self.language_segment.set("EN" if self.language == "en" else "ES")

        self.mode_segment = ctk.CTkSegmentedButton(
            self.sidebar,
            values=[self._mode_label("user"), self._mode_label("admin")],
            command=self._on_mode_segment,
            fg_color="#15294A",
            selected_color="#2E6FFF",
            selected_hover_color="#5A8DFF",
            unselected_color="#0F2341",
            unselected_hover_color="#203B69",
            text_color="#F6FAFF",
            font=ctk.CTkFont("Arial", 16, "bold"),
            height=44,
        )
        self.mode_segment.pack(fill="x", padx=18, pady=(6, 10))

        self.admin_btn = ctk.CTkButton(self.sidebar, text="", command=self._toggle_admin_panel, fg_color="#2E6FFF", hover_color="#5A8DFF", font=ctk.CTkFont("Arial", 16, "bold"), height=44)
        self.admin_btn.pack(fill="x", padx=18, pady=(0, 8))

        self.lock_btn = ctk.CTkButton(self.sidebar, text="", command=self._lock_admin, fg_color="#1E3764", hover_color="#355B9F", font=ctk.CTkFont("Arial", 16, "bold"), height=44)

        self.mode_summary = ctk.CTkLabel(self.sidebar, text="", justify="left", wraplength=270, text_color="#BFD1F4", font=ctk.CTkFont("Arial", 14))
        self.mode_summary.pack(fill="x", padx=18, pady=(2, 10))

        self.admin_panel = ctk.CTkFrame(self.sidebar, fg_color="#101F3A", corner_radius=14)
        self.admin_panel.pack(fill="x", padx=18, pady=(0, 8))
        self.admin_panel.pack_forget()

        self.admin_code_label = ctk.CTkLabel(self.admin_panel, text="", text_color="#F6FAFF", font=ctk.CTkFont("Arial", 16, "bold"))
        self.admin_code_label.pack(anchor="w", padx=10, pady=(10, 6))
        self.admin_code_entry = ctk.CTkEntry(self.admin_panel, show="*", height=36)
        self.admin_code_entry.pack(fill="x", padx=10)
        self.unlock_btn = ctk.CTkButton(self.admin_panel, text="", command=self._unlock_admin, fg_color="#2E6FFF", hover_color="#5A8DFF", font=ctk.CTkFont("Arial", 16, "bold"))
        self.unlock_btn.pack(fill="x", padx=10, pady=10)

        summary_card = ctk.CTkFrame(self.sidebar, fg_color="#101F3A", corner_radius=14)
        summary_card.pack(fill="x", padx=18, pady=(0, 12))
        self.summary_title = ctk.CTkLabel(summary_card, text="", text_color="#F6FAFF", font=ctk.CTkFont("Arial", 16, "bold"))
        self.summary_title.pack(anchor="w", padx=10, pady=(10, 4))
        self.summary_text = ctk.CTkLabel(summary_card, text="", justify="left", wraplength=260, text_color="#BFD1F4", font=ctk.CTkFont("Arial", 14))
        self.summary_text.pack(fill="x", padx=10, pady=(0, 10))

    def _build_main(self) -> None:
        top = ctk.CTkFrame(self.main, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew", padx=14, pady=(12, 8))
        top.grid_columnconfigure(0, weight=1)

        self.zone_title = ctk.CTkLabel(top, text="", text_color="#F6FAFF", font=ctk.CTkFont("Arial", 30, "bold"))
        self.zone_title.grid(row=0, column=0, sticky="w")

        self.track_loading_label = ctk.CTkLabel(top, text="", text_color="#8FB4FF", font=ctk.CTkFont("Arial", 15, "bold"))
        self.track_loading_label.grid(row=0, column=1, sticky="e")
        self.track_loading_label.grid_remove()

        self.now_playing = ctk.CTkLabel(top, text="", text_color="#BFD1F4", font=ctk.CTkFont("Arial", 16))
        self.now_playing.grid(row=1, column=0, sticky="w", pady=(4, 0))

        body = ctk.CTkFrame(self.main, fg_color="transparent")
        body.grid(row=1, column=0, sticky="nsew", padx=14, pady=(0, 10))
        body.grid_columnconfigure(0, weight=1)
        body.grid_rowconfigure(0, weight=1)

        self.admin_view = ctk.CTkFrame(body, fg_color="#0E1A31", corner_radius=16)
        self.user_view = ctk.CTkFrame(body, fg_color="#0E1A31", corner_radius=16)
        self.admin_view.grid(row=0, column=0, sticky="nsew")
        self.user_view.grid(row=0, column=0, sticky="nsew")

        self._build_admin_view()
        self._build_user_view()

        status = ctk.CTkFrame(self.main, fg_color="#101C35", corner_radius=14)
        status.grid(row=2, column=0, sticky="ew", padx=14, pady=(0, 12))
        status.grid_columnconfigure(1, weight=1)
        self.status_spinner = ctk.CTkProgressBar(status, mode="indeterminate", width=120, progress_color="#4B8BFF")
        self.status_spinner.grid(row=0, column=0, padx=(10, 10), pady=10, sticky="w")
        self.status_spinner.grid_remove()
        self.status_label = ctk.CTkLabel(status, text="", text_color="#F6FAFF", font=ctk.CTkFont("Arial", 15, "bold"))
        self.status_label.grid(row=0, column=1, sticky="w")

    def _build_admin_view(self) -> None:
        self.admin_view.grid_columnconfigure(0, weight=1)
        self.admin_view.grid_columnconfigure(1, weight=1)
        self.admin_view.grid_rowconfigure(1, weight=1)

        left = ctk.CTkFrame(self.admin_view, fg_color="#122142", corner_radius=14)
        left.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=(10, 6), pady=10)
        left.grid_columnconfigure(0, weight=1)

        self.mp3_title = ctk.CTkLabel(left, text="", text_color="#F6FAFF", font=ctk.CTkFont("Arial", 18, "bold"))
        self.mp3_title.pack(anchor="w", padx=10, pady=(10, 6))

        self.select_mp3_btn = ctk.CTkButton(left, text="", command=self._select_mp3, fg_color="#2E6FFF", hover_color="#5A8DFF", height=42, font=ctk.CTkFont("Arial", 15, "bold"))
        self.select_mp3_btn.pack(anchor="w", padx=10, pady=(0, 8))

        self.mp3_list = tk.Listbox(left, bg="#0A1428", fg="#F8FAFF", selectbackground="#2F6BFF", relief="flat", font=("Arial", 12), height=18)
        self.mp3_list.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        right = ctk.CTkFrame(self.admin_view, fg_color="#122142", corner_radius=14)
        right.grid(row=0, column=1, sticky="new", padx=(6, 10), pady=10)
        right.grid_columnconfigure(0, weight=1)

        self.prepare_title = ctk.CTkLabel(right, text="", text_color="#F6FAFF", font=ctk.CTkFont("Arial", 18, "bold"))
        self.prepare_title.grid(row=0, column=0, sticky="w", padx=10, pady=(10, 6))

        self.access_key_label = ctk.CTkLabel(right, text="", text_color="#D7E4FF", font=ctk.CTkFont("Arial", 14))
        self.access_key_label.grid(row=1, column=0, sticky="w", padx=10)

        self.encrypt_pass = ctk.CTkEntry(right, show="*")
        self.encrypt_pass.grid(row=2, column=0, sticky="ew", padx=10, pady=(4, 8))

        out_row = ctk.CTkFrame(right, fg_color="transparent")
        out_row.grid(row=3, column=0, sticky="ew", padx=10)
        out_row.grid_columnconfigure(0, weight=1)

        self.output_entry = ctk.CTkEntry(out_row)
        self.output_entry.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self.output_entry.configure(state="readonly")

        self.browse_btn = ctk.CTkButton(out_row, text="", command=self._choose_output, width=140, height=40, fg_color="#315CAB", hover_color="#4D75CC", font=ctk.CTkFont("Arial", 14, "bold"))
        self.browse_btn.grid(row=0, column=1)

        self.prepare_btn = ctk.CTkButton(right, text="", command=self._encrypt_selected, fg_color="#2E6FFF", hover_color="#5A8DFF", font=ctk.CTkFont("Arial", 15, "bold"))
        self.prepare_btn.grid(row=4, column=0, sticky="ew", padx=10, pady=(10, 10))

        self._set_output_entry(self.state_data.get("output_folder", ""))

    def _build_user_view(self) -> None:
        self.user_view.grid_columnconfigure(0, weight=1)
        self.user_view.grid_rowconfigure(0, weight=1)

        panel = ctk.CTkFrame(self.user_view, fg_color="#122142", corner_radius=14)
        panel.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        panel.grid_columnconfigure(0, weight=1)

        self.selected_audio_title = ctk.CTkLabel(panel, text="", text_color="#F6FAFF", font=ctk.CTkFont("Arial", 20, "bold"))
        self.selected_audio_title.grid(row=0, column=0, sticky="w", padx=12, pady=(12, 6))

        self.open_audx_btn = ctk.CTkButton(panel, text="", command=self._open_audx, fg_color="#2E6FFF", hover_color="#5A8DFF", height=44, font=ctk.CTkFont("Arial", 15, "bold"))
        self.open_audx_btn.grid(row=1, column=0, sticky="w", padx=12, pady=(0, 8))

        self.pass_panel = ctk.CTkFrame(panel, fg_color="#101C35", corner_radius=12)
        self.pass_panel.grid(row=2, column=0, sticky="w", padx=12, pady=(0, 8))
        self.pass_panel.grid_remove()

        self.playback_key_label = ctk.CTkLabel(self.pass_panel, text="", text_color="#D7E4FF")
        self.playback_key_label.grid(row=0, column=0, sticky="w", padx=10, pady=(8, 2))

        self.playback_pass = ctk.CTkEntry(self.pass_panel, show="*", width=280)
        self.playback_pass.grid(row=1, column=0, sticky="w", padx=10, pady=(0, 8))

        self.load_audio_btn = ctk.CTkButton(self.pass_panel, text="", command=self._load_audio, fg_color="#2E6FFF", hover_color="#5A8DFF", height=40, font=ctk.CTkFont("Arial", 14, "bold"))
        self.load_audio_btn.grid(row=2, column=0, sticky="w", padx=10, pady=(0, 10))

        selected_card = ctk.CTkFrame(panel, fg_color="#101C35", corner_radius=12)
        selected_card.grid(row=3, column=0, sticky="ew", padx=12, pady=(0, 10))
        self.loaded_audio_title = ctk.CTkLabel(selected_card, text="", text_color="#D7E4FF", font=ctk.CTkFont("Arial", 14, "bold"))
        self.loaded_audio_title.grid(row=0, column=0, sticky="w", padx=10, pady=(8, 4))

        self.selected_audio_label = ctk.CTkLabel(selected_card, text="", text_color="#F6FAFF", justify="left", anchor="w", wraplength=900, font=ctk.CTkFont("Arial", 14))
        self.selected_audio_label.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 10))

        transport = ctk.CTkFrame(panel, fg_color="#101C35", corner_radius=12)
        transport.grid(row=4, column=0, sticky="ew", padx=12, pady=(0, 8))
        transport.grid_columnconfigure((0, 1), weight=1)

        self.play_btn = ctk.CTkButton(transport, text="", command=lambda: self._send_command("toggle"), fg_color="#2E6FFF", hover_color="#5A8DFF", height=42, font=ctk.CTkFont("Arial", 14, "bold"))
        self.play_btn.grid(row=0, column=0, padx=4, pady=8)
        self.stop_btn = ctk.CTkButton(transport, text="", command=lambda: self._send_command("stop"), fg_color="#315CAB", hover_color="#4D75CC", height=42, font=ctk.CTkFont("Arial", 14, "bold"))
        self.stop_btn.grid(row=0, column=1, padx=4, pady=8)

        prog = ctk.CTkFrame(panel, fg_color="#101C35", corner_radius=12)
        prog.grid(row=5, column=0, sticky="ew", padx=12, pady=(0, 8))
        prog.grid_columnconfigure(0, weight=1)

        self.seek_slider = ctk.CTkSlider(prog, from_=0, to=100, command=self._on_seek_drag)
        self.seek_slider.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 4))
        self.elapsed = ctk.CTkLabel(prog, text="00:00", text_color="#D7E4FF")
        self.elapsed.grid(row=1, column=0, sticky="w", padx=10, pady=(0, 8))
        self.total = ctk.CTkLabel(prog, text="00:00", text_color="#D7E4FF")
        self.total.grid(row=1, column=0, sticky="e", padx=10, pady=(0, 8))

        vol = ctk.CTkFrame(panel, fg_color="#101C35", corner_radius=12)
        vol.grid(row=6, column=0, sticky="ew", padx=12, pady=(0, 12))
        self.volume_label = ctk.CTkLabel(vol, text="", text_color="#D7E4FF")
        self.volume_label.pack(anchor="w", padx=10, pady=(8, 2))
        self.volume_slider = ctk.CTkSlider(vol, from_=0, to=100, command=self._on_volume)
        self.volume_slider.set(float(self.state_data.get("volume", 80)))
        self.volume_slider.pack(fill="x", padx=10, pady=(0, 10))

    def _set_output_entry(self, value: str) -> None:
        self.output_entry.configure(state="normal")
        self.output_entry.delete(0, "end")
        self.output_entry.insert(0, value if value else self._t("output_folder"))
        self.output_entry.configure(state="readonly")

    def _apply_language(self) -> None:
        self.root.title(self._t("title"))
        self.language_label.configure(text=self._t("lang"))
        self.mode_segment.configure(values=[self._mode_label("user"), self._mode_label("admin")])
        self.mode_segment.set(self._mode_label(self.current_mode if self.current_mode in {"user", "admin"} else "user"))

        self.admin_btn.configure(text=self._t("enter_admin"))
        self.lock_btn.configure(text=self._t("lock_admin"))
        self.admin_code_label.configure(text=self._t("admin_code"))
        self.unlock_btn.configure(text=self._t("unlock"))

        self.summary_title.configure(text=self._t("summary"))

        self.track_loading_label.configure(text=self._t("switching"))
        if not self.now_playing.cget("text"):
            self.now_playing.configure(text=self._t("no_track"))

        self.mp3_title.configure(text=self._t("mp3_files"))
        self.select_mp3_btn.configure(text=self._t("select_mp3"))
        self.prepare_title.configure(text=self._t("prepare"))
        self.access_key_label.configure(text=self._t("access_key"))
        self.browse_btn.configure(text=self._t("browse"))
        self.prepare_btn.configure(text=self._t("prepare"))

        self.selected_audio_title.configure(text=self._t("selected_audio"))
        self.open_audx_btn.configure(text=self._t("open_audx"))
        self.playback_key_label.configure(text=self._t("playback_key"))
        self.load_audio_btn.configure(text=self._t("load_audio"))
        self.loaded_audio_title.configure(text=self._t("loaded_audio"))
        if not self.selected_audio_label.cget("text"):
            self.selected_audio_label.configure(text=self._t("no_audio_loaded"))
        self.play_btn.configure(text=self._t("play_pause"))
        self.stop_btn.configure(text=self._t("stop"))
        self.volume_label.configure(text=self._t("volume"))

        self._set_output_entry(self.state_data.get("output_folder", ""))
        self._set_mode(self.current_mode)

    def _on_language_change(self, value: str) -> None:
        self.language = "en" if value.upper() == "EN" else "es"
        self._apply_language()
        self._set_status(self._t("ready"))

    def _on_mode_segment(self, value: str) -> None:
        self._set_mode(self._mode_from_label(value))

    def _set_mode(self, mode: str) -> None:
        if mode == "admin" and not self.admin_unlocked:
            self.current_mode = "user"
            self.zone_title.configure(text=self._t("zone_user"))
            self.user_view.tkraise()
            self.mode_summary.configure(text=self._t("summary_user"))
            self.summary_text.configure(text=self._t("summary_user"))
            self.mode_segment.set(self._mode_label("user"))
            self._set_status(self._t("must_unlock"), is_error=True)
            return

        self.current_mode = mode
        if mode == "admin":
            self.zone_title.configure(text=self._t("zone_admin"))
            self.admin_view.tkraise()
            self.mode_summary.configure(text=self._t("summary_admin"))
            self.summary_text.configure(text=self._t("summary_admin"))
            self.mode_segment.set(self._mode_label("admin"))
        else:
            self.zone_title.configure(text=self._t("zone_user"))
            self.user_view.tkraise()
            self.mode_summary.configure(text=self._t("summary_user"))
            self.summary_text.configure(text=self._t("summary_user"))
            self.mode_segment.set(self._mode_label("user"))

    def _toggle_admin_panel(self) -> None:
        if self.admin_unlocked:
            return
        if self.admin_panel.winfo_ismapped():
            self.admin_panel.pack_forget()
        else:
            self.admin_panel.pack(fill="x", padx=18, pady=(0, 8))

    def _unlock_admin(self) -> None:
        code = self.admin_code_entry.get().strip()
        candidate = hashlib.sha256(code.encode("utf-8")).hexdigest()
        if not hmac.compare_digest(candidate, ADMIN_CODE_SHA256):
            self._set_status(self._t("bad_admin_code"), is_error=True)
            return
        self.admin_unlocked = True
        self.admin_panel.pack_forget()
        self.admin_btn.pack_forget()
        self.lock_btn.pack(fill="x", padx=18, pady=(0, 8))
        self._set_mode("admin")
        self._set_status(self._t("admin_unlocked"))

    def _lock_admin(self) -> None:
        self.admin_unlocked = False
        self.selected_mp3_files = []
        self.mp3_list.delete(0, "end")
        self.lock_btn.pack_forget()
        self.admin_btn.pack(fill="x", padx=18, pady=(0, 8))
        self._set_mode("user")
        self._set_status(self._t("admin_locked"))

    def _set_status(self, message: str, is_error: bool = False, loading: bool = False) -> None:
        self.status_label.configure(text=message, text_color=("#FF9FB3" if is_error else "#F6FAFF"))
        if loading:
            self.status_spinner.grid()
            self.status_spinner.start()
        else:
            self.status_spinner.stop()
            self.status_spinner.grid_remove()

    def _set_track_loading(self, loading: bool) -> None:
        if loading:
            self.track_loading_label.grid()
            self.root.update_idletasks()
        else:
            self.track_loading_label.grid_remove()

    def _select_mp3(self) -> None:
        if not self.admin_unlocked:
            self._set_status(self._t("must_unlock"), is_error=True)
            return
        files = filedialog.askopenfilenames(title=self._t("dialog_select_mp3"), filetypes=[("MP3 files", "*.mp3")])
        if not files:
            return
        self.selected_mp3_files = list(files)
        self.mp3_list.delete(0, "end")
        for item in self.selected_mp3_files:
            self.mp3_list.insert("end", item)
        self._set_status(self._t("mp3_selected", count=len(self.selected_mp3_files)))

    def _choose_output(self) -> None:
        if not self.admin_unlocked:
            self._set_status(self._t("must_unlock"), is_error=True)
            return
        directory = filedialog.askdirectory(title=self._t("dialog_output"))
        if not directory:
            return
        self._set_output_entry(directory)

    def _encrypt_selected(self) -> None:
        if not self.selected_mp3_files:
            self._set_status(self._t("no_mp3"), is_error=True)
            return

        output_dir = self.output_entry.get().strip()
        password = self.encrypt_pass.get()
        if not output_dir or output_dir == self._t("output_folder"):
            self._set_status(self._t("need_output"), is_error=True)
            return

        def work() -> list[str]:
            out: list[str] = []
            for path in self.selected_mp3_files:
                out.append(str(self.crypto.encrypt_file(path, password=password, output_dir=output_dir)))
            return out

        self._run_background(work, self._t("processing"), lambda created: self._set_status(self._t("processed", count=len(created))))

    def _open_audx(self) -> None:
        selected = filedialog.askopenfilename(title=self._t("dialog_open_audx"), filetypes=[("AUDX files", "*.audx")])
        if not selected:
            return
        self.pending_audx_file = selected
        self.pass_panel.grid()
        self.playback_pass.focus_set()
        self._set_status(self._t("audx_selected"))

    def _load_audio(self) -> None:
        if not self.pending_audx_file:
            self._set_status(self._t("need_audx"), is_error=True)
            return
        password = self.playback_pass.get().strip()
        if not password:
            self._set_status(self._t("need_key"), is_error=True)
            return
        if self.player is None:
            self._set_status(self.player_init_error or self._t("engine_error", error=""), is_error=True)
            return

        def work() -> tuple[list[PlaylistEntry], PlayerState]:
            entries = self.player.load_playlist([self.pending_audx_file], password)
            return entries, self.player.snapshot()

        def on_success(result: tuple[list[PlaylistEntry], PlayerState]) -> None:
            entries, state = result
            self.playlist = entries
            if entries:
                entry = entries[0]
                label = entry.title or "Audio"
                if entry.artist:
                    label = f"{label} - {entry.artist}"
                self.selected_audio_label.configure(text=label)
            else:
                self.selected_audio_label.configure(text=self._t("no_audio_loaded"))
            self._apply_state(state)
            self.playback_pass.delete(0, "end")
            self.pass_panel.grid_remove()
            if entries:
                self._send_command("play", 0)
            self._set_status(self._t("audio_loaded"))

        self._run_background(work, self._t("loading_audio"), on_success)

    def _send_command(self, command: str, value: Any = None) -> None:
        if self.player is None:
            self._set_status(self.player_init_error or self._t("engine_error", error=""), is_error=True)
            return

        track_change = command in {"play"}
        if track_change:
            self._set_track_loading(True)

        try:
            if command == "play":
                state = self.player.play_index(int(value))
            elif command == "toggle":
                state = self.player.toggle_play_pause()
            elif command == "stop":
                state = self.player.stop()
            elif command == "seek":
                state = self.player.seek(float(value))
            elif command == "volume":
                state = self.player.set_volume(int(float(value)))
            else:
                return
            self._apply_state(state)
        except (ValueError, SecureAudioError, IndexError) as exc:
            self._set_status(str(exc), is_error=True)
        finally:
            if track_change:
                self._set_track_loading(False)

    def _run_background(self, work: Callable[[], Any], loading_message: str, on_success: Callable[[Any], None]) -> None:
        self._set_status(loading_message, loading=True)
        self._set_controls_enabled(False)

        def runner() -> None:
            result: Any = None
            error: Exception | None = None
            try:
                result = work()
            except Exception as exc:
                error = exc

            def finish() -> None:
                self._set_controls_enabled(True)
                if error is not None:
                    self._handle_error(error)
                    return
                on_success(result)

            self.root.after(0, finish)

        threading.Thread(target=runner, daemon=True).start()

    def _set_controls_enabled(self, enabled: bool) -> None:
        state = "normal" if enabled else "disabled"
        for widget in [self.play_btn, self.stop_btn]:
            widget.configure(state=state)

    def _handle_error(self, error: Exception) -> None:
        if isinstance(error, (AuthenticationError, InvalidContainerError, SecureAudioError, OSError)):
            self._set_status(str(error), is_error=True)
            return
        self._set_status(self._t("generic_error", error=error), is_error=True)

    def _apply_state(self, state: PlayerState) -> None:
        self.current_state = state

        self.seek_slider.configure(to=max(state.duration_seconds, 1.0))
        self.seek_slider.set(max(0.0, state.position_seconds))
        self.elapsed.configure(text=self._fmt(state.position_seconds))
        self.total.configure(text=self._fmt(state.duration_seconds))

        self._suspend_volume_event = True
        self.volume_slider.set(state.volume)
        self._suspend_volume_event = False

        self.now_playing.configure(text=state.now_playing or self._t("no_track"))

    def _poll_state(self) -> None:
        if self.player is not None:
            try:
                self._apply_state(self.player.snapshot())
            except Exception:
                pass
        self.root.after(750, self._poll_state)

    def _on_seek_drag(self, value: float) -> None:
        if self.current_state is None:
            return
        self._send_command("seek", value)

    def _on_volume(self, value: float) -> None:
        if self._suspend_volume_event:
            return
        self._send_command("volume", value)

    def _bind_shortcuts(self) -> None:
        self.root.bind("<space>", lambda _e: self._send_command("toggle"))

    @staticmethod
    def _fmt(seconds: float) -> str:
        total = max(0, int(seconds))
        return f"{str(total // 60).zfill(2)}:{str(total % 60).zfill(2)}"


def run() -> None:
    root = ctk.CTk()
    app = CustomTkSecureAudioApp(root)
    try:
        root.mainloop()
    except KeyboardInterrupt:
        pass
    except Exception as exc:
        detail = f"Error en modo customtkinter: {exc}\n\n{traceback.format_exc()}"
        raise SystemExit(detail) from exc
