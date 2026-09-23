from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path

from sixbirds_glass.io.config import canonical_json_bytes
from sixbirds_glass.io.rational import rational_to_str
from sixbirds_glass.models.grid import DEFAULT_EPSILON_GRID
from sixbirds_glass.protocols import catalog

REQUIRED_READOUT_IDS = {
    "t_K",
    "hump_height",
    "t_peak",
    "hump_surface",
    "memdim_profile",
    "deficit_decay",
}


def test_readouts_registry_has_exact_readout_ids() -> None:
    registry = _load_registry()

    assert {entry["readout_id"] for entry in registry["readouts"]} == REQUIRED_READOUT_IDS
    assert len(registry["readouts"]) == 6
    assert all(entry["run_only"] is True for entry in registry["readouts"])


def test_readouts_registry_gt3_hashes_are_real() -> None:
    registry = _load_registry()
    repo_root = Path(__file__).resolve().parents[1]
    gt3_path = repo_root / "artifacts" / "gt3_foreclosure" / "lens_class_sweep.json"
    gt3_hash = hashlib.sha256(gt3_path.read_bytes()).hexdigest()

    for entry in registry["readouts"]:
        assert entry["gt3_cross_ref"] == {
            "artifact_path": "artifacts/gt3_foreclosure/lens_class_sweep.json",
            "artifact_hash": gt3_hash,
        }


def test_readouts_registry_content_hash_is_self_consistent() -> None:
    registry = _load_registry()
    body = dict(registry)
    stored_hash = body.pop("content_hash")

    assert hashlib.sha256(canonical_json_bytes(body)).hexdigest() == stored_hash


def test_hump_surface_cells_are_declared_grid_product() -> None:
    registry = _load_registry()
    cells = registry["grid_products"]["hump_surface_cells"]
    grid_values = {rational_to_str(epsilon) for epsilon in DEFAULT_EPSILON_GRID}

    assert len(cells) == 56
    for cell in cells:
        assert set(cell) == {"epsilon_hi", "epsilon_lo", "epsilon_mid", "t_w"}
        assert cell["epsilon_hi"] in grid_values
        assert cell["epsilon_lo"] in grid_values
        assert cell["epsilon_mid"] in grid_values
        assert cell["t_w"] in {20, 60}


def test_tau_ladder_is_frozen() -> None:
    registry = _load_registry()

    assert registry["grid_products"]["tau_ladder"] == [1, 2, 4, 8]


def test_protocol_catalog_instances_reference_real_constructors() -> None:
    registry = _load_registry()
    valid_constructors = {"p_eq", "p_quench", "p_kovacs"}

    for instance in registry["grid_products"]["protocol_catalog_instances"]:
        constructor = instance["constructor"]
        assert constructor in valid_constructors
        assert callable(getattr(catalog, constructor))


def _load_registry() -> dict:
    script = _load_builder()
    registry_path = Path(__file__).resolve().parents[1] / "registry" / "readouts.json"
    if not registry_path.exists():
        script.write_registry(registry_path)
    with registry_path.open(encoding="utf-8") as handle:
        loaded = json.load(handle)
    assert isinstance(loaded, dict)
    return loaded


def _load_builder():
    script_path = (
        Path(__file__).resolve().parents[1] / "experiments" / "build_gt7_readouts_registry.py"
    )
    spec = importlib.util.spec_from_file_location("build_gt7_readouts_registry", script_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module
