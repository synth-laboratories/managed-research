"""Sync exported SMR public schema artifacts into the public repo."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

DEFAULT_SCHEMA_DEST = Path("schemas/generated/v1")


class SchemaSyncError(RuntimeError):
    """Raised when schema sync input is missing or invalid."""


def _normalize_source(source: str | os.PathLike[str]) -> Path:
    path = Path(source).expanduser()
    if not path.exists():
        raise SchemaSyncError(f"Schema source does not exist: {path}")
    return path


def _json_sources(source: Path) -> list[Path]:
    if source.is_file():
        if source.suffix != ".json":
            raise SchemaSyncError(f"Schema source file must be JSON: {source}")
        return [source]

    candidates = sorted(path for path in source.iterdir() if path.is_file() and path.suffix == ".json")
    if not candidates:
        raise SchemaSyncError(f"Schema source directory has no JSON files: {source}")
    return candidates


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SchemaSyncError(f"Invalid JSON in schema artifact {path}: {exc}") from exc


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def sync_public_schemas(
    source: str | os.PathLike[str],
    destination: str | os.PathLike[str],
) -> list[Path]:
    """Copy JSON schema artifacts into the repo with normalized formatting."""
    source_path = _normalize_source(source)
    destination_path = Path(destination).expanduser()
    destination_path.mkdir(parents=True, exist_ok=True)

    written_paths: list[Path] = []
    expected_names: set[str] = set()
    for schema_path in _json_sources(source_path):
        payload = _load_json(schema_path)
        target_path = destination_path / schema_path.name
        _write_json(target_path, payload)
        expected_names.add(schema_path.name)
        written_paths.append(target_path)

    for existing_path in destination_path.glob("*.json"):
        if existing_path.name not in expected_names:
            existing_path.unlink()

    return sorted(written_paths)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source",
        help="Path to an exported schema JSON file or directory of JSON files.",
    )
    parser.add_argument(
        "--dest",
        help="Destination directory for normalized schema artifacts.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    try:
        args = parse_args(argv)
        repo_root = Path(__file__).resolve().parents[1]

        source = args.source or os.getenv("MANAGED_RESEARCH_SCHEMA_SOURCE")
        if not source:
            raise SchemaSyncError(
                "No schema source configured. Provide --source or set MANAGED_RESEARCH_SCHEMA_SOURCE."
            )

        destination = args.dest or str(repo_root / DEFAULT_SCHEMA_DEST)
        written = sync_public_schemas(source, destination)
        print(f"Synced {len(written)} schema artifact(s) into {Path(destination)}")
        return 0
    except SchemaSyncError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


__all__ = ["DEFAULT_SCHEMA_DEST", "SchemaSyncError", "main", "parse_args", "sync_public_schemas"]
