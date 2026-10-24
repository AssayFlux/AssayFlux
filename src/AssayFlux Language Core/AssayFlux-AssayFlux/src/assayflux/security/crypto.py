"""Authenticated encryption helpers for AssayFlux data.

Uses AES-256-GCM. Callers own key storage and rotation; this module never
writes keys to disk or logs them. Encryption is not an execution sandbox.
"""
from __future__ import annotations

import base64
import binascii
import json
import secrets
from typing import Any

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

_KEY_BYTES = 32
_NONCE_BYTES = 12
_VERSION = 1
_PREFIX = "afenc:v1:"

class EncryptionError(ValueError):
    """Malformed encrypted envelope or authentication failure."""

def generate_key() -> bytes:
    """Generate a fresh 256-bit AES key. Store it in a proper secret manager."""
    return AESGCM.generate_key(bit_length=256)

def _validate_key(key: bytes) -> None:
    if not isinstance(key, bytes) or len(key) != _KEY_BYTES:
        raise ValueError("AES-256-GCM key must be exactly 32 bytes")

def encrypt_bytes(plaintext: bytes, key: bytes, *, associated_data: bytes = b"") -> str:
    """Encrypt bytes into a versioned, URL-safe, authenticated envelope."""
    _validate_key(key)
    if not isinstance(plaintext, bytes) or not isinstance(associated_data, bytes):
        raise TypeError("plaintext and associated_data must be bytes")
    nonce = secrets.token_bytes(_NONCE_BYTES)
    ciphertext = AESGCM(key).encrypt(nonce, plaintext, associated_data)
    envelope = {"v": _VERSION, "n": base64.urlsafe_b64encode(nonce).decode("ascii"),
                "c": base64.urlsafe_b64encode(ciphertext).decode("ascii")}
    encoded = json.dumps(envelope, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return _PREFIX + base64.urlsafe_b64encode(encoded).decode("ascii")

def decrypt_bytes(token: str, key: bytes, *, associated_data: bytes = b"") -> bytes:
    """Authenticate and decrypt an envelope; fail closed on invalid input."""
    _validate_key(key)
    if not isinstance(token, str) or not token.startswith(_PREFIX):
        raise EncryptionError("Unsupported or malformed encrypted envelope")
    if not isinstance(associated_data, bytes):
        raise TypeError("associated_data must be bytes")
    try:
        raw = base64.b64decode(token[len(_PREFIX):], altchars=b"-_", validate=True)
        envelope: Any = json.loads(raw.decode("utf-8"))
        if not isinstance(envelope, dict) or set(envelope) != {"v", "n", "c"}:
            raise EncryptionError("Malformed encrypted envelope fields")
        if envelope["v"] != _VERSION:
            raise EncryptionError("Unsupported encrypted envelope version")
        nonce = base64.b64decode(envelope["n"], altchars=b"-_", validate=True)
        ciphertext = base64.b64decode(envelope["c"], altchars=b"-_", validate=True)
        if len(nonce) != _NONCE_BYTES or len(ciphertext) < 16:
            raise EncryptionError("Malformed encrypted envelope lengths")
        return AESGCM(key).decrypt(nonce, ciphertext, associated_data)
    except (InvalidTag, UnicodeDecodeError, json.JSONDecodeError, binascii.Error, TypeError, KeyError) as exc:
        raise EncryptionError("Encrypted data failed validation or authentication") from exc

def encrypt_text(plaintext: str, key: bytes, *, associated_data: bytes = b"") -> str:
    """UTF-8 encode and encrypt text."""
    if not isinstance(plaintext, str):
        raise TypeError("plaintext must be a string")
    return encrypt_bytes(plaintext.encode("utf-8"), key, associated_data=associated_data)

def decrypt_text(token: str, key: bytes, *, associated_data: bytes = b"") -> str:
    """Authenticate, decrypt and UTF-8 decode text."""
    try:
        return decrypt_bytes(token, key, associated_data=associated_data).decode("utf-8")
    except UnicodeDecodeError as exc:
        raise EncryptionError("Decrypted content is not valid UTF-8 text") from exc
