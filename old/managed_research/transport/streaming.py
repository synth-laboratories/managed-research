"""Helpers for previewing streamed/binary payloads."""

from __future__ import annotations

import base64
from dataclasses import dataclass


@dataclass(frozen=True)
class BinaryPayloadPreview:
    encoding: str
    content: str
    content_bytes_returned: int
    content_bytes_total: int
    truncated: bool


def preview_binary_payload(payload: bytes, *, max_bytes: int) -> BinaryPayloadPreview:
    """Return a UTF-8 preview when possible, otherwise base64-encode the bytes."""
    if max_bytes <= 0:
        raise ValueError("max_bytes must be a positive integer")

    full_size = len(payload)
    truncated = full_size > max_bytes
    preview_bytes = payload[:max_bytes] if truncated else payload

    try:
        content = preview_bytes.decode("utf-8")
        encoding = "utf-8"
    except UnicodeDecodeError:
        content = base64.b64encode(preview_bytes).decode("ascii")
        encoding = "base64"

    return BinaryPayloadPreview(
        encoding=encoding,
        content=content,
        content_bytes_returned=len(preview_bytes),
        content_bytes_total=full_size,
        truncated=truncated,
    )


__all__ = ["BinaryPayloadPreview", "preview_binary_payload"]
