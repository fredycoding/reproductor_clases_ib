from __future__ import annotations

import ctypes
import random
import threading
from dataclasses import dataclass, field
from pathlib import Path

import vlc

from .crypto import AudxCrypto, DecryptedAudio

MEDIA_OPEN_CB = ctypes.CFUNCTYPE(
    ctypes.c_int,
    ctypes.c_void_p,
    ctypes.POINTER(ctypes.c_void_p),
    ctypes.POINTER(ctypes.c_uint64),
)
MEDIA_READ_CB = ctypes.CFUNCTYPE(
    ctypes.c_ssize_t,
    ctypes.c_void_p,
    ctypes.POINTER(ctypes.c_char),
    ctypes.c_size_t,
)
MEDIA_SEEK_CB = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_void_p, ctypes.c_uint64)
MEDIA_CLOSE_CB = ctypes.CFUNCTYPE(None, ctypes.c_void_p)


@dataclass(slots=True)
class PlaylistEntry:
    path: str
    title: str
    artist: str
    duration: float


@dataclass(slots=True)
class PlayerState:
    playlist: list[PlaylistEntry] = field(default_factory=list)
    current_index: int = -1
    is_playing: bool = False
    is_paused: bool = False
    volume: int = 80
    repeat_mode: str = "off"
    shuffle_enabled: bool = False
    position_seconds: float = 0.0
    duration_seconds: float = 0.0
    now_playing: str = ""


class MemoryAudioStream:
    def __init__(self, data: bytearray) -> None:
        self.data = data
        self.size = len(data)
        self.position = 0

    def open(self) -> int:
        self.position = 0
        return self.size

    def read(self, length: int) -> bytes:
        remaining = self.size - self.position
        if remaining <= 0:
            return b""
        chunk_size = min(length, remaining)
        chunk = bytes(self.data[self.position : self.position + chunk_size])
        self.position += chunk_size
        return chunk

    def seek(self, offset: int) -> int:
        if offset < 0 or offset > self.size:
            return -1
        self.position = offset
        return 0

    def close(self) -> None:
        self.position = 0

    def wipe(self) -> None:
        for index in range(len(self.data)):
            self.data[index] = 0


