const TRANSLATIONS = {
  es: {
    "app.title": "Secure Audio Player",
    "brand.tagline": "Reproduccion local de audio",
    "lang.title": "Idioma / Language",
    "mode.title": "Modo",
    "mode.user": "Usuario",
    "mode.admin": "Administrador",
    "mode.enter_admin": "Ingresar al admin",
    "mode.lock_admin": "Bloquear admin",
    "summary.title": "Resumen",
    "mode.desc_locked": "Solo el modo usuario esta disponible hasta desbloquear admin.",
    "summary.user_locked": "Usa la zona de usuario para reproducir un audio.",
    "summary.admin": "Esta zona esta pensada para preparar la biblioteca segura antes de distribuirla.",
    "summary.user": "Esta zona esta pensada para cargar y reproducir un audio.",
    "admin.auth_title": "Ingresar codigo de administrador",
    "admin.code_label": "Codigo admin",
    "admin.unlock": "Desbloquear",
    "admin.zone": "Zona de administrador",
    "admin.hero_title": "Preparar biblioteca",
    "admin.hero_subtitle": "Selecciona MP3, define la clave y prepara la biblioteca para reproduccion.",
    "admin.badge_encrypt": "Gestion local",
    "admin.mp3_title": "Archivos MP3",
    "admin.select_mp3": "Seleccionar MP3",
    "admin.output_title": "Configuracion de salida",
    "admin.encrypt_password": "Clave de acceso",
    "admin.output_placeholder": "Carpeta de salida",
    "admin.browse": "Examinar",
    "admin.encrypt_button": "Preparar biblioteca",
    "user.zone": "Zona de usuario",
    "user.playlist_title": "Audio seleccionado",
    "user.open_audx": "Abrir audio AUDX",
    "user.playback_passphrase": "Clave de reproduccion",
    "user.load_library": "Cargar audio",
    "controls.prev": "Anterior",
    "controls.play_pause": "Play/Pausa",
    "controls.stop": "Detener",
    "controls.next": "Siguiente",
    "controls.volume": "Volumen",
    "shortcuts.title": "Atajos de teclado",
    "shortcuts.play_pause": "Espacio play o pausa",
    "shortcuts.seek": "Izq/Der mover 5s",
    "shortcuts.volume": "Arriba/Abajo volumen",
    "shortcuts.next_prev": "N siguiente, P anterior",
    "status.ready": "Listo",
    "status.need_admin_code": "Debes desbloquear la zona admin con el codigo.",
    "status.admin_unlocked": "Admin desbloqueado.",
    "status.admin_locked": "Admin bloqueado.",
    "status.admin_lock_error": "No se pudo bloquear admin.",
    "status.admin_selected_mp3": "{count} archivo(s) MP3 seleccionado(s).",
    "status.admin_encrypted": "{count} archivo(s) procesado(s) en la biblioteca.",
    "status.need_playback_pass": "Ingresa primero la clave de reproduccion.",
    "status.library_files_selected": "Archivo seleccionado. Ingresa la clave para cargar.",
    "status.library_not_selected": "Primero debes seleccionar un archivo AUDX.",
    "status.playlist_loaded": "Audio cargado.",
    "status.loading_audio": "Cargando audio...",
    "status.mode_admin_desc": "Gestiona los MP3 y genera archivos protegidos.",
    "status.mode_user_desc": "Reproduce tus pistas como usuario final.",
    "status.mode_need_code": "Ingresa el codigo para habilitar el modo administrador.",
    "player.no_track": "Sin pista seleccionada",
    "player.subtitle_idle": "Carga un audio para iniciar reproduccion.",
    "player.subtitle_playing": "Reproduccion activa.",
    "player.subtitle_paused": "Reproduccion en pausa.",
  },
  en: {
    "app.title": "Secure Audio Player",
    "brand.tagline": "Local audio playback",
    "lang.title": "Language / Idioma",
    "mode.title": "Mode",
    "mode.user": "User",
    "mode.admin": "Administrator",
    "mode.enter_admin": "Enter admin",
    "mode.lock_admin": "Lock admin",
    "summary.title": "Summary",
    "mode.desc_locked": "Only user mode is available until admin is unlocked.",
    "summary.user_locked": "Use user mode to play one audio file.",
    "summary.admin": "This area is for preparing the library before distribution.",
    "summary.user": "This area is for loading and playing one audio file.",
    "admin.auth_title": "Enter administrator code",
    "admin.code_label": "Admin code",
    "admin.unlock": "Unlock",
    "admin.zone": "Administrator zone",
    "admin.hero_title": "Prepare library",
    "admin.hero_subtitle": "Select MP3 files, set passphrase, and prepare the library for playback.",
    "admin.badge_encrypt": "Local management",
    "admin.mp3_title": "MP3 files",
    "admin.select_mp3": "Select MP3",
    "admin.output_title": "Output configuration",
    "admin.encrypt_password": "Access passphrase",
    "admin.output_placeholder": "Output folder",
    "admin.browse": "Browse",
    "admin.encrypt_button": "Prepare library",
    "user.zone": "User zone",
    "user.playlist_title": "Selected audio",
    "user.open_audx": "Open AUDX audio",
    "user.playback_passphrase": "Playback passphrase",
    "user.load_library": "Load audio",
    "controls.prev": "Previous",
    "controls.play_pause": "Play/Pause",
    "controls.stop": "Stop",
    "controls.next": "Next",
    "controls.volume": "Volume",
    "shortcuts.title": "Keyboard shortcuts",
    "shortcuts.play_pause": "Space play or pause",
    "shortcuts.seek": "Left/Right seek 5s",
    "shortcuts.volume": "Up/Down volume",
    "shortcuts.next_prev": "N next, P previous",
    "status.ready": "Ready",
    "status.need_admin_code": "You must unlock admin mode with the code.",
    "status.admin_unlocked": "Admin unlocked.",
    "status.admin_locked": "Admin locked.",
    "status.admin_lock_error": "Could not lock admin.",
    "status.admin_selected_mp3": "{count} MP3 file(s) selected.",
    "status.admin_encrypted": "{count} file(s) processed into the library.",
    "status.need_playback_pass": "Enter playback passphrase first.",
    "status.library_files_selected": "Audio file selected. Enter passphrase to load.",
    "status.library_not_selected": "You must select one AUDX file first.",
    "status.playlist_loaded": "Audio loaded.",
    "status.loading_audio": "Loading audio...",
    "status.mode_admin_desc": "Manage MP3 files and generate protected files.",
    "status.mode_user_desc": "Play tracks as end user.",
    "status.mode_need_code": "Enter the code to enable administrator mode.",
    "player.no_track": "No track selected",
    "player.subtitle_idle": "Load one audio file to start playback.",
    "player.subtitle_playing": "Playback is active.",
    "player.subtitle_paused": "Playback is paused.",
  },
};

