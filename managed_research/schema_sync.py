"""Schema sync helpers for the rewritten package surface."""

from __future__ import annotations

import shutil
from pathlib import Path


def sync_public_schemas(
    *,
    source_dir: Path | None = None,
    destination_dir: Path | None = None,
) -> list[Path]:
    """Copy quarantined legacy schemas into the new generated schema folder."""

    package_root = Path(__file__).resolve().parent
    repo_root = package_root.parent
    source = source_dir or (repo_root / "old" / "schemas" / "generated")
    destination = destination_dir or (package_root / "models" / "generated")
    copied: list[Path] = []
    if not source.exists():
        return copied
    destination.mkdir(parents=True, exist_ok=True)
    for path in sorted(source.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(source)
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
        copied.append(target)
    return copied


__all__ = ["sync_public_schemas"]
