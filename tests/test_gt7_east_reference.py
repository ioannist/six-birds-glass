from __future__ import annotations

import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

pytestmark = pytest.mark.slow


def test_east_reference_artifact_validates_against_envelope() -> None:
    artifact = _load_artifact()
    schema = _load_schema("artifact_envelope.schema.json")

    Draft202012Validator(schema).validate(artifact)
    assert artifact["artifact_kind"] == "constants_readout"
    assert artifact["claim_id"] == "GT7.east_reference"
    assert artifact["evidence_type"] == "monte_carlo_frozen_seeds"
    assert artifact["tau_probe"] == 60


def test_hump_surface_exact_matches_registry_cells() -> None:
    artifact = _load_artifact()
    registry = _load_registry()
    rows = artifact["payload"]["hump_surface_exact"]
    registry_cells = {
        (
            cell["epsilon_hi"],
            cell["epsilon_lo"],
            cell["epsilon_mid"],
            cell["t_w"],
        )
        for cell in registry["grid_products"]["hump_surface_cells"]
    }
    artifact_cells = {
        (
            row["epsilon_hi"],
            row["epsilon_lo"],
            row["epsilon_mid"],
            row["t_w"],
        )
        for row in rows
    }

    assert len(rows) == 56
    assert artifact_cells == registry_cells
    assert len(artifact_cells) == len(rows)


def test_hump_surface_mc_spotcheck_has_declared_slice() -> None:
    artifact = _load_artifact()
    registry = _load_registry()
    rows = artifact["payload"]["hump_surface_mc_spotcheck"]["rows"]
    epsilon_grid = set(registry["grid_products"]["epsilon_grid"])

    assert len(rows) == 7
    assert {row["epsilon_mid"] for row in rows} == epsilon_grid
    assert {row["N"] for row in rows} == {16}
    assert {row["n_traj"] for row in rows} == {20_000}


def test_n10_cross_validation_entries_pass() -> None:
    artifact = _load_artifact()
    entries = artifact["payload"]["n10_cross_validation"]

    assert len(entries) == 2
    assert all(entry["pass"] is True for entry in entries)


def test_memdim_profile_entries_include_quench_nonapplicability() -> None:
    artifact = _load_artifact()
    profiles = artifact["payload"]["memdim_profile"]
    by_id = {entry["instance_id"]: entry for entry in profiles}

    assert set(by_id) == {"kovacs_default", "kovacs_short", "quench_only"}
    assert by_id["kovacs_default"]["max_fiber_size"] == 2
    assert by_id["kovacs_short"]["max_fiber_size"] == 2
    assert by_id["quench_only"]["status"] == "not_applicable"


def test_deficit_decay_secant_slope_recomputes() -> None:
    artifact = _load_artifact()
    deficit = artifact["payload"]["deficit_decay"]
    cd_values = deficit["cd_values"]

    assert deficit["tau_ladder"] == [1, 2, 4, 8]
    assert deficit["secant_slope"] == pytest.approx((cd_values["8"] - cd_values["1"]) / 7.0)


def test_readouts_freeze_hash_matches_registry() -> None:
    artifact = _load_artifact()
    registry = _load_registry()

    assert artifact["readouts_freeze_hash"] == registry["content_hash"]


def _load_artifact() -> dict:
    path = (
        Path(__file__).resolve().parents[1] / "artifacts" / "gt7_constants" / "east_reference.json"
    )
    with path.open(encoding="utf-8") as handle:
        artifact = json.load(handle)
    assert isinstance(artifact, dict)
    return artifact


def _load_registry() -> dict:
    path = Path(__file__).resolve().parents[1] / "registry" / "readouts.json"
    with path.open(encoding="utf-8") as handle:
        registry = json.load(handle)
    assert isinstance(registry, dict)
    return registry


def _load_schema(filename: str) -> dict:
    path = Path(__file__).resolve().parents[1] / "design" / "schemas" / filename
    with path.open(encoding="utf-8") as handle:
        schema = json.load(handle)
    assert isinstance(schema, dict)
    return schema
