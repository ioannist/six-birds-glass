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

from experiments.build_gt6_filing import (  # noqa: E402
    CITED_ARTIFACTS,
    TEN_NONCLAIMS,
    VERDICT_BASIS,
    build_artifact,
    gate_table_from_certificate,
)

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
        verdict = json.loads(path.read_text())["payload"]["verdict"]
        print(f"PASS gt6_filing_record verdict={verdict}")
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
        _check_scientific_bridge(artifact)
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
    paths = [row["artifact_path"] for row in artifact["payload"]["citations"]]
    if len(paths) != len(set(paths)) or set(paths) != set(CITED_ARTIFACTS):
        raise ValueError("citation set differs from the declared evidence set")
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
    if any(entry.get("violated") not in (None, False, True) for entry in entries):
        raise ValueError("malformed exclusion value")
    violated = [entry["check"] for entry in entries if entry.get("violated") is True]
    if violated:
        raise ValueError(f"AdmDomain exclusion checks violated: {violated}")
    pending = [entry["check"] for entry in entries if entry.get("violated") is None]
    if pending and artifact["payload"]["verdict"] != "failed":
        raise ValueError("pending AdmDomain checks cannot support an accepted verdict")


def _check_disintegration(artifact: dict[str, Any]) -> None:
    if artifact["payload"]["disintegration"].get("passes_threshold") is not True:
        raise ValueError("disintegration gap does not pass the declared threshold")


def _check_scientific_bridge(artifact: dict[str, Any]) -> None:
    certificate = artifact["payload"]["strictness_certificate"]
    # The builder replays the certificate from actual preparations and kernels.
    # Compare the complete scientific payload, including textual scope fields
    # and pressure diagnostics, so editing an uncrosschecked field cannot
    # silently change the claimed theorem. Receipt code_version is historical.
    expected_artifact = json.loads(json.dumps(build_artifact()))
    if artifact["payload"] != expected_artifact["payload"]:
        raise ValueError("scientific payload differs from complete source replay")
    for key in (
        "claim_id",
        "config_hash",
        "config_path",
        "claim_grade",
        "evidence_type",
        "diagnostic_evidence_type",
        "verdict_basis",
        "quantifier_domain",
        "nonclaims",
    ):
        if artifact[key] != expected_artifact[key]:
            raise ValueError(f"scientific envelope differs from source replay: {key}")
    maps = certificate["object_maps"]
    bridge = artifact["payload"]["bridge_records"][0]
    if bridge["pi0"] != maps["pi0"] or bridge["pi1"] != maps["pi1"]:
        raise ValueError("bridge maps disagree with actual source replay")
    if bridge["carrier_S"]["histories"] != maps["carrier"]:
        raise ValueError("bridge carrier disagrees with the actual witness")
    scope = certificate["scope"]
    for key in ("stop_times", "future_horizons"):
        if bridge["carrier_S"][key] != scope[key]:
            raise ValueError(f"bridge {key} disagrees with the actual experiments")
    if artifact["quantifier_domain"]["N_values"] != [scope["N"]]:
        raise ValueError("quantifier N scope disagrees with actual witness")
    if artifact["config_hash"] != scope["config_hash"]:
        raise ValueError("filing configuration disagrees with actual witness")
    expected = gate_table_from_certificate(certificate, artifact["payload"]["citations"])
    observed = gate_table_from_payload(artifact["payload"]["gate_table"])
    if observed != expected:
        raise ValueError("gate table disagrees with actual scientific evidence")
    if artifact["verdict_basis"] != VERDICT_BASIS:
        raise ValueError("verdict theorem direction is incorrect")
    if artifact["payload"]["object_map_verdict"] != "strict":
        raise ValueError("object-map verdict disagrees with the certified split")
    if bridge["delta"]["delta_stab"] != certificate["packaging_fixed_point_obstruction"]:
        raise ValueError("stability obstruction differs from exact source replay")


def _schema(filename: str) -> dict[str, Any]:
    path = REPO_ROOT / "design" / "schemas" / filename
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TypeError(f"{path} did not contain a JSON object")
    return data


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1]) if len(sys.argv) > 1 else AUDIT_PATH))
