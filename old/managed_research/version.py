"""Package version helpers."""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("managed-research")
except PackageNotFoundError:
    __version__ = "0.1.0"
