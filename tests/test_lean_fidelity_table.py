from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

ALLOWED_FIDELITIES = {
    "verified",
    "narrowed / parametric",
    "schema (projection)",
    "trivial",
    "typed mirror",
    "computational evidence only",
}


def test_lean_fidelity_table_validates_against_envelope() -> None:
    artifact = _artifact()

    Draft202012Validator(_load_json("design/schemas/artifact_envelope.schema.json")).validate(
        artifact
    )
    assert artifact["artifact_kind"] == "lean_fidelity_table"
    assert artifact["claim_grade"] == "bridge_record"
    assert artifact["scope_boundary_finding"]


def test_every_fidelity_label_is_allowed() -> None:
    for row in _rows():
        assert row["fidelity"] in ALLOWED_FIDELITIES


def test_cited_lean_names_exist_in_corresponding_files() -> None:
    for row in _rows():
        lean_name = row["lean_name"]
        lean_file = row["lean_file"]
        if lean_name is None:
            assert lean_file is None
            continue
        assert lean_file is not None
        content = (_repo_root() / lean_file).read_text(encoding="utf-8")
        assert lean_name in content


def test_vacuous_antecedent_notes_are_present() -> None:
    rows_by_name = {row["qualified_lean_name"]: row for row in _rows()}

    for lean_name in [
        "HolonomyMemory.strictRefinement_iff_nonempty_predictiveWitness",
        "HolonomyMemory.loopAsymmetry_exhibits_movedPredictive_fixedCurrent",
    ]:
        notes = rows_by_name[lean_name]["notes"]
        assert "unsatisfiable" in notes
        assert "strictRefinement_impossible_GENERIC" in notes


def test_theorem_rows_record_print_axioms_output() -> None:
    non_theorem_names = {"push_id", "observe_push", "push_compose", "glassInstance", None}

    for row in _rows():
        if row["lean_name"] in non_theorem_names:
            assert "axioms" not in row
            assert "axioms_raw" not in row
            continue
        assert "axioms" in row
        assert isinstance(row["axioms"], list)
        assert row["axioms_raw"]

    rows_by_name = {row["qualified_lean_name"]: row for row in _rows()}
    assert rows_by_name["HolonomyMemory.predictiveToCurrent_commutes_with_transport"]["axioms"] == [
        "propext",
        "Quot.sound",
    ]
    assert rows_by_name["HolonomyMemory.current_implies_future_GENERIC"]["axioms"] == []


def test_inventory_covers_live_audit_and_binds_all_current_sources() -> None:
    artifact = _artifact()
    audit = _load_json("math/lean_axiom_audit.json")
    rows = {row["qualified_lean_name"]: row for row in _rows() if row["lean_name"] is not None}
    assert set(rows) == {theorem["declaration"] for theorem in audit["theorems"]}
    for theorem in audit["theorems"]:
        row = rows[theorem["declaration"]]
        assert row["axioms"] == theorem["axioms"]
        assert row["axioms_raw"] == theorem["raw"]
    assert artifact["payload"]["source_sha256"] == audit["source_sha256"]
    for path, expected_hash in artifact["payload"]["source_sha256"].items():
        assert hashlib.sha256((_repo_root() / path).read_bytes()).hexdigest() == expected_hash
    assert "GlassWitness.EnergyN8.all_horizons_nonfactorization" in rows
    assert "M factors through S" in artifact["payload"]["factorization_direction"]


def test_native_decide_not_used() -> None:
    artifact = _artifact()
    assert all(row["native_decide_used"] is False for row in _rows())
    assert artifact["payload"]["native_decide_grep_result"] == ""

    result = subprocess.run(
        ["rg", "-n", "native_decide", "lean"],
        cwd=_repo_root(),
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.stdout == ""


def _artifact() -> dict[str, Any]:
    return _load_json("artifacts/lean_fidelity_table.json")


def _rows() -> list[dict[str, Any]]:
    rows = _artifact()["payload"]["rows"]
    assert isinstance(rows, list)
    return rows


def _load_json(relative_path: str) -> dict[str, Any]:
    with (_repo_root() / relative_path).open(encoding="utf-8") as handle:
        data = json.load(handle)
    assert isinstance(data, dict)
    return data


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]