const state = {
  selectedMp3Files: [],
  playlist: [],
  pendingLibraryFiles: [],
  playbackPassword: "",
  currentState: null,
  currentMode: "user",
  language: "es",
  admin: {
    hasPin: true,
    unlocked: false,
  },
};

const els = {
  langEsBtn: document.getElementById("lang-es-btn"),
  langEnBtn: document.getElementById("lang-en-btn"),
  adminModeBtn: document.getElementById("admin-mode-btn"),
  userModeBtn: document.getElementById("user-mode-btn"),
  adminAccessBtn: document.getElementById("admin-access-btn"),
  adminLockBtn: document.getElementById("admin-lock-btn"),
  adminAuthPanel: document.getElementById("admin-auth-panel"),
  adminAuthTitle: document.getElementById("admin-auth-title"),
  adminUnlockFields: document.getElementById("admin-unlock-fields"),
  adminCodeInput: document.getElementById("admin-code-input"),
  adminCodeUnlockBtn: document.getElementById("admin-code-unlock-btn"),
  modeDescription: document.getElementById("mode-description"),
  sidebarSummary: document.getElementById("sidebar-summary"),
  adminView: document.getElementById("admin-view"),
  userView: document.getElementById("user-view"),
  selectMp3Btn: document.getElementById("select-mp3-btn"),
  selectedMp3List: document.getElementById("selected-mp3-list"),
  encryptPassword: document.getElementById("encrypt-password"),
  chooseOutputBtn: document.getElementById("choose-output-btn"),
  outputDir: document.getElementById("output-dir"),
  encryptBtn: document.getElementById("encrypt-btn"),
  openAudxBtn: document.getElementById("open-audx-btn"),
  playbackAuthPanel: document.getElementById("playback-auth-panel"),
  loadLibraryBtn: document.getElementById("load-library-btn"),
  playbackPassword: document.getElementById("playback-password"),
  playlist: document.getElementById("playlist"),
  playBtn: document.getElementById("play-btn"),
  stopBtn: document.getElementById("stop-btn"),
  prevBtn: document.getElementById("prev-btn"),
  nextBtn: document.getElementById("next-btn"),
  seekBar: document.getElementById("seek-bar"),
  elapsedTime: document.getElementById("elapsed-time"),
  totalTime: document.getElementById("total-time"),
  volumeSlider: document.getElementById("volume-slider"),
  statusText: document.getElementById("status-text"),
  statusLoader: document.getElementById("status-loader"),
  nowPlayingTitle: document.getElementById("now-playing-title"),
  nowPlayingSubtitle: document.getElementById("now-playing-subtitle"),
};

