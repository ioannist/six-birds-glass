import importlib.util
import json
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.slow
REQUIRED_GATES = (
    "G_suff",
    "G_desc",
    "G_stab",
    "G_ctrl",
    "G_nosmuggle",
    "G_vis",
    "G_audit",
    "G_strict",
    "G_locglob",
)


def test_gt6_filing_checker_accepts_real_and_rejects_corruptions(tmp_path: Path) -> None:
    audit_path = tmp_path / "audit.json"
    build_main = _load_symbol("build_gt6_filing", "main")
    check_file = _load_symbol("check_gt6_filing", "check_file")

    build_main(output_path=audit_path)

    ok, messages = check_file(audit_path)
    assert ok, messages

    missing_nonclaim = json.loads(audit_path.read_text(encoding="utf-8"))
    missing_nonclaim["nonclaims"] = missing_nonclaim["nonclaims"][1:]
    missing_nonclaim_path = tmp_path / "missing_nonclaim.json"
    missing_nonclaim_path.write_text(json.dumps(missing_nonclaim), encoding="utf-8")
    ok, _messages = check_file(missing_nonclaim_path)
    assert not ok

    bad_hash = json.loads(audit_path.read_text(encoding="utf-8"))
    bad_hash["payload"]["citations"][0]["sha256"] = "0" * 64
    bad_hash_path = tmp_path / "bad_hash.json"
    bad_hash_path.write_text(json.dumps(bad_hash), encoding="utf-8")
    ok, _messages = check_file(bad_hash_path)
    assert not ok


def test_audit_verdict_basis_separates_t20_from_full_forcing_theorem(tmp_path: Path) -> None:
    audit = _build_audit(tmp_path)
    basis = audit.get("verdict_basis")

    assert isinstance(basis, str)
    assert basis
    assert audit["payload"]["verdict"] == "strict"
    assert "F-III T19/T20" in basis
    assert "H4_forcing.material_forcing_count = 0" in basis
    assert "not invoked" in basis.lower()
    assert "full obligation stack satisfied" not in basis.lower()


@pytest.mark.parametrize("missing_gate", REQUIRED_GATES)
def test_checker_rejects_missing_required_gate(tmp_path: Path, missing_gate: str) -> None:
    audit = _build_audit(tmp_path)
    check_file = _load_symbol("check_gt6_filing", "check_file")
    audit["payload"]["gate_table"] = [
        row for row in audit["payload"]["gate_table"] if row["gate"] != missing_gate
    ]
    audit["payload"]["bridge_records"][0]["GateResults"] = [
        row
        for row in audit["payload"]["bridge_records"][0]["GateResults"]
        if row["gate"] != missing_gate
    ]
    path = _write_json(tmp_path / f"missing_{missing_gate}.json", audit)

    ok, _messages = check_file(path)

    assert not ok


def test_checker_rejects_extra_unknown_gate(tmp_path: Path) -> None:
    audit = _build_audit(tmp_path)
    check_file = _load_symbol("check_gt6_filing", "check_file")
    extra = {"gate": "G_unknown", "status": "pass", "required": True, "evidence": "bad"}
    audit["payload"]["gate_table"].append(extra)
    audit["payload"]["bridge_records"][0]["GateResults"].append(extra)
    path = _write_json(tmp_path / "extra_gate.json", audit)

    ok, _messages = check_file(path)

    assert not ok


def test_checker_rejects_duplicate_gate(tmp_path: Path) -> None:
    audit = _build_audit(tmp_path)
    check_file = _load_symbol("check_gt6_filing", "check_file")
    duplicate = dict(audit["payload"]["gate_table"][0])
    audit["payload"]["gate_table"].append(duplicate)
    audit["payload"]["bridge_records"][0]["GateResults"].append(duplicate)
    path = _write_json(tmp_path / "duplicate_gate.json", audit)

    ok, _messages = check_file(path)

    assert not ok


def test_checker_rejects_top_level_bridge_gate_mismatch(tmp_path: Path) -> None:
    audit = _build_audit(tmp_path)
    check_file = _load_symbol("check_gt6_filing", "check_file")
    audit["payload"]["bridge_records"][0]["GateResults"][0]["status"] = "failed"
    path = _write_json(tmp_path / "gate_mismatch.json", audit)

    ok, _messages = check_file(path)

    assert not ok


def test_checker_rejects_missing_disintegration_nonclaim(tmp_path: Path) -> None:
    audit = _build_audit(tmp_path)
    check_file = _load_symbol("check_gt6_filing", "check_file")
    audit["nonclaims"] = [
        nonclaim
        for nonclaim in audit["nonclaims"]
        if "conditional disintegration on strata" not in nonclaim
    ]
    path = _write_json(tmp_path / "missing_disintegration_nonclaim.json", audit)

    ok, _messages = check_file(path)

    assert not ok


def test_checker_rejects_failed_disintegration_threshold(tmp_path: Path) -> None:
    audit = _build_audit(tmp_path)
    check_file = _load_symbol("check_gt6_filing", "check_file")
    audit["payload"]["disintegration"]["passes_threshold"] = False
    path = _write_json(tmp_path / "failed_threshold.json", audit)

    ok, _messages = check_file(path)

    assert not ok


def test_checker_rejects_two_bridge_records(tmp_path: Path) -> None:
    audit = _build_audit(tmp_path)
    check_file = _load_symbol("check_gt6_filing", "check_file")
    audit["payload"]["bridge_records"].append(dict(audit["payload"]["bridge_records"][0]))
    path = _write_json(tmp_path / "two_bridges.json", audit)

    ok, _messages = check_file(path)

    assert not ok


def test_checker_rejects_incomplete_exclusion_ledger(tmp_path: Path) -> None:
    audit = _build_audit(tmp_path)
    check_file = _load_symbol("check_gt6_filing", "check_file")
    audit["payload"]["adm_domain"]["exclusion_checks"] = audit["payload"]["adm_domain"][
        "exclusion_checks"
    ][1:]
    path = _write_json(tmp_path / "incomplete_exclusions.json", audit)

    ok, _messages = check_file(path)

    assert not ok


def _build_audit(tmp_path: Path) -> dict:
    audit_path = tmp_path / "audit.json"
    build_main = _load_symbol("build_gt6_filing", "main")
    build_main(output_path=audit_path)
    return json.loads(audit_path.read_text(encoding="utf-8"))


def _write_json(path: Path, data: dict) -> Path:
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def _load_symbol(script_stem: str, symbol: str):
    script_path = Path(__file__).resolve().parents[1] / "experiments" / f"{script_stem}.py"
    spec = importlib.util.spec_from_file_location(script_stem, script_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return getattr(module, symbol)
