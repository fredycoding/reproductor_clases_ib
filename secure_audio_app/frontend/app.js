const state = {
  selectedMp3Files: [],
  playlist: [],
  playbackPassword: "",
  currentState: null,
};

const els = {
  selectMp3Btn: document.getElementById("select-mp3-btn"),
  selectedMp3List: document.getElementById("selected-mp3-list"),
  encryptPassword: document.getElementById("encrypt-password"),
  chooseOutputBtn: document.getElementById("choose-output-btn"),
  outputDir: document.getElementById("output-dir"),
  encryptBtn: document.getElementById("encrypt-btn"),
  openAudxBtn: document.getElementById("open-audx-btn"),
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
  repeatSelect: document.getElementById("repeat-select"),
  shuffleToggle: document.getElementById("shuffle-toggle"),
  statusText: document.getElementById("status-text"),
  nowPlayingTitle: document.getElementById("now-playing-title"),
  nowPlayingSubtitle: document.getElementById("now-playing-subtitle"),
};

async function callApi(method, ...args) {
  return window.pywebview.api[method](...args);
}

function setStatus(message, isError = false) {
  els.statusText.textContent = message;
  els.statusText.style.color = isError ? "#ff9b9b" : "";
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
  els.repeatSelect.value = nextState.repeat_mode;
  els.shuffleToggle.checked = nextState.shuffle_enabled;
  els.seekBar.max = Math.max(nextState.duration_seconds || 0, 1);
  if (!els.seekBar.matches(":active")) {
    els.seekBar.value = nextState.position_seconds || 0;
  }
  els.elapsedTime.textContent = formatTime(nextState.position_seconds || 0);
  els.totalTime.textContent = formatTime(nextState.duration_seconds || 0);
  els.nowPlayingTitle.textContent = nextState.now_playing || "No track selected";
  els.nowPlayingSubtitle.textContent = nextState.is_playing
    ? "Playback is active."
    : nextState.is_paused
      ? "Playback is paused."
      : "Load encrypted files to start playback.";
}

function formatTime(seconds) {
  const total = Math.max(0, Math.floor(seconds || 0));
  const mins = String(Math.floor(total / 60)).padStart(2, "0");
  const secs = String(total % 60).padStart(2, "0");
  return `${mins}:${secs}`;
}

async function bootstrap() {
  await callApi("bootstrap");
  setStatus("Ready");
  pollState();
}

async function selectMp3Files() {
  const response = await callApi("browse_mp3_files");
  state.selectedMp3Files = response.files || [];
  renderSelectedMp3Files();
  setStatus(`${state.selectedMp3Files.length} MP3 file(s) selected.`);
}

async function chooseOutputDir() {
  const response = await callApi("choose_output_dir");
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
  setStatus(`Encrypted ${response.created.length} file(s) to AUDX.`);
}

async function openAudxFiles() {
  const picked = await callApi("browse_encrypted_files");
  if (!picked.files || !picked.files.length) return;
  const password = els.playbackPassword.value;
  if (!password) {
    setStatus("Enter the playback passphrase first.", true);
    return;
  }
  state.playbackPassword = password;
  const response = await callApi("load_playlist", JSON.stringify(picked.files), password);
  if (!response.ok) {
    setStatus(response.error, true);
    return;
  }
  state.playlist = response.playlist || [];
  applyPlayerState(response.state);
  setStatus(`Loaded ${state.playlist.length} encrypted track(s).`);
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

els.selectMp3Btn.addEventListener("click", selectMp3Files);
els.chooseOutputBtn.addEventListener("click", chooseOutputDir);
els.encryptBtn.addEventListener("click", encryptSelectedFiles);
els.openAudxBtn.addEventListener("click", openAudxFiles);
els.playBtn.addEventListener("click", () => sendPlaybackCommand("toggle"));
els.stopBtn.addEventListener("click", () => sendPlaybackCommand("stop"));
els.prevBtn.addEventListener("click", () => sendPlaybackCommand("previous"));
els.nextBtn.addEventListener("click", () => sendPlaybackCommand("next"));
els.seekBar.addEventListener("change", () => sendPlaybackCommand("seek", Number(els.seekBar.value)));
els.volumeSlider.addEventListener("input", () => sendPlaybackCommand("volume", Number(els.volumeSlider.value)));
els.repeatSelect.addEventListener("change", () => sendPlaybackCommand("repeat", els.repeatSelect.value));
els.shuffleToggle.addEventListener("change", () => sendPlaybackCommand("shuffle", els.shuffleToggle.checked));

window.addEventListener("pywebviewready", bootstrap);
