from __future__ import annotations

import unittest

from secure_audio_app.crypto import AuthenticationError, AudxCrypto, InvalidContainerError


class CryptoTests(unittest.TestCase):
    def test_encrypt_decrypt_round_trip(self) -> None:
        crypto = AudxCrypto(time_cost=1, memory_cost_kib=8192, parallelism=1)
        metadata = {
            "original_name": "track01",
            "track_title": "Track 01",
            "artist": "Test Artist",
            "album": "Album",
            "duration_seconds": 12.5,
        }
        audio_bytes = b"ID3" + b"\x00" * 1024

        encrypted = crypto.encrypt_bytes(audio_bytes, password="correct horse battery", metadata=metadata)
        decrypted = crypto.decrypt_bytes(encrypted, password="correct horse battery")

        self.assertEqual(bytes(decrypted.audio_bytes), audio_bytes)
        self.assertEqual(decrypted.metadata["track_title"], "Track 01")

    def test_new_container_uses_scrypt_kdf(self) -> None:
        crypto = AudxCrypto(time_cost=1, memory_cost_kib=8192, parallelism=1)
        encrypted = crypto.encrypt_bytes(
            b"ID3" + b"z" * 64,
            password="correct horse battery",
            metadata={"original_name": "x", "track_title": "x", "artist": "", "album": "", "duration_seconds": 1.0},
        )
        header, _, _ = crypto.parse_container(encrypted)
        self.assertEqual(header["kdf"], "scrypt")
        self.assertEqual(header["kdf_params"], {"n": 2**14, "r": 8, "p": 1})
    def test_tampered_ciphertext_fails_authentication(self) -> None:
        crypto = AudxCrypto(time_cost=1, memory_cost_kib=8192, parallelism=1)
        encrypted = crypto.encrypt_bytes(
            b"ID3" + b"a" * 128,
            password="correct horse battery",
            metadata={"original_name": "x", "track_title": "x", "artist": "", "album": "", "duration_seconds": 1.0},
        )
        tampered = bytearray(encrypted)
        tampered[-1] ^= 0x01

        with self.assertRaises(AuthenticationError):
            crypto.decrypt_bytes(bytes(tampered), password="correct horse battery")

    def test_invalid_magic_is_rejected(self) -> None:
        crypto = AudxCrypto(time_cost=1, memory_cost_kib=8192, parallelism=1)
        with self.assertRaises(InvalidContainerError):
            crypto.parse_container(b"BADXFILE\x01\x00\x00\x00\x01{}")


if __name__ == "__main__":
    unittest.main()