try {
  const savedLang = window.localStorage.getItem("audx_lang");
  if (savedLang === "es" || savedLang === "en") {
    state.language = savedLang;
  }
} catch (_error) {
  state.language = "es";
}

function t(key, vars = {}) {
  const dict = TRANSLATIONS[state.language] || TRANSLATIONS.es;
  let text = dict[key] || key;
  Object.entries(vars).forEach(([name, value]) => {
    text = text.replace(`{${name}}`, String(value));
  });
  return text;
}

function applyTranslations() {
  document.documentElement.lang = state.language;
  document.title = t("app.title");
  document.querySelectorAll("[data-i18n]").forEach((node) => {
    node.textContent = t(node.dataset.i18n);
  });
  document.querySelectorAll("[data-i18n-placeholder]").forEach((node) => {
    node.placeholder = t(node.dataset.i18nPlaceholder);
  });
  els.langEsBtn.classList.toggle("primary", state.language === "es");
  els.langEnBtn.classList.toggle("primary", state.language === "en");
  updateModeTexts();
  const hasMultiple = (state.playlist?.length || 0) > 1;
  els.prevBtn.disabled = !hasMultiple;
  els.nextBtn.disabled = !hasMultiple;
  updateNowPlayingTexts();
}

function setLanguage(language) {
  state.language = language === "en" ? "en" : "es";
  try {
    window.localStorage.setItem("audx_lang", state.language);
  } catch (_error) {}
  applyTranslations();
}

async function callApi(method, ...args) {
  return window.pywebview.api[method](...args);
}

function setStatus(message, isError = false, showLoading = false) {
  els.statusText.textContent = message;
  els.statusText.style.color = isError ? "#ff9b9b" : "";
  if (els.statusLoader) {
    els.statusLoader.classList.toggle("hidden", !showLoading);
  }
}

function updateModeTexts() {
  if (!state.admin.unlocked) {
    els.modeDescription.textContent = t("status.mode_need_code");
    els.sidebarSummary.textContent = t("summary.user_locked");
    els.adminAuthTitle.textContent = t("admin.auth_title");
    return;
  }
  if (state.currentMode === "admin") {
    els.modeDescription.textContent = t("status.mode_admin_desc");
    els.sidebarSummary.textContent = t("summary.admin");
  } else {
    els.modeDescription.textContent = t("status.mode_user_desc");
    els.sidebarSummary.textContent = t("summary.user");
  }
}

function setMode(mode) {
  if (mode === "admin" && !state.admin.unlocked) {
    setStatus(t("status.need_admin_code"), true);
    return;
  }
  state.currentMode = mode;
  const isAdmin = mode === "admin";
  els.adminView.classList.toggle("active", isAdmin);
  els.userView.classList.toggle("active", !isAdmin);
  els.adminModeBtn.classList.toggle("primary", isAdmin);
  els.userModeBtn.classList.toggle("primary", !isAdmin);
  updateModeTexts();
}

function setAdminState(admin) {
  state.admin.hasPin = !!admin?.has_pin;
  state.admin.unlocked = !!admin?.unlocked;
  els.adminModeBtn.disabled = !state.admin.unlocked;
  els.adminAccessBtn.classList.toggle("hidden", state.admin.unlocked);
  els.adminLockBtn.classList.toggle("hidden", !state.admin.unlocked);
  if (state.admin.unlocked) {
    els.adminAuthPanel.classList.add("hidden");
  }
  if (!state.admin.unlocked && state.currentMode === "admin") {
    setMode("user");
  }
  updateModeTexts();
}

function updateNowPlayingTexts() {
  const nextState = state.currentState;
  els.nowPlayingTitle.textContent = nextState?.now_playing || t("player.no_track");
  if (nextState?.is_playing) {
    els.nowPlayingSubtitle.textContent = t("player.subtitle_playing");
  } else if (nextState?.is_paused) {
    els.nowPlayingSubtitle.textContent = t("player.subtitle_paused");
  } else {
    els.nowPlayingSubtitle.textContent = t("player.subtitle_idle");
  }
}

