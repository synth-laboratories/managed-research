import json
from pathlib import Path

import pytest
from managed_research.schema_sync import SchemaSyncError, main, sync_public_schemas


def test_sync_public_schemas_copies_and_normalizes_json(tmp_path: Path) -> None:
    source_dir = tmp_path / "source"
    source_dir.mkdir()
    (source_dir / "projects.json").write_text(
        json.dumps({"title": "Projects", "type": "object"}),
        encoding="utf-8",
    )
    (source_dir / "runs.json").write_text(
        json.dumps({"title": "Runs", "type": "object"}),
        encoding="utf-8",
    )

    destination_dir = tmp_path / "dest"
    destination_dir.mkdir()
    stale_path = destination_dir / "stale.json"
    stale_path.write_text("{}", encoding="utf-8")

    written = sync_public_schemas(source_dir, destination_dir)

    assert [path.name for path in written] == ["projects.json", "runs.json"]
    assert stale_path.exists() is False
    assert json.loads((destination_dir / "projects.json").read_text(encoding="utf-8")) == {
        "title": "Projects",
        "type": "object",
    }


def test_sync_public_schemas_rejects_missing_source(tmp_path: Path) -> None:
    with pytest.raises(SchemaSyncError, match="Schema source does not exist"):
        sync_public_schemas(tmp_path / "missing", tmp_path / "dest")


def test_sync_public_schemas_rejects_invalid_json(tmp_path: Path) -> None:
    source_dir = tmp_path / "source"
    source_dir.mkdir()
    (source_dir / "broken.json").write_text("{not valid json", encoding="utf-8")

    with pytest.raises(SchemaSyncError, match="Invalid JSON"):
        sync_public_schemas(source_dir, tmp_path / "dest")


def test_schema_sync_main_reports_missing_source_cleanly(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.delenv("MANAGED_RESEARCH_SCHEMA_SOURCE", raising=False)

    exit_code = main([])

    captured = capsys.readouterr()
    assert exit_code == 2
    assert "No schema source configured" in captured.err
