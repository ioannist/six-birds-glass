from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path
from typing import Any

from sixbirds_glass.io.config import canonical_json_bytes

REPO_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = REPO_ROOT / "paper" / "evidence_manifest.json"
HEX64 = re.compile(r"^[0-9a-f]{64}$")
PATH_RE = re.compile(
    r"(artifacts/[^\s,;()]+?\.json|bridges/[^\s,;()]+?\.json|registry/[^\s,;()]+?\.json)"
)


def test_evidence_manifest_is_fresh_against_builder() -> None:
    assert canonical_json_bytes(_load_manifest()) == canonical_json_bytes(
        _builder().build_manifest()
    )


def test_evidence_manifest_entries_resolve_current_bytes() -> None:
    for entry in _load_manifest()["entries"]:
        path = REPO_ROOT / entry["path"]
        data = path.read_bytes()
        assert path.is_file()
        assert entry["bytes"] == len(data)
        assert entry["sha256"] == hashlib.sha256(data).hexdigest()


def test_evidence_manifest_complete_no_orphans() -> None:
    manifest_paths = {entry["path"] for entry in _load_manifest()["entries"]}
    scanned_paths = {path.as_posix() for path in _independent_scan_paths()}

    assert manifest_paths == scanned_paths


def test_evidence_manifest_self_hash_verifies() -> None:
    manifest = _load_manifest()
    expected = manifest["content_hash"]
    body = dict(manifest)
    body.pop("content_hash")

    assert hashlib.sha256(canonical_json_bytes(body)).hexdigest() == expected


def test_evidence_manifest_builder_is_deterministic() -> None:
    builder = _builder()

    first = builder.build_manifest()
    second = builder.build_manifest()

    assert canonical_json_bytes(first) == canonical_json_bytes(second)


def test_citation_targets_are_manifested() -> None:
    manifest_paths = {entry["path"] for entry in _load_manifest()["entries"]}
    citation_targets = _citation_targets()

    assert citation_targets
    assert citation_targets <= manifest_paths


def _load_manifest() -> dict[str, Any]:
    data = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    return data


def _builder():
    script_path = REPO_ROOT / "experiments" / "build_evidence_manifest.py"
    spec = importlib.util.spec_from_file_location("build_evidence_manifest", script_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _independent_scan_paths() -> list[Path]:
    paths = [
        *_glob("artifacts/**/*.json"),
        *_glob("registry/*.json"),
        *_glob("bridges/*.json"),
        *_glob("lean/GlassWitness/*.lean"),
        *_glob("lean/HolonomyMemory/**/*.lean"),
        Path("lean/HolonomyMemory.lean"),
        Path("lean/lean-toolchain"),
        Path("lean/lakefile.toml"),
        Path("experiments/score_transfer.py"),
        Path("experiments/check_gt6_filing.py"),
        Path("experiments/check_bridges.py"),
    ]
    return sorted(path for path in set(paths) if (REPO_ROOT / path).is_file())


def _glob(pattern: str) -> list[Path]:
    return sorted(path.relative_to(REPO_ROOT) for path in REPO_ROOT.glob(pattern) if path.is_file())


def _citation_targets() -> set[str]:
    targets: set[str] = set()
    for root in (REPO_ROOT / "artifacts", REPO_ROOT / "bridges", REPO_ROOT / "registry"):
        for source in sorted(root.rglob("*.json")):
            _walk_json_for_citation_targets(json.loads(source.read_text(encoding="utf-8")), targets)

    predictions = _load_json(REPO_ROOT / "registry" / "predictions_f5e2a3332a2191a2.json")
    targets.update(
        {
            "artifacts/gt7_constants/east_reference.json",
            "registry/readouts.json",
            "experiments/score_transfer.py",
        }
    )
    assert HEX64.match(predictions["source_artifact_hash"])
    assert HEX64.match(predictions["readouts_freeze_hash"])
    assert HEX64.match(predictions["scoring_script_hash"])

    scores = _load_json(REPO_ROOT / "artifacts" / "gt7_constants" / "gt7_transfer_scores.json")
    targets.update({"registry/predictions_f5e2a3332a2191a2.json", "experiments/score_transfer.py"})
    assert HEX64.match(scores["predictions_source_hash"])
    assert HEX64.match(scores["scoring_script_hash"])
    return targets


def _walk_json_for_citation_targets(obj: Any, targets: set[str]) -> None:
    if isinstance(obj, dict):
        path_value = next(
            (
                obj.get(key)
                for key in ("artifact_path", "path")
                if isinstance(obj.get(key), str) and obj.get(key).endswith(".json")
            ),
            None,
        )
        if isinstance(path_value, str) and (
            HEX64.match(str(obj.get("sha256", "")))
            or HEX64.match(str(obj.get("artifact_hash", "")))
        ):
            targets.add(path_value)

        formal_hash = obj.get("formal_artifact_hash")
        formal_object = obj.get("formal_object")
        if isinstance(formal_hash, str) and HEX64.match(formal_hash):
            if isinstance(formal_object, str) and (match := PATH_RE.search(formal_object)):
                targets.add(match.group(1))

        for value in obj.values():
            _walk_json_for_citation_targets(value, targets)
    elif isinstance(obj, list):
        for value in obj:
            _walk_json_for_citation_targets(value, targets)


def _load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    return data
