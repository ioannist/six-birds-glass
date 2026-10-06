from __future__ import annotations

import glob
import hashlib
import importlib.util
import json
import math
import sys
from pathlib import Path

from jsonschema import Draft202012Validator


def test_predictions_registry_validates_against_schema() -> None:
    registry = _load_predictions()
    schema = _load_json("design/schemas/predictions_registry.schema.json")

    Draft202012Validator(schema).validate(registry)


def test_predictions_registry_hash_citations_are_real() -> None:
    registry = _load_predictions()

    assert registry["source_artifact_hash"] == _sha256(
        "artifacts/gt7_constants/east_reference.json"
    )
    assert registry["readouts_freeze_hash"] == _load_json("registry/readouts.json")["content_hash"]
    assert registry["scoring_script_hash"] == _sha256("experiments/score_transfer.py")


def test_prediction_cell_counts_match_east_reference_truth() -> None:
    registry = _load_predictions()
    east_rows = _load_json("artifacts/gt7_constants/east_reference.json")["payload"][
        "hump_surface_exact"
    ]
    found_count = sum(1 for row in east_rows if row["found"])
    not_found_count = len(east_rows) - found_count
    predictions = registry["predictions"]
    interval_count = sum(1 for row in predictions if row["prediction_type"] == "interval")
    no_prediction_count = sum(1 for row in predictions if row["prediction_type"] == "no_prediction")
    order_count = sum(1 for row in predictions if row["prediction_type"] == "order_relation")

    assert found_count == 7
    assert not_found_count == 49
    assert interval_count == found_count * 2 * 3
    assert no_prediction_count == not_found_count * 2 * 3
    assert order_count == 2
    assert len(predictions) == (len(east_rows) * 2 * 3) + 2


def test_interval_predictions_have_valid_bounds() -> None:
    registry = _load_predictions()

    for prediction in registry["predictions"]:
        if prediction["prediction_type"] != "interval":
            continue
        lo = float(prediction["interval"]["lo"])
        hi = float(prediction["interval"]["hi"])
        assert lo >= 0
        assert lo <= hi


def test_order_relation_compare_ids_resolve() -> None:
    registry = _load_predictions()
    cell_ids = {prediction["cell_id"] for prediction in registry["predictions"]}

    for prediction in registry["predictions"]:
        if prediction["prediction_type"] == "order_relation":
            assert prediction["compare_to_cell_id"] in cell_ids


def test_rescaling_maps_cover_all_grid_epsilons_with_positive_finite_values() -> None:
    registry = _load_predictions()
    grid = set(_load_json("registry/readouts.json")["grid_products"]["epsilon_grid"])
    maps = {entry["map_id"]: entry for entry in registry["rescaling_maps"]}

    assert set(maps) == {"spectral_gap_ratio_fa", "spectral_gap_ratio_trap"}
    for entry in maps.values():
        assert set(entry["parameters"]) == grid
        assert all(
            math.isfinite(float(value)) and float(value) > 0
            for value in entry["parameters"].values()
        )


def test_every_east_cell_appears_for_both_families_and_three_readouts() -> None:
    registry = _load_predictions()
    east_rows = _load_json("artifacts/gt7_constants/east_reference.json")["payload"][
        "hump_surface_exact"
    ]
    prediction_keys = {
        (
            _family_prefix(prediction["target_family"]),
            prediction["readout_id"],
            prediction["grid_point"]["epsilon_hi"],
            prediction["grid_point"]["epsilon_lo"],
            prediction["grid_point"]["epsilon_mid"],
            prediction["grid_point"]["t_w"],
        )
        for prediction in registry["predictions"]
        if prediction["prediction_type"] in {"interval", "no_prediction"}
    }

    for row in east_rows:
        for family in ("fa", "trap"):
            for readout_id in ("t_K", "t_peak", "hump_height"):
                assert (
                    family,
                    readout_id,
                    row["epsilon_hi"],
                    row["epsilon_lo"],
                    row["epsilon_mid"],
                    row["t_w"],
                ) in prediction_keys


def _load_predictions() -> dict:
    paths = sorted(
        glob.glob(str(Path(__file__).resolve().parents[1] / "registry/predictions_*.json"))
    )
    assert len(paths) == 1
    with Path(paths[0]).open(encoding="utf-8") as handle:
        registry = json.load(handle)
    assert isinstance(registry, dict)
    return registry


def _load_json(relative_path: str) -> dict:
    path = Path(__file__).resolve().parents[1] / relative_path
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    assert isinstance(data, dict)
    return data


def _sha256(relative_path: str) -> str:
    path = Path(__file__).resolve().parents[1] / relative_path
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _family_prefix(target_family: str) -> str:
    return "fa" if target_family == "fa1f" else target_family


def _load_builder():
    script_path = Path(__file__).resolve().parents[1] / "experiments" / "build_gt7_predictions.py"
    spec = importlib.util.spec_from_file_location("build_gt7_predictions", script_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module
