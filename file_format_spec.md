# File Format Specification: `.audx`

## Purpose

`.audx` is a proprietary encrypted container for audio payloads, currently focused on MP3 content.

## Endianness

All fixed-width integer fields use big-endian encoding.

## Layout

```text
+----------------------+----------------------------------+
| Field                | Size                             |
+----------------------+----------------------------------+
| Magic                | 8 bytes                          |
| Version              | 1 byte                           |
| Header length        | 4 bytes                          |
| Header JSON          | variable                         |
| Ciphertext blob      | remaining bytes                  |
+----------------------+----------------------------------+
```

## Magic

ASCII bytes:

```text
AUDXFILE
```

## Version

Current version:

```text
0x01
```

## Header JSON

UTF-8 encoded JSON with canonical compact serialization.

Required fields:

- `alg`: `"AES-256-GCM"`
- `kdf`: `"Argon2id"` or `"scrypt"`
- `kdf_params`: object containing the parameters used for the selected KDF
- `nonce_b64`: base64 nonce for AES-GCM, 12 bytes raw
- `salt_b64`: base64 salt for Argon2id, 16 bytes raw
- `meta_len`: integer length of encrypted metadata prefix after decryption
- `content_type`: `"audio/mpeg"`
- `original_ext`: `".mp3"`
- `created_utc`: ISO-8601 UTC timestamp

Optional fields:

- `original_name`: original stem without path
- `track_title`
- `artist`
- `album`
- `duration_seconds`

## Plaintext Before Encryption

Before encryption, the plaintext is assembled as:

```text
[metadata_json_utf8][raw_audio_bytes]
```

Where:

- `metadata_json_utf8` is compact UTF-8 JSON
- its byte length is stored in `meta_len`

## Ciphertext

- Produced by AES-256-GCM over the full plaintext blob
- Additional authenticated data is the exact serialized header JSON bytes
- GCM authentication tag is appended by the library as part of the ciphertext blob

## Validation Rules

- Magic must match exactly
- Version must be supported
- Header length must be within sane bounds
- JSON must decode cleanly
- `alg` and `kdf` must match supported values
- `nonce_b64` and `salt_b64` lengths must match expected raw sizes
- `meta_len` must be non-negative and smaller than decrypted plaintext size
- `original_ext` must be `.mp3`
- Decryption failures are treated as integrity/authentication failures

## Security Notes

- Every file uses a fresh random salt and nonce
- The encryption key is derived from the user passphrase and per-file salt using Argon2id where available, otherwise scrypt
- Header fields are authenticated through AES-GCM AAD
- Payload is never trusted without successful authentication
