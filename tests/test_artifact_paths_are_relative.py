from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def test_json_artifact_paths_are_repo_relative() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    root_text = str(repo_root)

    offenders: list[str] = []
    for base in ("artifacts", "bridges", "registry"):
        for path in sorted((repo_root / base).rglob("*.json")):
            text = path.read_text(encoding="utf-8")
            if root_text in text:
                offenders.append(f"{path.relative_to(repo_root)} contains repo root literal")
            data = json.loads(text)
            offenders.extend(
                f"{path.relative_to(repo_root)}:{location} has absolute path {value!r}"
                for location, value in _path_values(data)
                if Path(value).is_absolute()
            )

    assert offenders == []


def _path_values(value: Any, *, location: str = "$") -> list[tuple[str, str]]:
    if isinstance(value, dict):
        found: list[tuple[str, str]] = []
        for key, item in value.items():
            child_location = f"{location}.{key}"
            if isinstance(item, str) and key.endswith("_path"):
                found.append((child_location, item))
            else:
                found.extend(_path_values(item, location=child_location))
        return found
    if isinstance(value, list):
        found = []
        for index, item in enumerate(value):
            found.extend(_path_values(item, location=f"{location}[{index}]"))
        return found
    return []
