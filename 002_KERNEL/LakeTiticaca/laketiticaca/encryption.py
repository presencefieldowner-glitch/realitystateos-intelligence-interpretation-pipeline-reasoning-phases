"""
encryption.py — Symmetric encryption for data-at-rest / in-transit within the
Kernel AI's boundary (e.g. cached knowledge, tokens-in-flight). Uses AES-GCM
via the `cryptography` package — real, audited crypto, not a placeholder.
"""
from __future__ import annotations
import os
from dataclasses import dataclass

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


@dataclass(frozen=True)
class EncryptedPayload:
    nonce: bytes
    ciphertext: bytes

    def to_bytes(self) -> bytes:
        return self.nonce + self.ciphertext

    @staticmethod
    def from_bytes(data: bytes, nonce_len: int = 12) -> "EncryptedPayload":
        return EncryptedPayload(nonce=data[:nonce_len], ciphertext=data[nonce_len:])


def generate_key() -> bytes:
    return AESGCM.generate_key(bit_length=256)


def encrypt(plaintext: bytes, key: bytes, associated_data: bytes | None = None) -> EncryptedPayload:
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, plaintext, associated_data)
    return EncryptedPayload(nonce=nonce, ciphertext=ciphertext)


def decrypt(payload: EncryptedPayload, key: bytes, associated_data: bytes | None = None) -> bytes:
    aesgcm = AESGCM(key)
    return aesgcm.decrypt(payload.nonce, payload.ciphertext, associated_data)


def encrypt_str(plaintext: str, key: bytes) -> bytes:
    return encrypt(plaintext.encode("utf-8"), key).to_bytes()


def decrypt_str(data: bytes, key: bytes) -> str:
    return decrypt(EncryptedPayload.from_bytes(data), key).decode("utf-8")
