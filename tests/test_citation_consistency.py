from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
JSON_ROOTS = (REPO_ROOT / "artifacts", REPO_ROOT / "bridges", REPO_ROOT / "registry")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
PATH_RE = re.compile(
    r"(artifacts/[^\s,;()]+?\.json|bridges/[^\s,;()]+?\.json|registry/[^\s,;()]+?\.json)"
)
PREDICTIONS_PATH = REPO_ROOT / "registry" / "predictions_f5e2a3332a2191a2.json"
READOUTS_PATH = REPO_ROOT / "registry" / "readouts.json"
SCORING_SCRIPT_PATH = REPO_ROOT / "experiments" / "score_transfer.py"


def test_repo_wide_hash_citations_resolve_current_bytes() -> None:
    checks: list[tuple[str, str, str, str]] = []

    for root in JSON_ROOTS:
        for source in sorted(root.rglob("*.json")):
            _walk_json_for_citations(source, _load_json(source), checks)

    predictions = _load_json(PREDICTIONS_PATH)
    _add_check(
        checks,
        "registry/predictions:source_artifact_hash",
        REPO_ROOT / "artifacts" / "gt7_constants" / "east_reference.json",
        predictions["source_artifact_hash"],
    )
    _add_check(
        checks,
        "registry/predictions:readouts_freeze_hash",
        READOUTS_PATH,
        predictions["readouts_freeze_hash"],
        mode="content_hash",
    )
    _add_check(
        checks,
        "registry/predictions:scoring_script_hash",
        SCORING_SCRIPT_PATH,
        predictions["scoring_script_hash"],
    )

    scores = _load_json(REPO_ROOT / "artifacts" / "gt7_constants" / "gt7_transfer_scores.json")
    _add_check(
        checks,
        "gt7_transfer_scores:predictions_source_hash",
        PREDICTIONS_PATH,
        scores["predictions_source_hash"],
    )
    _add_check(
        checks,
        "gt7_transfer_scores:scoring_script_hash",
        SCORING_SCRIPT_PATH,
        scores["scoring_script_hash"],
    )

    for registry_path in (READOUTS_PATH, PREDICTIONS_PATH):
        registry = _load_json(registry_path)
        _add_check(
            checks,
            f"{_relative(registry_path)}:content_hash",
            registry_path,
            registry["content_hash"],
            mode="content_hash",
        )

    expected_freeze_refs = {
        _content_hash(READOUTS_PATH),
        _content_hash(PREDICTIONS_PATH),
    }
    for artifact_path in (
        REPO_ROOT / "artifacts" / "gt7_constants" / "fa_target.json",
        REPO_ROOT / "artifacts" / "gt7_constants" / "trap_target.json",
    ):
        freeze_refs = set(_load_json(artifact_path).get("freeze_refs", []))
        for expected in expected_freeze_refs:
            checks.append(
                (f"{_relative(artifact_path)}:freeze_refs", "content_hash", expected, expected)
            )
            assert expected in freeze_refs

    assert len(checks) == 32
    assert all(expected == observed for _, _, expected, observed in checks)


def _walk_json_for_citations(
    source: Path, obj: Any, checks: list[tuple[str, str, str, str]], locator: str = ""
) -> None:
    if isinstance(obj, dict):
        path_value = next(
            (
                obj.get(key)
                for key in ("artifact_path", "path")
                if isinstance(obj.get(key), str) and obj.get(key).endswith(".json")
            ),
            None,
        )
        if isinstance(path_value, str):
            for hash_key in ("sha256", "artifact_hash"):
                expected = obj.get(hash_key)
                if isinstance(expected, str) and HEX64.match(expected):
                    _add_check(
                        checks,
                        _locator(source, locator, hash_key),
                        _resolve_relative(path_value),
                        expected,
                    )

        formal_hash = obj.get("formal_artifact_hash")
        formal_object = obj.get("formal_object")
        if isinstance(formal_hash, str) and isinstance(formal_object, str):
            match = PATH_RE.search(formal_object)
            if match and HEX64.match(formal_hash):
                _add_check(
                    checks,
                    _locator(source, locator, "formal_artifact_hash"),
                    _resolve_relative(match.group(1)),
                    formal_hash,
                )

        for key, value in obj.items():
            child = f"{locator}.{key}" if locator else key
            _walk_json_for_citations(source, value, checks, child)
    elif isinstance(obj, list):
        for index, value in enumerate(obj):
            _walk_json_for_citations(source, value, checks, f"{locator}[{index}]")


def _add_check(
    checks: list[tuple[str, str, str, str]],
    source: str,
    target: Path,
    expected: str,
    *,
    mode: str = "file_hash",
) -> None:
    assert not target.is_absolute() or target.is_relative_to(REPO_ROOT)
    assert target.is_file(), f"{source} targets missing file {target}"
    observed = _content_hash(target) if mode == "content_hash" else _sha256(target)
    checks.append((source, _relative(target), expected, observed))


def _load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    return data


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _content_hash(path: Path) -> str:
    data = _load_json(path)
    body = dict(data)
    body.pop("content_hash", None)
    blob = json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode(
        "utf-8"
    )
    return hashlib.sha256(blob).hexdigest()


def _resolve_relative(path_text: str) -> Path:
    path = Path(path_text)
    assert not path.is_absolute()
    return REPO_ROOT / path


def _relative(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


def _locator(source: Path, locator: str, key: str) -> str:
    suffix = f"{locator}.{key}" if locator else key
    return f"{_relative(source)}:{suffix}"
