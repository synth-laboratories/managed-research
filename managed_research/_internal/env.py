"""Environment and local-config helpers."""

from __future__ import annotations

import json
import os
from pathlib import Path


def _read_json_object(path: Path) -> dict[str, object]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return payload if isinstance(payload, dict) else {}


def config_search_paths() -> tuple[Path, ...]:
    home = Path.home()
    return (
        home / ".synth_ai" / "config.json",
        home / ".config" / "synth" / "config.json",
    )


def get_api_key(env_key: str = "SYNTH_API_KEY", required: bool = True) -> str | None:
    """Resolve the API key from environment or known local Synth config files."""

    value = str(os.getenv(env_key) or "").strip()
    if value:
        return value
    for path in config_search_paths():
        payload = _read_json_object(path)
        candidate = payload.get(env_key)
        if isinstance(candidate, str) and candidate.strip():
            return candidate.strip()
    if required:
        raise ValueError(f"{env_key} is required (set {env_key} or add it to local Synth config)")
    return None


__all__ = ["config_search_paths", "get_api_key"]
