"""Auth and transport helpers for the public Managed Research package."""

from __future__ import annotations

import base64
import json
import os
from pathlib import Path
from urllib.parse import urlparse, urlunparse

from nacl.public import PublicKey, SealedBox

BACKEND_URL_BASE = (os.getenv("SYNTH_BACKEND_URL") or "https://api.usesynth.ai").strip()


def _read_json_object(path: Path) -> dict[str, object]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return raw if isinstance(raw, dict) else {}


def _config_search_paths() -> list[Path]:
    home = Path.home()
    return [
        home / ".synth_ai" / "config.json",
        home / ".config" / "synth" / "config.json",
    ]


def get_api_key(env_key: str = "SYNTH_API_KEY", required: bool = True) -> str | None:
    """Resolve the Synth API key from environment or local config."""
    value = (os.getenv(env_key) or "").strip()
    if value:
        return value

    for path in _config_search_paths():
        payload = _read_json_object(path)
        config_value = payload.get(env_key)
        if isinstance(config_value, str) and config_value.strip():
            return config_value.strip()

    if required:
        raise ValueError(f"{env_key} is required (set {env_key} or store it in local Synth config)")
    return None


def _strip_terminal_segment(path: str, segment: str) -> str:
    trimmed = path.rstrip("/")
    if trimmed.endswith(segment):
        return trimmed[: -len(segment)].rstrip("/")
    return trimmed


def normalize_backend_base(url: str) -> str:
    """Normalize a backend URL down to the service base."""
    parsed = urlparse(url.strip())
    path = _strip_terminal_segment(parsed.path, "/v1")
    path = _strip_terminal_segment(path, "/api")
    normalized = parsed._replace(path=path.rstrip("/"), query="", fragment="")
    return urlunparse(normalized)


def encrypt_for_backend(pubkey_b64: str, secret: str | bytes) -> str:
    """Encrypt a provider key using the backend's sealed-box public key."""
    if isinstance(secret, bytes):
        secret = secret.decode("utf-8")
    try:
        pubkey_raw = base64.b64decode(pubkey_b64, validate=True)
    except Exception as exc:
        raise RuntimeError("Invalid backend public key (not base64)") from exc
    box = SealedBox(PublicKey(pubkey_raw))
    ciphertext = box.encrypt(secret.encode("utf-8"))
    return base64.b64encode(ciphertext).decode("utf-8")
