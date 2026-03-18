from __future__ import annotations

import hashlib
import hmac
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import Any, Callable

from .crypto import AuthenticationError, AudxCrypto, InvalidContainerError, SecureAudioError
from .player import PlaylistEntry, PlayerState, SecureVlcPlayer

ADMIN_CODE_SHA256 = "c9bc710759f356523ecc7669b32e94c88b2c6e55496dc75fa23247156e72ca09"

TRANSLATIONS: dict[str, dict[str, str]] = {
    "es": {
        "app_title": "Reproductor Seguro de Audio (Tkinter)",
        "language": "Idioma",
        "mode": "Modo",
        "mode_user": "Usuario",
        "mode_admin": "Administrador",
        "enter_admin": "Ingresar al admin",
        "lock_admin": "Bloquear admin",
        "admin_code": "Codigo admin",
        "unlock": "Desbloquear",
        "summary_label": "Resumen",
        "summary_locked": "Solo el modo usuario esta disponible hasta desbloquear admin.",
        "summary_user": "Esta zona permite cargar y reproducir un audio AUDX.",
        "summary_admin": "Esta zona prepara la biblioteca segura desde MP3.",
        "admin_zone": "Zona de administrador",
        "user_zone": "Zona de usuario",
        "select_mp3": "Seleccionar MP3",
        "selected_mp3": "MP3 seleccionados",
        "access_pass": "Clave de acceso",
        "output_folder": "Carpeta de salida",
        "browse": "Examinar",
        "prepare_library": "Preparar biblioteca",
        "open_audx": "Abrir audio AUDX",
        "playback_pass": "Clave de reproduccion",
        "load_audio": "Cargar audio",
        "playlist": "Audio seleccionado",
        "prev": "Anterior",
        "play_pause": "Play/Pausa",
        "stop": "Detener",
        "next": "Siguiente",
        "volume": "Volumen",
        "status_ready": "Listo.",
        "status_need_admin": "Debes desbloquear la zona de administrador con el codigo.",
        "status_admin_unlocked": "Admin desbloqueado.",
        "status_admin_locked": "Admin bloqueado.",
        "status_selected_mp3": "MP3 seleccionados: {count}.",
        "status_encrypted": "Archivos procesados: {count}.",
        "status_need_playback_pass": "Ingresa primero la clave de reproduccion.",
        "status_audx_selected": "Archivo AUDX seleccionado. Ingresa clave y pulsa Cargar audio.",
        "status_audio_loaded": "Audio cargado.",
        "status_loading": "Cargando audio...",
        "status_encrypting": "Procesando biblioteca...",
        "status_error_prefix": "Error",
        "error_admin_code": "Codigo de administrador incorrecto.",
        "error_no_mp3": "No MP3 files selected.",
        "error_output_required": "An output directory is required.",
        "error_no_audx": "Primero debes seleccionar un archivo AUDX.",
        "no_track": "Sin pista seleccionada",
        "shortcuts": "Atajos: Espacio play/pausa, Izq/Der seek 5s, Arriba/Abajo volumen, N siguiente, P anterior.",
        "audio_engine_error": "Motor de audio no disponible (VLC/libvlc).",
    },
    "en": {
        "app_title": "Secure Audio Player (Tkinter)",
        "language": "Language",
        "mode": "Mode",
        "mode_user": "User",
        "mode_admin": "Administrator",
        "enter_admin": "Enter admin",
        "lock_admin": "Lock admin",
        "admin_code": "Admin code",
        "unlock": "Unlock",
        "summary_label": "Summary",
        "summary_locked": "Only user mode is available until admin is unlocked.",
        "summary_user": "This area loads and plays one AUDX audio file.",
        "summary_admin": "This area prepares the secure library from MP3 files.",
        "admin_zone": "Administrator zone",
        "user_zone": "User zone",
        "select_mp3": "Select MP3",
        "selected_mp3": "Selected MP3",
        "access_pass": "Access passphrase",
        "output_folder": "Output folder",
        "browse": "Browse",
        "prepare_library": "Prepare library",
        "open_audx": "Open AUDX audio",
        "playback_pass": "Playback passphrase",
        "load_audio": "Load audio",
        "playlist": "Selected audio",
        "prev": "Previous",
        "play_pause": "Play/Pause",
        "stop": "Stop",
        "next": "Next",
        "volume": "Volume",
        "status_ready": "Ready.",
        "status_need_admin": "You must unlock admin mode with the code.",
        "status_admin_unlocked": "Admin unlocked.",
        "status_admin_locked": "Admin locked.",
        "status_selected_mp3": "Selected MP3 files: {count}.",
        "status_encrypted": "Processed files: {count}.",
        "status_need_playback_pass": "Enter playback passphrase first.",
        "status_audx_selected": "AUDX file selected. Enter passphrase and press Load audio.",
        "status_audio_loaded": "Audio loaded.",
        "status_loading": "Loading audio...",
        "status_encrypting": "Processing library...",
        "status_error_prefix": "Error",
        "error_admin_code": "Incorrect administrator code.",
        "error_no_mp3": "No MP3 files selected.",
        "error_output_required": "An output directory is required.",
        "error_no_audx": "You must select one AUDX file first.",
        "no_track": "No track selected",
        "shortcuts": "Shortcuts: Space play/pause, Left/Right seek 5s, Up/Down volume, N next, P previous.",
        "audio_engine_error": "Audio engine unavailable (VLC/libvlc).",
    },
}


class TkSecureAudioApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.geometry("1280x860")
        self.root.minsize(1080, 720)

        self.language = "es"
        self.admin_unlocked = False
        self.current_mode = "user"
        self.selected_mp3_files: list[str] = []
        self.pending_audx_file: str = ""
        self.playlist: list[PlaylistEntry] = []
        self.current_state: PlayerState | None = None
        self._suspend_volume_event = False

        self.crypto = AudxCrypto()
        self.player: SecureVlcPlayer | None = None
        self.player_init_error: str = ""
        try:
            self.player = SecureVlcPlayer(self.crypto)
        except Exception as exc:
            self.player_init_error = f"{self.t('audio_engine_error')} {exc}"

        self._build_styles()
        self._build_layout()
        self._bind_shortcuts()
        self._refresh_texts()
        self._set_mode("user")
        if self.player_init_error:
            self._set_status(self.player_init_error, is_error=True)
        else:
            self._set_status(self.t("status_ready"))
        self._poll_state()

    def t(self, key: str, **vars: Any) -> str:
        text = TRANSLATIONS.get(self.language, TRANSLATIONS["es"]).get(key, key)
        for name, value in vars.items():
            text = text.replace(f"{{{name}}}", str(value))
        return text

    def _build_styles(self) -> None:
        self.root.configure(bg="#0D1117")
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("App.TFrame", background="#0D1117")
        style.configure("Side.TFrame", background="#111827")
        style.configure("Card.TFrame", background="#151E2E")
        style.configure("CardAlt.TFrame", background="#1B2537")
        style.configure("Header.TLabel", background="#0D1117", foreground="#F8FAFC", font=("Segoe UI", 20, "bold"))
        style.configure("Title.TLabel", background="#151E2E", foreground="#E2E8F0", font=("Segoe UI", 13, "bold"))
        style.configure("Text.TLabel", background="#151E2E", foreground="#CBD5E1", font=("Segoe UI", 10))
        style.configure("Muted.TLabel", background="#151E2E", foreground="#94A3B8", font=("Segoe UI", 9))
        style.configure("Status.TLabel", background="#0F172A", foreground="#E2E8F0", font=("Segoe UI", 10, "bold"))
        style.configure("Accent.TButton", font=("Segoe UI", 10, "bold"))
        style.map(
            "Accent.TButton",
            background=[("active", "#1D4ED8"), ("!disabled", "#2563EB"), ("disabled", "#334155")],
            foreground=[("!disabled", "#FFFFFF"), ("disabled", "#94A3B8")],
        )
        style.map(
            "TButton",
            background=[("active", "#1E293B"), ("!disabled", "#0F172A"), ("disabled", "#1E293B")],
            foreground=[("!disabled", "#E2E8F0"), ("disabled", "#64748B")],
        )
        style.configure(
            "TEntry",
            fieldbackground="#0B1220",
            foreground="#E2E8F0",
            insertcolor="#E2E8F0",
            bordercolor="#334155",
            lightcolor="#334155",
            darkcolor="#334155",
        )
        style.configure("TProgressbar", troughcolor="#0B1220", background="#22C55E")

    def _build_layout(self) -> None:
        container = ttk.Frame(self.root, style="App.TFrame", padding=12)
        container.pack(fill="both", expand=True)
        container.columnconfigure(1, weight=1)
        container.rowconfigure(0, weight=1)

        self.sidebar = ttk.Frame(container, style="Side.TFrame", padding=14)
        self.sidebar.grid(row=0, column=0, sticky="nsw")
        self.main = ttk.Frame(container, style="App.TFrame")
        self.main.grid(row=0, column=1, sticky="nsew", padx=(12, 0))
        self.main.columnconfigure(0, weight=1)
        self.main.rowconfigure(1, weight=1)

        self._build_sidebar()
        self._build_main()

    def _build_sidebar(self) -> None:
        ttk.Label(self.sidebar, text="Audio Studio", style="Header.TLabel").pack(anchor="w", pady=(0, 8))

        lang_card = ttk.Frame(self.sidebar, style="Card.TFrame", padding=10)
        lang_card.pack(fill="x", pady=6)
        self.lang_title = ttk.Label(lang_card, style="Title.TLabel")
        self.lang_title.pack(anchor="w")
        lang_row = ttk.Frame(lang_card, style="Card.TFrame")
        lang_row.pack(fill="x", pady=(8, 0))
        self.lang_es_btn = ttk.Button(lang_row, text="ES", style="Accent.TButton", command=lambda: self._set_language("es"))
        self.lang_en_btn = ttk.Button(lang_row, text="EN", command=lambda: self._set_language("en"))
        self.lang_es_btn.pack(side="left", padx=(0, 8))
        self.lang_en_btn.pack(side="left")
        mode_card = ttk.Frame(self.sidebar, style="Card.TFrame", padding=10)
        mode_card.pack(fill="x", pady=6)
        self.mode_title = ttk.Label(mode_card, style="Title.TLabel")
        self.mode_title.pack(anchor="w")
        mode_row = ttk.Frame(mode_card, style="Card.TFrame")
        mode_row.pack(fill="x", pady=(8, 0))
        self.user_mode_btn = ttk.Button(mode_row, command=lambda: self._set_mode("user"))
        self.user_mode_btn.pack(side="left", padx=(0, 8))
        self.admin_mode_btn = ttk.Button(mode_row, command=lambda: self._set_mode("admin"))
        self.admin_mode_btn.pack(side="left")
        self.enter_admin_btn = ttk.Button(mode_card, style="Accent.TButton", command=self._toggle_admin_unlock_panel)
        self.enter_admin_btn.pack(fill="x", pady=(8, 6))
        self.lock_admin_btn = ttk.Button(mode_card, command=self._lock_admin)
        self.lock_admin_btn.pack(fill="x")
        self.mode_summary = ttk.Label(mode_card, style="Muted.TLabel", wraplength=250, justify="left")
        self.mode_summary.pack(fill="x", pady=(10, 0))

        self.admin_unlock_card = ttk.Frame(self.sidebar, style="CardAlt.TFrame", padding=10)
        self.admin_unlock_title = ttk.Label(self.admin_unlock_card, style="Title.TLabel")
        self.admin_unlock_title.pack(anchor="w")
        self.admin_code_entry = ttk.Entry(self.admin_unlock_card, show="*")
        self.admin_code_entry.pack(fill="x", pady=(8, 6))
        self.unlock_btn = ttk.Button(self.admin_unlock_card, style="Accent.TButton", command=self._unlock_admin)
        self.unlock_btn.pack(fill="x")
        self.admin_unlock_card.pack(fill="x", pady=6)
        self.admin_unlock_card.pack_forget()

        summary_card = ttk.Frame(self.sidebar, style="Card.TFrame", padding=10)
        summary_card.pack(fill="x", pady=6)
        self.summary_title = ttk.Label(summary_card, style="Title.TLabel")
        self.summary_title.pack(anchor="w")
        self.summary_text = ttk.Label(summary_card, style="Muted.TLabel", wraplength=250, justify="left")
        self.summary_text.pack(fill="x", pady=(8, 0))

    def _build_main(self) -> None:
        top = ttk.Frame(self.main, style="App.TFrame")
        top.grid(row=0, column=0, sticky="ew")
        top.columnconfigure(0, weight=1)
        self.zone_title = ttk.Label(top, style="Header.TLabel")
        self.zone_title.grid(row=0, column=0, sticky="w", pady=(0, 8))
        self.now_playing_label = ttk.Label(top, style="Muted.TLabel")
        self.now_playing_label.grid(row=1, column=0, sticky="w", pady=(0, 6))

        stack = ttk.Frame(self.main, style="App.TFrame")
        stack.grid(row=1, column=0, sticky="nsew")
        stack.columnconfigure(0, weight=1)
        stack.rowconfigure(0, weight=1)
        self.admin_view = ttk.Frame(stack, style="App.TFrame")
        self.user_view = ttk.Frame(stack, style="App.TFrame")
        self.admin_view.grid(row=0, column=0, sticky="nsew")
        self.user_view.grid(row=0, column=0, sticky="nsew")

        self._build_admin_view()
        self._build_user_view()

        status = ttk.Frame(self.main, style="Card.TFrame", padding=(12, 8))
        status.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        status.columnconfigure(1, weight=1)
        self.status_loader = ttk.Progressbar(status, mode="indeterminate", length=120)
        self.status_loader.grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.status_loader.grid_remove()
        self.status_text = ttk.Label(status, style="Status.TLabel")
        self.status_text.grid(row=0, column=1, sticky="w")

    def _build_admin_view(self) -> None:
        card = ttk.Frame(self.admin_view, style="Card.TFrame", padding=12)
        card.pack(fill="both", expand=True)
        card.columnconfigure(0, weight=1)
        card.columnconfigure(1, weight=1)
        card.rowconfigure(1, weight=1)

        left = ttk.Frame(card, style="Card.TFrame")
        left.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=(0, 8))
        left.columnconfigure(0, weight=1)
        self.selected_mp3_label = ttk.Label(left, style="Title.TLabel")
        self.selected_mp3_label.pack(anchor="w")
        self.select_mp3_btn = ttk.Button(left, style="Accent.TButton", command=self._select_mp3_files)
        self.select_mp3_btn.pack(anchor="w", pady=(8, 8))
        self.mp3_listbox = tk.Listbox(
            left,
            bg="#0B1220",
            fg="#E2E8F0",
            selectbackground="#1D4ED8",
            relief="flat",
            font=("Segoe UI", 10),
            height=20,
        )
        self.mp3_listbox.pack(fill="both", expand=True)

        right = ttk.Frame(card, style="Card.TFrame")
        right.grid(row=0, column=1, sticky="new")
        right.columnconfigure(0, weight=1)
        self.output_card_title = ttk.Label(right, style="Title.TLabel")
        self.output_card_title.grid(row=0, column=0, sticky="w")
        self.encrypt_pass_label = ttk.Label(right, style="Text.TLabel")
        self.encrypt_pass_label.grid(row=1, column=0, sticky="w", pady=(10, 4))
        self.encrypt_pass_entry = ttk.Entry(right, show="*")
        self.encrypt_pass_entry.grid(row=2, column=0, sticky="ew")
        self.output_label = ttk.Label(right, style="Text.TLabel")
        self.output_label.grid(row=3, column=0, sticky="w", pady=(10, 4))
        out_row = ttk.Frame(right, style="Card.TFrame")
        out_row.grid(row=4, column=0, sticky="ew")
        out_row.columnconfigure(0, weight=1)
        self.output_dir_entry = ttk.Entry(out_row)
        self.output_dir_entry.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self.output_dir_entry.configure(state="readonly")
        self.choose_output_btn = ttk.Button(out_row, command=self._choose_output_dir)
        self.choose_output_btn.grid(row=0, column=1)
        self.encrypt_btn = ttk.Button(right, style="Accent.TButton", command=self._encrypt_selected_files)
        self.encrypt_btn.grid(row=5, column=0, sticky="ew", pady=(12, 0))

    def _build_user_view(self) -> None:
        card = ttk.Frame(self.user_view, style="Card.TFrame", padding=12)
        card.pack(fill="both", expand=True)
        card.columnconfigure(0, weight=1)
        card.columnconfigure(1, weight=1)
        card.rowconfigure(1, weight=1)

        left = ttk.Frame(card, style="Card.TFrame")
        left.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=(0, 8))
        left.columnconfigure(0, weight=1)
        left.rowconfigure(3, weight=1)
        self.playlist_title = ttk.Label(left, style="Title.TLabel")
        self.playlist_title.grid(row=0, column=0, sticky="w")
        self.open_audx_btn = ttk.Button(left, style="Accent.TButton", command=self._open_audx_file)
        self.open_audx_btn.grid(row=1, column=0, sticky="w", pady=(8, 8))

        self.playback_pass_frame = ttk.Frame(left, style="CardAlt.TFrame", padding=8)
        self.playback_pass_label = ttk.Label(self.playback_pass_frame, style="Text.TLabel")
        self.playback_pass_label.grid(row=0, column=0, sticky="w")
        self.playback_pass_entry = ttk.Entry(self.playback_pass_frame, show="*")
        self.playback_pass_entry.grid(row=1, column=0, sticky="ew", pady=(4, 6))
        self.load_audio_btn = ttk.Button(self.playback_pass_frame, style="Accent.TButton", command=self._load_selected_audio)
        self.load_audio_btn.grid(row=2, column=0, sticky="ew")
        self.playback_pass_frame.columnconfigure(0, weight=1)
        self.playback_pass_frame.grid(row=2, column=0, sticky="ew", pady=(0, 8))
        self.playback_pass_frame.grid_remove()

        self.playlist_listbox = tk.Listbox(
            left,
            bg="#0B1220",
            fg="#E2E8F0",
            selectbackground="#1D4ED8",
            relief="flat",
            font=("Segoe UI", 10),
            height=18,
        )
        self.playlist_listbox.grid(row=3, column=0, sticky="nsew")
        self.playlist_listbox.bind("<<ListboxSelect>>", self._on_playlist_select)
        right = ttk.Frame(card, style="Card.TFrame")
        right.grid(row=0, column=1, rowspan=2, sticky="nsew")
        right.columnconfigure(0, weight=1)

        controls = ttk.Frame(right, style="CardAlt.TFrame", padding=10)
        controls.grid(row=0, column=0, sticky="ew")
        self.prev_btn = ttk.Button(controls, command=lambda: self._send_playback_command("previous"))
        self.prev_btn.grid(row=0, column=0, padx=4)
        self.play_btn = ttk.Button(controls, style="Accent.TButton", command=lambda: self._send_playback_command("toggle"))
        self.play_btn.grid(row=0, column=1, padx=4)
        self.stop_btn = ttk.Button(controls, command=lambda: self._send_playback_command("stop"))
        self.stop_btn.grid(row=0, column=2, padx=4)
        self.next_btn = ttk.Button(controls, command=lambda: self._send_playback_command("next"))
        self.next_btn.grid(row=0, column=3, padx=4)

        progress = ttk.Frame(right, style="CardAlt.TFrame", padding=10)
        progress.grid(row=1, column=0, sticky="ew", pady=(8, 0))
        progress.columnconfigure(0, weight=1)
        self.seek_scale = ttk.Scale(progress, from_=0, to=100, orient="horizontal")
        self.seek_scale.grid(row=0, column=0, sticky="ew")
        self.seek_scale.bind("<ButtonRelease-1>", self._on_seek_release)
        time_row = ttk.Frame(progress, style="CardAlt.TFrame")
        time_row.grid(row=1, column=0, sticky="ew", pady=(4, 0))
        self.elapsed_label = ttk.Label(time_row, text="00:00", style="Muted.TLabel")
        self.elapsed_label.pack(side="left")
        self.total_label = ttk.Label(time_row, text="00:00", style="Muted.TLabel")
        self.total_label.pack(side="right")

        vol = ttk.Frame(right, style="CardAlt.TFrame", padding=10)
        vol.grid(row=2, column=0, sticky="ew", pady=(8, 0))
        self.volume_label = ttk.Label(vol, style="Text.TLabel")
        self.volume_label.pack(anchor="w")
        self.volume_scale = ttk.Scale(vol, from_=0, to=100, orient="horizontal", command=self._on_volume_change)
        self.volume_scale.set(80)
        self.volume_scale.pack(fill="x", pady=(4, 0))

        self.shortcuts_label = ttk.Label(right, style="Muted.TLabel", wraplength=430, justify="left")
        self.shortcuts_label.grid(row=3, column=0, sticky="w", pady=(10, 0))

    def _bind_shortcuts(self) -> None:
        self.root.bind("<space>", lambda _: self._on_space())
        self.root.bind("<Left>", lambda _: self._on_left())
        self.root.bind("<Right>", lambda _: self._on_right())
        self.root.bind("<Up>", lambda _: self._on_up())
        self.root.bind("<Down>", lambda _: self._on_down())
        self.root.bind("<Key-n>", lambda _: self._send_playback_command("next"))
        self.root.bind("<Key-N>", lambda _: self._send_playback_command("next"))
        self.root.bind("<Key-p>", lambda _: self._send_playback_command("previous"))
        self.root.bind("<Key-P>", lambda _: self._send_playback_command("previous"))

    def _entry_is_focused(self) -> bool:
        focused = self.root.focus_get()
        return isinstance(focused, tk.Entry) or isinstance(focused, ttk.Entry)

    def _on_space(self) -> None:
        if self._entry_is_focused():
            return
        self._send_playback_command("toggle")

    def _on_left(self) -> None:
        if self._entry_is_focused():
            return
        self._seek_delta(-5)

    def _on_right(self) -> None:
        if self._entry_is_focused():
            return
        self._seek_delta(5)

    def _on_up(self) -> None:
        if self._entry_is_focused():
            return
        self._volume_delta(5)

    def _on_down(self) -> None:
        if self._entry_is_focused():
            return
        self._volume_delta(-5)

    def _set_language(self, language: str) -> None:
        self.language = "en" if language == "en" else "es"
        self._refresh_texts()

    def _refresh_texts(self) -> None:
        self.root.title(self.t("app_title"))
        self.lang_title.configure(text=self.t("language"))
        self.mode_title.configure(text=self.t("mode"))
        self.user_mode_btn.configure(text=self.t("mode_user"))
        self.admin_mode_btn.configure(text=self.t("mode_admin"))
        self.enter_admin_btn.configure(text=self.t("enter_admin"))
        self.lock_admin_btn.configure(text=self.t("lock_admin"))
        self.admin_unlock_title.configure(text=self.t("admin_code"))
        self.unlock_btn.configure(text=self.t("unlock"))
        self.summary_title.configure(text=self.t("summary_label"))
        self.selected_mp3_label.configure(text=self.t("selected_mp3"))
        self.select_mp3_btn.configure(text=self.t("select_mp3"))
        self.output_card_title.configure(text=self.t("prepare_library"))
        self.encrypt_pass_label.configure(text=self.t("access_pass"))
        self.output_label.configure(text=self.t("output_folder"))
        self.choose_output_btn.configure(text=self.t("browse"))
        self.encrypt_btn.configure(text=self.t("prepare_library"))
        self.playlist_title.configure(text=self.t("playlist"))
        self.open_audx_btn.configure(text=self.t("open_audx"))
        self.playback_pass_label.configure(text=self.t("playback_pass"))
        self.load_audio_btn.configure(text=self.t("load_audio"))
        self.prev_btn.configure(text=self.t("prev"))
        self.play_btn.configure(text=self.t("play_pause"))
        self.stop_btn.configure(text=self.t("stop"))
        self.next_btn.configure(text=self.t("next"))
        self.volume_label.configure(text=self.t("volume"))
        self.shortcuts_label.configure(text=self.t("shortcuts"))
        self._refresh_summary()

    def _refresh_summary(self) -> None:
        self.admin_mode_btn.configure(state=("normal" if self.admin_unlocked else "disabled"))
        if self.admin_unlocked:
            self.enter_admin_btn.pack_forget()
            self.lock_admin_btn.pack(fill="x")
        else:
            self.lock_admin_btn.pack_forget()
            self.enter_admin_btn.pack(fill="x", pady=(8, 6))
        if not self.admin_unlocked:
            self.mode_summary.configure(text=self.t("summary_locked"))
            self.summary_text.configure(text=self.t("summary_user"))
        elif self.current_mode == "admin":
            self.mode_summary.configure(text=self.t("summary_admin"))
            self.summary_text.configure(text=self.t("summary_admin"))
        else:
            self.mode_summary.configure(text=self.t("summary_user"))
            self.summary_text.configure(text=self.t("summary_user"))

    def _toggle_admin_unlock_panel(self) -> None:
        if self.admin_unlocked:
            return
        if self.admin_unlock_card.winfo_ismapped():
            self.admin_unlock_card.pack_forget()
            return
        self.admin_unlock_card.pack(fill="x", pady=6)
        self.admin_code_entry.focus_set()

    def _unlock_admin(self) -> None:
        admin_code = self.admin_code_entry.get().strip()
        candidate = hashlib.sha256(admin_code.encode("utf-8")).hexdigest()
        if not hmac.compare_digest(candidate, ADMIN_CODE_SHA256):
            self._set_status(self.t("error_admin_code"), is_error=True)
            return
        self.admin_unlocked = True
        self.admin_code_entry.delete(0, "end")
        self.admin_unlock_card.pack_forget()
        self._refresh_summary()
        self._set_mode("admin")
        self._set_status(self.t("status_admin_unlocked"))
    def _lock_admin(self) -> None:
        self.admin_unlocked = False
        self.selected_mp3_files = []
        self.mp3_listbox.delete(0, "end")
        self._set_mode("user")
        self._refresh_summary()
        self._set_status(self.t("status_admin_locked"))

    def _set_mode(self, mode: str) -> None:
        if mode == "admin" and not self.admin_unlocked:
            self._set_status(self.t("status_need_admin"), is_error=True)
            return
        self.current_mode = mode
        if mode == "admin":
            self.zone_title.configure(text=self.t("admin_zone"))
            self.admin_view.tkraise()
        else:
            self.zone_title.configure(text=self.t("user_zone"))
            self.user_view.tkraise()
        self._refresh_summary()

    def _set_status(self, message: str, is_error: bool = False, loading: bool = False) -> None:
        color = "#FDA4AF" if is_error else "#E2E8F0"
        self.status_text.configure(text=message, foreground=color)
        if loading:
            self.status_loader.grid()
            self.status_loader.start(12)
        else:
            self.status_loader.stop()
            self.status_loader.grid_remove()

    def _select_mp3_files(self) -> None:
        if not self.admin_unlocked:
            self._set_status(self.t("status_need_admin"), is_error=True)
            return
        selected = filedialog.askopenfilenames(
            title=self.t("select_mp3"),
            filetypes=[("MP3 files", "*.mp3")],
        )
        if not selected:
            return
        self.selected_mp3_files = list(selected)
        self.mp3_listbox.delete(0, "end")
        for file_path in self.selected_mp3_files:
            self.mp3_listbox.insert("end", file_path)
        self._set_status(self.t("status_selected_mp3", count=len(self.selected_mp3_files)))

    def _choose_output_dir(self) -> None:
        if not self.admin_unlocked:
            self._set_status(self.t("status_need_admin"), is_error=True)
            return
        directory = filedialog.askdirectory(title=self.t("output_folder"))
        if not directory:
            return
        self.output_dir_entry.configure(state="normal")
        self.output_dir_entry.delete(0, "end")
        self.output_dir_entry.insert(0, directory)
        self.output_dir_entry.configure(state="readonly")

    def _encrypt_selected_files(self) -> None:
        if not self.admin_unlocked:
            self._set_status(self.t("status_need_admin"), is_error=True)
            return
        if not self.selected_mp3_files:
            self._set_status(self.t("error_no_mp3"), is_error=True)
            return
        password = self.encrypt_pass_entry.get()
        output_dir = self.output_dir_entry.get().strip()
        if not output_dir:
            self._set_status(self.t("error_output_required"), is_error=True)
            return

        def work() -> list[str]:
            created: list[str] = []
            for file_path in self.selected_mp3_files:
                target = self.crypto.encrypt_file(file_path, password=password, output_dir=output_dir)
                created.append(str(target))
            return created

        self._run_background(
            work=work,
            loading_message=self.t("status_encrypting"),
            on_success=lambda created: self._set_status(self.t("status_encrypted", count=len(created))),
        )

    def _open_audx_file(self) -> None:
        selected = filedialog.askopenfilename(
            title=self.t("open_audx"),
            filetypes=[("AUDX files", "*.audx")],
        )
        if not selected:
            return
        self.pending_audx_file = selected
        self.playback_pass_frame.grid()
        self.playback_pass_entry.focus_set()
        self._set_status(self.t("status_audx_selected"))

    def _load_selected_audio(self) -> None:
        if not self.pending_audx_file:
            self._set_status(self.t("error_no_audx"), is_error=True)
            return
        password = self.playback_pass_entry.get().strip()
        if not password:
            self._set_status(self.t("status_need_playback_pass"), is_error=True)
            return
        if self.player is None:
            self._set_status(self.player_init_error or self.t("audio_engine_error"), is_error=True)
            return

        def work() -> tuple[list[PlaylistEntry], PlayerState]:
            entries = self.player.load_playlist([self.pending_audx_file], password)
            return entries, self.player.snapshot()

        def on_success(result: tuple[list[PlaylistEntry], PlayerState]) -> None:
            entries, snapshot = result
            self.playlist = entries
            self._render_playlist()
            self._apply_player_state(snapshot)
            self._set_status(self.t("status_audio_loaded"))

        self._run_background(work=work, loading_message=self.t("status_loading"), on_success=on_success)

    def _send_playback_command(self, command: str, value: Any = None) -> None:
        if self.player is None:
            self._set_status(self.player_init_error or self.t("audio_engine_error"), is_error=True)
            return
        try:
            if command == "play":
                state = self.player.play_index(int(value))
            elif command == "toggle":
                state = self.player.toggle_play_pause()
            elif command == "pause":
                state = self.player.pause()
            elif command == "stop":
                state = self.player.stop()
            elif command == "next":
                state = self.player.next_track()
            elif command == "previous":
                state = self.player.previous_track()
            elif command == "seek":
                state = self.player.seek(float(value))
            elif command == "volume":
                state = self.player.set_volume(int(float(value)))
            else:
                return
            self._apply_player_state(state)
        except (ValueError, SecureAudioError, IndexError) as exc:
            self._set_status(str(exc), is_error=True)

    def _run_background(
        self,
        work: Callable[[], Any],
        loading_message: str,
        on_success: Callable[[Any], None],
    ) -> None:
        self._set_status(loading_message, loading=True)
        self._set_actions_enabled(False)

        def runner() -> None:
            result: Any = None
            error: Exception | None = None
            try:
                result = work()
            except Exception as exc:
                error = exc

            def finalize() -> None:
                self._set_actions_enabled(True)
                if error is not None:
                    self._handle_error(error)
                    return
                on_success(result)

            self.root.after(0, finalize)

        threading.Thread(target=runner, daemon=True).start()

    def _handle_error(self, error: Exception) -> None:
        if isinstance(error, AuthenticationError):
            self._set_status(str(error), is_error=True)
            return
        if isinstance(error, (InvalidContainerError, SecureAudioError, OSError)):
            self._set_status(str(error), is_error=True)
            return
        self._set_status(f"{self.t('status_error_prefix')}: {error}", is_error=True)

    def _set_actions_enabled(self, enabled: bool) -> None:
        state = "normal" if enabled else "disabled"
        widgets = [
            self.select_mp3_btn,
            self.choose_output_btn,
            self.encrypt_btn,
            self.open_audx_btn,
            self.load_audio_btn,
            self.prev_btn,
            self.play_btn,
            self.stop_btn,
            self.next_btn,
        ]
        for widget in widgets:
            widget.configure(state=state)
        if not enabled:
            return
        if not self.admin_unlocked:
            self.admin_mode_btn.configure(state="disabled")
        if len(self.playlist) <= 1:
            self.prev_btn.configure(state="disabled")
            self.next_btn.configure(state="disabled")

    def _render_playlist(self) -> None:
        self.playlist_listbox.delete(0, "end")
        for entry in self.playlist:
            title = f"{entry.title}"
            if entry.artist:
                title = f"{title} - {entry.artist}"
            title = f"{title} ({self._format_time(entry.duration)})"
            self.playlist_listbox.insert("end", title)
        if self.playlist:
            self.playlist_listbox.selection_set(0)

    def _apply_player_state(self, next_state: PlayerState) -> None:
        self.current_state = next_state
        if next_state.current_index >= 0 and next_state.current_index < self.playlist_listbox.size():
            self.playlist_listbox.selection_clear(0, "end")
            self.playlist_listbox.selection_set(next_state.current_index)
            self.playlist_listbox.see(next_state.current_index)
        self.seek_scale.configure(to=max(next_state.duration_seconds, 1.0))
        self.seek_scale.set(max(0.0, next_state.position_seconds))
        self.elapsed_label.configure(text=self._format_time(next_state.position_seconds))
        self.total_label.configure(text=self._format_time(next_state.duration_seconds))
        self._suspend_volume_event = True
        self.volume_scale.set(next_state.volume)
        self._suspend_volume_event = False
        now_playing = next_state.now_playing or self.t("no_track")
        self.now_playing_label.configure(text=now_playing)
        has_multiple = len(self.playlist) > 1
        self.prev_btn.configure(state=("normal" if has_multiple else "disabled"))
        self.next_btn.configure(state=("normal" if has_multiple else "disabled"))

    def _poll_state(self) -> None:
        if self.player is not None:
            try:
                self._apply_player_state(self.player.snapshot())
            except Exception:
                pass
        self.root.after(750, self._poll_state)

    def _on_playlist_select(self, _event: tk.Event[Any]) -> None:
        if self.player is None:
            return
        selection = self.playlist_listbox.curselection()
        if not selection:
            return
        self._send_playback_command("play", selection[0])

    def _on_seek_release(self, _event: tk.Event[Any]) -> None:
        self._send_playback_command("seek", self.seek_scale.get())

    def _on_volume_change(self, value: str) -> None:
        if self._suspend_volume_event:
            return
        self._send_playback_command("volume", value)

    def _seek_delta(self, delta: float) -> None:
        if not self.current_state:
            return
        self._send_playback_command("seek", self.current_state.position_seconds + delta)

    def _volume_delta(self, delta: int) -> None:
        current = int(float(self.volume_scale.get()))
        self._send_playback_command("volume", max(0, min(100, current + delta)))

    @staticmethod
    def _format_time(seconds: float) -> str:
        total = max(0, int(seconds))
        mins = str(total // 60).zfill(2)
        secs = str(total % 60).zfill(2)
        return f"{mins}:{secs}"


def run() -> None:
    root = tk.Tk()
    TkSecureAudioApp(root)
    try:
        root.mainloop()
    except KeyboardInterrupt:
        pass
    except Exception as exc:
        messagebox.showerror("Error", str(exc))


