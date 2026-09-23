"""Check the GT6 filing artifact and recompute its verdict."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from experiments.build_gt6_filing import TEN_NONCLAIMS  # noqa: E402

from sixbirds_glass.extension.filing import (  # noqa: E402
    EXCLUSION_CHECKS,
    gate_table_from_payload,
    recompute_verdict,
    validate_gate_table,
)
from sixbirds_glass.extension.strict import artifact_sha256  # noqa: E402

AUDIT_PATH = REPO_ROOT / "artifacts" / "gt6_bridge" / "audit.json"


def main(path: Path = AUDIT_PATH) -> int:
    """CLI entry point returning a process status code."""

    ok, messages = check_file(path)
    for message in messages:
        print(message)
    if ok:
        print("PASS gt6_filing")
        return 0
    print("FAIL gt6_filing")
    return 1


def check_file(path: Path) -> tuple[bool, list[str]]:
    """Validate one filing artifact."""

    messages: list[str] = []
    try:
        artifact = json.loads(path.read_text(encoding="utf-8"))
        Draft202012Validator(_schema("artifact_envelope.schema.json")).validate(artifact)
        _check_nonclaims(artifact)
        _check_citations(artifact)
        _check_bridge_records(artifact)
        _check_exclusion_ledger(artifact)
        _check_disintegration(artifact)
        _check_verdict(artifact)
    except Exception as exc:
        messages.append(str(exc))
        return False, messages
    messages.append(f"checked {path}")
    return True, messages


def _check_nonclaims(artifact: dict[str, Any]) -> None:
    present = set(artifact["nonclaims"])
    missing = set(TEN_NONCLAIMS) - present
    if missing:
        raise ValueError(f"missing required nonclaims: {sorted(missing)}")


def _check_citations(artifact: dict[str, Any]) -> None:
    for citation in artifact["payload"]["citations"]:
        path = _resolve_repo_path(citation["artifact_path"])
        if not path.is_file():
            raise ValueError(f"cited artifact does not exist: {path}")
        observed = artifact_sha256(path)
        if observed != citation["sha256"]:
            raise ValueError(
                f"hash mismatch for {path}: expected {citation['sha256']}, got {observed}"
            )


def _resolve_repo_path(path_text: str) -> Path:
    path = Path(path_text)
    return path if path.is_absolute() else REPO_ROOT / path


def _check_verdict(artifact: dict[str, Any]) -> None:
    gate_table = gate_table_from_payload(artifact["payload"]["gate_table"])
    validate_gate_table(gate_table)
    recomputed = recompute_verdict(gate_table)
    stored = artifact["payload"]["verdict"]
    if recomputed != stored:
        raise ValueError(f"stored verdict {stored!r} disagrees with recomputed {recomputed!r}")


def _check_bridge_records(artifact: dict[str, Any]) -> None:
    bridge_records = artifact["payload"].get("bridge_records")
    if not isinstance(bridge_records, list) or len(bridge_records) != 1:
        raise ValueError("filing must contain exactly one bridge record")
    top_gate_table = artifact["payload"]["gate_table"]
    bridge_gate_table = bridge_records[0].get("GateResults")
    if bridge_gate_table != top_gate_table:
        raise ValueError("bridge GateResults differ from top-level gate_table")
    validate_gate_table(gate_table_from_payload(bridge_gate_table))
    required_fields = {
        "id",
        "T0",
        "T1",
        "carrier_S",
        "O0",
        "O1",
        "pi0",
        "pi1",
        "L",
        "V",
        "Theta",
        "A",
        "delta",
        "GateResults",
        "N",
        "HostTag",
        "lambda_prom",
    }
    observed = set(bridge_records[0])
    missing = sorted(required_fields - observed)
    extra = sorted(observed - required_fields)
    if missing or extra:
        raise ValueError(f"bridge record field mismatch: missing={missing}, extra={extra}")


def _check_exclusion_ledger(artifact: dict[str, Any]) -> None:
    entries = artifact["payload"]["adm_domain"].get("exclusion_checks")
    if not isinstance(entries, list):
        raise ValueError("AdmDomain exclusion_checks must be a list")
    names = [entry.get("check") for entry in entries]
    duplicates = sorted({name for name in names if names.count(name) > 1})
    if duplicates:
        raise ValueError(f"duplicate exclusion checks: {duplicates}")
    expected = set(EXCLUSION_CHECKS)
    observed = set(names)
    missing = sorted(expected - observed)
    extra = sorted(observed - expected)
    if missing or extra:
        raise ValueError(f"exclusion-check mismatch: missing={missing}, extra={extra}")
    violated = [entry["check"] for entry in entries if entry.get("violated") is not False]
    if violated:
        raise ValueError(f"AdmDomain exclusion checks violated: {violated}")


def _check_disintegration(artifact: dict[str, Any]) -> None:
    if artifact["payload"]["disintegration"].get("passes_threshold") is not True:
        raise ValueError("disintegration gap does not pass the declared threshold")


def _schema(filename: str) -> dict[str, Any]:
    path = REPO_ROOT / "design" / "schemas" / filename
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TypeError(f"{path} did not contain a JSON object")
    return data


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1]) if len(sys.argv) > 1 else AUDIT_PATH))
