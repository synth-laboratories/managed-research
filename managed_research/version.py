"""Package version derived from package metadata or pyproject.toml."""

from __future__ import annotations

from importlib import metadata as _metadata
from importlib.metadata import PackageNotFoundError
from pathlib import Path

try:
    __version__ = _metadata.version("managed-research")
except PackageNotFoundError:
    try:
        import tomllib as _toml
    except ModuleNotFoundError:  # pragma: no cover
        import tomli as _toml  # type: ignore[no-redef]

    try:
        pyproject_path = Path(__file__).resolve().parents[1] / "pyproject.toml"
        with pyproject_path.open("rb") as fh:
            _pyproject = _toml.load(fh)
        __version__ = str(_pyproject["project"]["version"])
    except Exception:
        __version__ = "0.0.0.dev0"

__all__ = ["__version__"]
