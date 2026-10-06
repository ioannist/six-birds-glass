from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


def _load_checker():
    script_path = Path(__file__).resolve().parents[1] / "experiments" / "check_bridges.py"
    spec = importlib.util.spec_from_file_location("check_bridges", script_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


CHECKER = _load_checker()
BRIDGE_PATHS = CHECKER.BRIDGE_PATHS
MANDATORY_NONCLAIMS = CHECKER.MANDATORY_NONCLAIMS
_artifact_hashes = CHECKER._artifact_hashes
check_all = CHECKER.check_all
validate_bridge = CHECKER.validate_bridge


def test_all_bridge_records_validate() -> None:
    result = check_all()
    assert result.ok, result.errors


def test_bridge_hashes_resolve_to_existing_artifacts() -> None:
    artifact_hashes = _artifact_hashes()
    for path in BRIDGE_PATHS:
        bridge = json.loads(path.read_text(encoding="utf-8"))
        for entry in bridge["level_map"]:
            assert entry["formal_artifact_hash"] in artifact_hashes
            assert artifact_hashes[entry["formal_artifact_hash"]].exists()


def test_bridge_nonclaims_are_complete() -> None:
    for path in BRIDGE_PATHS:
        bridge = json.loads(path.read_text(encoding="utf-8"))
        assert MANDATORY_NONCLAIMS.issubset(bridge["suppressed_structure_nonclaims"])


def test_bridge_denylist_rejects_bad_record(tmp_path: Path) -> None:
    bridge = json.loads(BRIDGE_PATHS[0].read_text(encoding="utf-8"))
    bridge["level_map"][0]["measured_structure"] = "this realizes the formal object"
    bad_path = tmp_path / "bad_bridge.json"
    bad_path.write_text(json.dumps(bridge), encoding="utf-8")

    errors = validate_bridge(bad_path, artifact_hashes=_artifact_hashes())
    assert any("denylisted phrase" in error for error in errors)
