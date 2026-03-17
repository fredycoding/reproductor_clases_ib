from __future__ import annotations

import base64
import hashlib
import json
import os
import struct
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from argon2.low_level import Type, hash_secret_raw
except ModuleNotFoundError:
    Type = None
    hash_secret_raw = None
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from mutagen import File as MutagenFile


MAGIC = b"AUDXFILE"
VERSION = 1
HEADER_LEN_STRUCT = struct.Struct(">I")
MAX_HEADER_LEN = 16 * 1024
NONCE_SIZE = 12
SALT_SIZE = 16
DATACLASS_KWARGS = {"slots": True} if sys.version_info >= (3, 10) else {}


class SecureAudioError(Exception):
    pass


class InvalidContainerError(SecureAudioError):
    pass


class AuthenticationError(SecureAudioError):
    pass


@dataclass(**DATACLASS_KWARGS)
class DecryptedAudio:
    metadata: dict[str, Any]
    audio_bytes: bytearray
    source_suffix: str

    def wipe(self) -> None:
        for index in range(len(self.audio_bytes)):
            self.audio_bytes[index] = 0


class AudxCrypto:
    def __init__(self, time_cost: int = 3, memory_cost_kib: int = 65536, parallelism: int = 2) -> None:
        self.time_cost = time_cost
        self.memory_cost_kib = memory_cost_kib
        self.parallelism = parallelism
        self.kdf_name = "scrypt"

    def encrypt_file(self, source_path: str | Path, password: str, output_dir: str | Path) -> Path:
        source = Path(source_path)
        if source.suffix.lower() != ".mp3":
            raise SecureAudioError("Solo se aceptan archivos MP3 para encriptacion.")

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        audio_bytes = source.read_bytes()
        metadata = self._extract_audio_metadata(source)
        container = self.encrypt_bytes(audio_bytes, password=password, metadata=metadata)
        target = output_path / f"{source.stem}.audx"
        target.write_bytes(container)
        return target

    def encrypt_bytes(self, audio_bytes: bytes, password: str, metadata: dict[str, Any]) -> bytes:
        salt = os.urandom(SALT_SIZE)
        nonce = os.urandom(NONCE_SIZE)
        key = self._derive_key(password, salt)

        metadata_bytes = self._canonical_json(metadata)
        plaintext = metadata_bytes + audio_bytes
        header = {
            "alg": "AES-256-GCM",
            "kdf": self.kdf_name,
            "nonce_b64": base64.b64encode(nonce).decode("ascii"),
            "salt_b64": base64.b64encode(salt).decode("ascii"),
            "meta_len": len(metadata_bytes),
            "content_type": "audio/mpeg",
            "original_ext": ".mp3",
            "created_utc": datetime.now(timezone.utc).isoformat(),
            "original_name": metadata.get("original_name", ""),
            "track_title": metadata.get("track_title", ""),
            "artist": metadata.get("artist", ""),
            "duration_seconds": float(metadata.get("duration_seconds", 0.0)),
        }
        if self.kdf_name == "Argon2id":
            header["kdf_params"] = {
                "time_cost": self.time_cost,
                "memory_cost_kib": self.memory_cost_kib,
                "parallelism": self.parallelism,
            }
        else:
            header["kdf_params"] = {"n": 2**14, "r": 8, "p": 1}
        header_bytes = self._canonical_json(header)
        cipher = AESGCM(key)
        ciphertext = cipher.encrypt(nonce, plaintext, header_bytes)
        return MAGIC + bytes([VERSION]) + HEADER_LEN_STRUCT.pack(len(header_bytes)) + header_bytes + ciphertext

    def decrypt_file(self, encrypted_path: str | Path, password: str) -> DecryptedAudio:
        return self.decrypt_bytes(Path(encrypted_path).read_bytes(), password)

    def decrypt_bytes(self, encrypted_bytes: bytes, password: str) -> DecryptedAudio:
        header, header_bytes, ciphertext = self.parse_container(encrypted_bytes)
        salt = self._decode_b64_field(header, "salt_b64", SALT_SIZE)
        nonce = self._decode_b64_field(header, "nonce_b64", NONCE_SIZE)
        key = self._derive_key(password, salt, header)
        cipher = AESGCM(key)

        try:
            plaintext = cipher.decrypt(nonce, ciphertext, header_bytes)
        except Exception as exc:
            raise AuthenticationError("Fallo la autenticacion del archivo o la clave es incorrecta.") from exc

        meta_len = header["meta_len"]
        if not isinstance(meta_len, int) or meta_len <= 0 or meta_len >= len(plaintext):
            raise InvalidContainerError("El contenedor tiene un meta_len invalido.")

        metadata_bytes = plaintext[:meta_len]
        audio_bytes = bytearray(plaintext[meta_len:])
        try:
            metadata = json.loads(metadata_bytes.decode("utf-8"))
        except json.JSONDecodeError as exc:
            raise InvalidContainerError("No se pudo leer la metadata interna del archivo.") from exc

        return DecryptedAudio(metadata=metadata, audio_bytes=audio_bytes, source_suffix=header["original_ext"])

    def inspect_file(self, encrypted_path: str | Path) -> dict[str, Any]:
        raw = Path(encrypted_path).read_bytes()
        header, _, _ = self.parse_container(raw)
        return header

    def parse_container(self, encrypted_bytes: bytes) -> tuple[dict[str, Any], bytes, bytes]:
        if len(encrypted_bytes) < len(MAGIC) + 1 + HEADER_LEN_STRUCT.size:
            raise InvalidContainerError("El archivo es demasiado pequeno para ser un contenedor valido.")
        if encrypted_bytes[: len(MAGIC)] != MAGIC:
            raise InvalidContainerError("El archivo no pertenece al formato AUDX.")

        version = encrypted_bytes[len(MAGIC)]
        if version != VERSION:
            raise InvalidContainerError(f"Version no soportada: {version}")

        header_len_start = len(MAGIC) + 1
        header_len_end = header_len_start + HEADER_LEN_STRUCT.size
        header_len = HEADER_LEN_STRUCT.unpack(encrypted_bytes[header_len_start:header_len_end])[0]
        if header_len <= 0 or header_len > MAX_HEADER_LEN:
            raise InvalidContainerError("La longitud del encabezado es invalida.")

        header_start = header_len_end
        header_end = header_start + header_len
        if header_end >= len(encrypted_bytes):
            raise InvalidContainerError("El contenedor esta truncado.")

        header_bytes = encrypted_bytes[header_start:header_end]
        ciphertext = encrypted_bytes[header_end:]
        try:
            header = json.loads(header_bytes.decode("utf-8"))
        except json.JSONDecodeError as exc:
            raise InvalidContainerError("El encabezado JSON es invalido.") from exc

        self._validate_header(header)
        return header, header_bytes, ciphertext

    def _validate_header(self, header: dict[str, Any]) -> None:
        required = {
            "alg": "AES-256-GCM",
            "content_type": "audio/mpeg",
            "original_ext": ".mp3",
        }
        for field, expected in required.items():
            if header.get(field) != expected:
                raise InvalidContainerError(f"Campo de encabezado invalido: {field}")

        meta_len = header.get("meta_len")
        if not isinstance(meta_len, int) or meta_len <= 0:
            raise InvalidContainerError("Campo meta_len invalido.")

        if header.get("kdf") not in {"Argon2id", "scrypt"}:
            raise InvalidContainerError("Campo kdf invalido.")

        self._decode_b64_field(header, "nonce_b64", NONCE_SIZE)
        self._decode_b64_field(header, "salt_b64", SALT_SIZE)

    def _decode_b64_field(self, header: dict[str, Any], field: str, expected_size: int) -> bytes:
        value = header.get(field)
        if not isinstance(value, str):
            raise InvalidContainerError(f"Campo {field} invalido.")
        try:
            decoded = base64.b64decode(value)
        except Exception as exc:
            raise InvalidContainerError(f"No se pudo decodificar {field}.") from exc
        if len(decoded) != expected_size:
            raise InvalidContainerError(f"Longitud invalida para {field}.")
        return decoded

    def _derive_key(self, password: str, salt: bytes, header: dict[str, Any] | None = None) -> bytes:
        if len(password) < 10:
            raise SecureAudioError("La clave debe tener al menos 10 caracteres.")
        kdf_name = header.get("kdf") if header else self.kdf_name
        kdf_params = header.get("kdf_params", {}) if header else {}
        if kdf_name == "Argon2id":
            if hash_secret_raw is None or Type is None:
                raise SecureAudioError(
                    "Este build no incluye Argon2id (argon2-cffi). "
                    "Usa una app con Argon2 o archivos AUDX con kdf scrypt."
                )
            return hash_secret_raw(
                secret=password.encode("utf-8"),
                salt=salt,
                time_cost=int(kdf_params.get("time_cost", self.time_cost)),
                memory_cost=int(kdf_params.get("memory_cost_kib", self.memory_cost_kib)),
                parallelism=int(kdf_params.get("parallelism", self.parallelism)),
                hash_len=32,
                type=Type.ID,
            )
        if kdf_name == "scrypt":
            n = int(kdf_params.get("n", 2**14))
            r = int(kdf_params.get("r", 8))
            p = int(kdf_params.get("p", 1))
            return self._derive_key_scrypt(password=password, salt=salt, n=n, r=r, p=p)
        raise SecureAudioError("La derivacion de clave configurada no esta disponible.")

    @staticmethod
    def _derive_key_scrypt(password: str, salt: bytes, n: int, r: int, p: int) -> bytes:
        scrypt_fn = getattr(hashlib, "scrypt", None)
        if callable(scrypt_fn):
            return scrypt_fn(
                password.encode("utf-8"),
                salt=salt,
                n=n,
                r=r,
                p=p,
                dklen=32,
                maxmem=0,
            )

        # Some macOS system Pythons do not expose hashlib.scrypt.
        kdf = Scrypt(salt=salt, length=32, n=n, r=r, p=p)
        return kdf.derive(password.encode("utf-8"))

    @staticmethod
    def _canonical_json(data: dict[str, Any]) -> bytes:
        return json.dumps(data, ensure_ascii=True, separators=(",", ":"), sort_keys=True).encode("utf-8")

    @staticmethod
    def _extract_audio_metadata(source: Path) -> dict[str, Any]:
        metadata: dict[str, Any] = {
            "original_name": source.stem,
            "track_title": source.stem,
            "artist": "",
            "album": "",
            "duration_seconds": 0.0,
        }

        audio = MutagenFile(source)
        if audio is not None:
            if hasattr(audio, "info") and getattr(audio.info, "length", None) is not None:
                metadata["duration_seconds"] = float(audio.info.length)
            tags = getattr(audio, "tags", None)
            if tags:
                metadata["track_title"] = _read_tag(tags, ("TIT2", "title"), source.stem)
                metadata["artist"] = _read_tag(tags, ("TPE1", "artist"), "")
                metadata["album"] = _read_tag(tags, ("TALB", "album"), "")
        return metadata


def _read_tag(tags: Any, names: tuple[str, ...], default: str) -> str:
    for name in names:
        value = tags.get(name)
        if value is None:
            continue
        if isinstance(value, list) and value:
            return str(value[0])
        text = getattr(value, "text", None)
        if text:
            return str(text[0])
        return str(value)
    return default