async function refreshAdminStatus() {
  const response = await callApi("admin_status");
  if (response.ok) {
    setAdminState(response.admin);
  }
}

function toggleAdminPanel() {
  if (state.admin.unlocked) return;
  els.adminAuthPanel.classList.toggle("hidden");
}

async function unlockAdmin() {
  const code = els.adminCodeInput.value.trim();
  const response = await callApi("admin_unlock", code);
  if (!response.ok) {
    setStatus(response.error, true);
    return;
  }
  els.adminCodeInput.value = "";
  setAdminState(response.admin);
  setMode("admin");
  setStatus(t("status.admin_unlocked"));
}

async function lockAdmin() {
  const response = await callApi("admin_lock");
  if (!response.ok) {
    setStatus(t("status.admin_lock_error"), true);
    return;
  }
  setAdminState(response.admin);
  setMode("user");
  setStatus(t("status.admin_locked"));
}

function renderSelectedMp3Files() {
  els.selectedMp3List.innerHTML = "";
  state.selectedMp3Files.forEach((file) => {
    const li = document.createElement("li");
    li.textContent = file;
    els.selectedMp3List.appendChild(li);
  });
}

function renderPlaylist() {
  els.playlist.innerHTML = "";
  state.playlist.forEach((item, index) => {
    const li = document.createElement("li");
    const active = state.currentState && state.currentState.current_index === index;
    if (active) li.classList.add("active");
    const button = document.createElement("button");
    button.textContent = `${item.title}${item.artist ? ` - ${item.artist}` : ""} (${formatTime(item.duration)})`;
    button.addEventListener("click", () => playIndex(index));
    li.appendChild(button);
    els.playlist.appendChild(li);
  });
}

function applyPlayerState(nextState) {
  state.currentState = nextState;
  renderPlaylist();
  els.volumeSlider.value = nextState.volume;
  els.seekBar.max = Math.max(nextState.duration_seconds || 0, 1);
  if (!els.seekBar.matches(":active")) {
    els.seekBar.value = nextState.position_seconds || 0;
  }
  els.elapsedTime.textContent = formatTime(nextState.position_seconds || 0);
  els.totalTime.textContent = formatTime(nextState.duration_seconds || 0);
  const hasMultiple = (state.playlist?.length || 0) > 1;
  els.prevBtn.disabled = !hasMultiple;
  els.nextBtn.disabled = !hasMultiple;
  updateNowPlayingTexts();
}

function formatTime(seconds) {
  const total = Math.max(0, Math.floor(seconds || 0));
  const mins = String(Math.floor(total / 60)).padStart(2, "0");
  const secs = String(total % 60).padStart(2, "0");
  return `${mins}:${secs}`;
}

async function bootstrap() {
  setLanguage(state.language);
  const response = await callApi("bootstrap");
  if (response.ok && response.admin) {
    setAdminState(response.admin);
  } else {
    await refreshAdminStatus();
  }
  setMode("user");
  if (response.ok && response.audio && response.audio.error) {
    setStatus(response.audio.error, true);
  } else {
    setStatus(t("status.ready"));
  }
  const hasMultiple = (state.playlist?.length || 0) > 1;
  els.prevBtn.disabled = !hasMultiple;
  els.nextBtn.disabled = !hasMultiple;
  updateNowPlayingTexts();
  pollState();
}

async function selectMp3Files() {
  const response = await callApi("browse_mp3_files");
  if (!response.ok) {
    setStatus(response.error, true);
    return;
  }
  state.selectedMp3Files = response.files || [];
  renderSelectedMp3Files();
  setStatus(t("status.admin_selected_mp3", { count: state.selectedMp3Files.length }));
}

async function chooseOutputDir() {
  const response = await callApi("choose_output_dir");
  if (!response.ok) {
    setStatus(response.error, true);
    return;
  }
  els.outputDir.value = response.directory || "";
}

async function encryptSelectedFiles() {
  const password = els.encryptPassword.value;
  const outputDir = els.outputDir.value;
  const response = await callApi("encrypt_selected_files", password, outputDir);
  if (!response.ok) {
    setStatus(response.error, true);
    return;
  }
  setStatus(t("status.admin_encrypted", { count: response.created.length }));
}

async function openAudxFiles() {
  const picked = await callApi("browse_encrypted_files");
  if (!picked.files || !picked.files.length) return;
  state.pendingLibraryFiles = [picked.files[0]];
  els.playbackAuthPanel.classList.remove("hidden");
  els.playbackPassword.focus();
  setStatus(t("status.library_files_selected"));
}

