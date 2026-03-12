# Threat Model

## Goal

Make extraction of the original MP3 significantly harder and prevent casual copying. The goal is not absolute DRM.

## Assets to Protect

- Original MP3 content
- Encryption passwords
- Proprietary encrypted `.audx` files

## Assumptions

- The user controls the machine and runs the desktop application locally.
- Playback must occur fully offline.
- Attackers may have file-system access to encrypted files.

## Threats Addressed

### Offline file access

- An attacker obtains `.audx` files and attempts to recover the MP3 without the password.
- Mitigation:
  - AES-256-GCM
  - Argon2id with per-file salt
  - authenticated file structure

### Malformed or tampered container files

- An attacker modifies headers or ciphertext to crash or confuse the player.
- Mitigation:
  - strict header validation
  - bounds checks
  - authenticated decryption
  - defensive parsing

### Casual extraction from the application

- A user looks for a decrypted output or temp file.
- Mitigation:
  - no export feature
  - no plaintext cache
  - playback from memory only
  - buffer clearing where feasible

## Threats Not Fully Solved

### Live capture during playback

If audio can be heard, it can be captured:

- system loopback recording
- hooked audio APIs
- memory inspection
- kernel-level malware
- analog recording from speakers

No local desktop application can guarantee absolute prevention of copying once playback occurs.

### Reverse engineering

An attacker with time and tooling can inspect Python bytecode, hook process memory, or instrument VLC callbacks.

This project raises the difficulty but does not claim unbreakable DRM.

## Security Posture

This application is intended to:

- protect encrypted audio at rest
- reduce obvious plaintext exposure paths
- prevent casual duplication workflows

It is not intended to defend against:

- privileged malware
- forensic memory extraction
- determined reverse engineering teams
- compromised operating systems

## Operational Recommendations

- Use strong passphrases.
- Package with code signing where possible.
- Avoid running on untrusted machines.
- Keep the app and bundled dependencies updated.
