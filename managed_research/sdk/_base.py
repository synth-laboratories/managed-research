"""Shared base for SDK namespace wrappers."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from managed_research.sdk.client import SmrControlClient


class _ClientNamespace:
    def __init__(self, client: SmrControlClient) -> None:
        self._client = client


__all__ = ["_ClientNamespace"]