async function loadSelectedLibrary() {
  if (!state.pendingLibraryFiles.length) {
    setStatus(t("status.library_not_selected"), true);
    return;
  }
  const password = els.playbackPassword.value.trim();
  if (!password) {
    setStatus(t("status.need_playback_pass"), true);
    return;
  }
  state.playbackPassword = password;
  setStatus(t("status.loading_audio"), false, true);
  els.loadLibraryBtn.disabled = true;
  els.openAudxBtn.disabled = true;
  try {
    let response;
    try {
      response = await callApi("load_playlist", JSON.stringify(state.pendingLibraryFiles), password);
    } catch (error) {
      const detail = error && error.message ? error.message : String(error || "Error desconocido");
      setStatus(`No se pudo cargar el audio: ${detail}`, true);
      return;
    }
    if (!response.ok) {
      setStatus(response.error, true);
      return;
    }
    state.playlist = response.playlist || [];
    applyPlayerState(response.state);
    setStatus(t("status.playlist_loaded"));
  } finally {
    els.loadLibraryBtn.disabled = false;
    els.openAudxBtn.disabled = false;
  }
}

async function playIndex(index) {
  const response = await callApi("playback_command", "play", index);
  if (!response.ok) {
    setStatus(response.error, true);
    return;
  }
  applyPlayerState(response.state);
}

async function sendPlaybackCommand(command, value = null) {
  const response = await callApi("playback_command", command, value);
  if (!response.ok) {
    setStatus(response.error, true);
    return;
  }
  applyPlayerState(response.state);
}

async function pollState() {
  try {
    const response = await callApi("poll_state");
    if (response.ok && response.state) {
      applyPlayerState(response.state);
    }
  } catch (_error) {
  } finally {
    window.setTimeout(pollState, 750);
  }
}

document.addEventListener("keydown", (event) => {
  if (["INPUT", "TEXTAREA", "SELECT"].includes(document.activeElement.tagName)) return;
  if (event.code === "Space") {
    event.preventDefault();
    sendPlaybackCommand("toggle");
  } else if (event.code === "ArrowRight") {
    event.preventDefault();
    const current = state.currentState?.position_seconds || 0;
    sendPlaybackCommand("seek", current + 5);
  } else if (event.code === "ArrowLeft") {
    event.preventDefault();
    const current = state.currentState?.position_seconds || 0;
    sendPlaybackCommand("seek", current - 5);
  } else if (event.code === "ArrowUp") {
    event.preventDefault();
    const next = Math.min(100, Number(els.volumeSlider.value) + 5);
    els.volumeSlider.value = next;
    sendPlaybackCommand("volume", next);
  } else if (event.code === "ArrowDown") {
    event.preventDefault();
    const next = Math.max(0, Number(els.volumeSlider.value) - 5);
    els.volumeSlider.value = next;
    sendPlaybackCommand("volume", next);
  } else if (event.key.toLowerCase() === "n") {
    sendPlaybackCommand("next");
  } else if (event.key.toLowerCase() === "p") {
    sendPlaybackCommand("previous");
  }
});

els.langEsBtn.addEventListener("click", () => setLanguage("es"));
els.langEnBtn.addEventListener("click", () => setLanguage("en"));
els.selectMp3Btn.addEventListener("click", selectMp3Files);
els.chooseOutputBtn.addEventListener("click", chooseOutputDir);
els.encryptBtn.addEventListener("click", encryptSelectedFiles);
els.adminModeBtn.addEventListener("click", () => setMode("admin"));
els.userModeBtn.addEventListener("click", () => setMode("user"));
els.adminAccessBtn.addEventListener("click", toggleAdminPanel);
els.adminLockBtn.addEventListener("click", lockAdmin);
els.adminCodeUnlockBtn.addEventListener("click", unlockAdmin);
els.openAudxBtn.addEventListener("click", openAudxFiles);
els.loadLibraryBtn.addEventListener("click", loadSelectedLibrary);
els.playBtn.addEventListener("click", () => sendPlaybackCommand("toggle"));
els.stopBtn.addEventListener("click", () => sendPlaybackCommand("stop"));
els.prevBtn.addEventListener("click", () => sendPlaybackCommand("previous"));
els.nextBtn.addEventListener("click", () => sendPlaybackCommand("next"));
els.seekBar.addEventListener("change", () => sendPlaybackCommand("seek", Number(els.seekBar.value)));
els.volumeSlider.addEventListener("input", () => sendPlaybackCommand("volume", Number(els.volumeSlider.value)));

window.addEventListener("pywebviewready", bootstrap);