class SecureVlcPlayer:
    def __init__(self, crypto: AudxCrypto) -> None:
        self.crypto = crypto
        self.instance = vlc.Instance("--no-video", "--quiet")
        self.player = self.instance.media_player_new()
        self.state = PlayerState()
        self.password = ""
        self._lock = threading.RLock()
        self._current_stream: MemoryAudioStream | None = None
        self._current_audio: DecryptedAudio | None = None
        self._stream_registry: dict[int, MemoryAudioStream] = {}
        self._vlc_callbacks = self._create_vlc_callbacks()
        self._bind_events()
        self.set_volume(self.state.volume)

    def load_playlist(self, file_paths: list[str], password: str) -> list[PlaylistEntry]:
        entries: list[PlaylistEntry] = []
        for file_path in file_paths:
            header = self.crypto.inspect_file(file_path)
            entries.append(
                PlaylistEntry(
                    path=file_path,
                    title=header.get("track_title") or header.get("original_name") or Path(file_path).stem,
                    artist=header.get("artist", ""),
                    duration=float(header.get("duration_seconds", 0.0)),
                )
            )

        with self._lock:
            self.stop()
            self.state.playlist = entries
            self.state.current_index = -1
            self.password = password
            return list(entries)

    def play_index(self, index: int) -> PlayerState:
        with self._lock:
            if index < 0 or index >= len(self.state.playlist):
                raise IndexError("Track index out of range.")
            self._load_current(index)
            self.player.play()
            self.state.current_index = index
            self.state.is_playing = True
            self.state.is_paused = False
            return self.snapshot()

    def toggle_play_pause(self) -> PlayerState:
        with self._lock:
            if self.state.current_index < 0 and self.state.playlist:
                return self.play_index(0)
            return self.pause()

    def pause(self) -> PlayerState:
        with self._lock:
            self.player.pause()
            self.state.is_paused = not self.state.is_paused
            self.state.is_playing = not self.state.is_paused
            return self.snapshot()

    def stop(self) -> PlayerState:
        with self._lock:
            self.player.stop()
            self.state.is_playing = False
            self.state.is_paused = False
            self.state.position_seconds = 0.0
            self._release_current_media()
            return self.snapshot()

    def next_track(self) -> PlayerState:
        with self._lock:
            next_index = self._resolve_next_index()
            if next_index is None:
                return self.stop()
            return self.play_index(next_index)

    def previous_track(self) -> PlayerState:
        with self._lock:
            if self.state.current_index <= 0:
                return self.snapshot()
            return self.play_index(self.state.current_index - 1)

    def seek(self, seconds: float) -> PlayerState:
        with self._lock:
            if self.state.duration_seconds <= 0:
                return self.snapshot()
            clamped = max(0.0, min(seconds, self.state.duration_seconds))
            self.player.set_time(int(clamped * 1000))
            return self.snapshot()

    def set_volume(self, volume: int) -> PlayerState:
        with self._lock:
            clamped = max(0, min(volume, 100))
            self.player.audio_set_volume(clamped)
            self.state.volume = clamped
            return self.snapshot()

    def set_repeat_mode(self, mode: str) -> PlayerState:
        if mode not in {"off", "all", "one"}:
            raise ValueError("Unsupported repeat mode.")
        with self._lock:
            self.state.repeat_mode = mode
            return self.snapshot()

    def set_shuffle(self, enabled: bool) -> PlayerState:
        with self._lock:
            self.state.shuffle_enabled = bool(enabled)
            return self.snapshot()

    def snapshot(self) -> PlayerState:
        with self._lock:
            current_time = self.player.get_time()
            if current_time >= 0:
                self.state.position_seconds = current_time / 1000.0
            length_ms = self.player.get_length()
            if length_ms > 0:
                self.state.duration_seconds = length_ms / 1000.0
            return PlayerState(
                playlist=list(self.state.playlist),
                current_index=self.state.current_index,
                is_playing=self.state.is_playing,
                is_paused=self.state.is_paused,
                volume=self.state.volume,
                repeat_mode=self.state.repeat_mode,
                shuffle_enabled=self.state.shuffle_enabled,
                position_seconds=self.state.position_seconds,
                duration_seconds=self.state.duration_seconds,
                now_playing=self.state.now_playing,
            )

    def _bind_events(self) -> None:
        self.player.event_manager().event_attach(vlc.EventType.MediaPlayerEndReached, self._on_end_reached)

    def _on_end_reached(self, _event) -> None:
        self.next_track()

    def _resolve_next_index(self) -> int | None:
        if not self.state.playlist:
            return None
        if self.state.repeat_mode == "one" and self.state.current_index >= 0:
            return self.state.current_index
        if self.state.shuffle_enabled and len(self.state.playlist) > 1:
            choices = [idx for idx in range(len(self.state.playlist)) if idx != self.state.current_index]
            return random.choice(choices)
        next_index = self.state.current_index + 1
        if next_index < len(self.state.playlist):
            return next_index
        if self.state.repeat_mode == "all":
            return 0
        return None

    def _load_current(self, index: int) -> None:
        self._release_current_media()
        entry = self.state.playlist[index]
        audio = self.crypto.decrypt_file(entry.path, self.password)
        stream = MemoryAudioStream(audio.audio_bytes)
        stream_id = id(stream)
        self._stream_registry[stream_id] = stream
        media = self.instance.media_new_callbacks(
            self._vlc_callbacks["open"],
            self._vlc_callbacks["read"],
            self._vlc_callbacks["seek"],
            self._vlc_callbacks["close"],
            stream_id,
        )
        self.player.set_media(media)
        self._current_stream = stream
        self._current_audio = audio
        metadata = audio.metadata
        self.state.duration_seconds = float(metadata.get("duration_seconds", 0.0))
        title = metadata.get("track_title") or Path(entry.path).stem
        artist = metadata.get("artist", "")
        self.state.now_playing = f"{title} - {artist}".strip(" -")

    def _release_current_media(self) -> None:
        if self._current_stream is not None:
            self._stream_registry.pop(id(self._current_stream), None)
            self._current_stream.wipe()
            self._current_stream = None
        if self._current_audio is not None:
            self._current_audio.wipe()
            self._current_audio = None

    def _create_vlc_callbacks(self) -> dict[str, object]:
        def open_cb(opaque, data_pointer, size_pointer) -> int:
            stream = self._stream_from_opaque(opaque)
            stream.open()
            data_pointer[0] = ctypes.c_void_p(_opaque_to_int(opaque))
            size_pointer[0] = ctypes.c_uint64(stream.size)
            return 0

        def read_cb(opaque, buffer, length) -> int:
            stream = self._stream_from_opaque(opaque)
            chunk = stream.read(int(length))
            if not chunk:
                return 0
            ctypes.memmove(buffer, chunk, len(chunk))
            return len(chunk)

        def seek_cb(opaque, offset) -> int:
            stream = self._stream_from_opaque(opaque)
            return stream.seek(int(offset))

        def close_cb(opaque) -> None:
            stream = self._stream_from_opaque(opaque)
            stream.close()

        return {
            "open": MEDIA_OPEN_CB(open_cb),
            "read": MEDIA_READ_CB(read_cb),
            "seek": MEDIA_SEEK_CB(seek_cb),
            "close": MEDIA_CLOSE_CB(close_cb),
        }

    def _stream_from_opaque(self, opaque) -> MemoryAudioStream:
        stream_id = _opaque_to_int(opaque)
        stream = self._stream_registry.get(stream_id)
        if stream is None:
            raise RuntimeError("VLC stream handle is invalid.")
        return stream


def _opaque_to_int(value) -> int:
    if isinstance(value, int):
        return value
    if hasattr(value, "value"):
        return int(value.value)
    return int(value)
