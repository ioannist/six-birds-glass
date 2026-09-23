from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

FROZEN_SCORER_HASH = "beb83ce759f656ae1b60fdecd22dc736fe682440eba338e279dab9199ad21b22"


def test_score_transfer_hash_matches_frozen_reference() -> None:
    assert _sha256_file(_repo_root() / "experiments" / "score_transfer.py") == FROZEN_SCORER_HASH


def test_observations_intermediate_lives_in_registry() -> None:
    builder = _builder()

    assert builder.OBSERVATIONS_PATH.relative_to(_repo_root()) == Path(
        "registry/gt7_observations.json"
    )
    assert not (_repo_root() / "artifacts" / "gt7_constants" / "observations.json").exists()


def test_build_observations_resolves_order_relation_cell_ids() -> None:
    builder = _builder()
    predictions = _load_json("registry/predictions_f5e2a3332a2191a2.json")["predictions"]
    observations = builder.build_observations(
        predictions,
        _load_json("artifacts/gt7_constants/fa_target.json"),
        _load_json("artifacts/gt7_constants/trap_target.json"),
    )

    order_cell_ids = {
        prediction["cell_id"]
        for prediction in predictions
        if prediction["prediction_type"] == "order_relation"
    }

    assert order_cell_ids == {
        "fa:t_K_order:eps_mid_3-5_vs_1-2",
        "trap:t_K_order:eps_mid_3-5_vs_1-2",
    }
    assert order_cell_ids <= observations.keys()


def test_transfer_scores_artifact_validates_against_envelope() -> None:
    artifact = _load_scores_artifact()

    Draft202012Validator(_load_json("design/schemas/artifact_envelope.schema.json")).validate(
        artifact
    )
    assert artifact["artifact_kind"] == "transfer_scores"
    assert artifact["scoring_script_hash"] == FROZEN_SCORER_HASH


def test_transfer_score_aggregate_counts_are_consistent() -> None:
    aggregate = _load_scores_artifact()["payload"]["aggregate"]

    assert (
        aggregate["n_pass"]
        + aggregate["n_fail"]
        + aggregate["n_no_prediction"]
        + aggregate["n_unobserved"]
        == aggregate["total"]
        == 338
    )


def test_two_concrete_fa_cells_score_as_hand_verified_passes() -> None:
    scores = _score_cells_by_id()
    predictions = _predictions_by_id()
    fa_rows = _target_rows_by_key("artifacts/gt7_constants/fa_target.json")

    _assert_fa_pass_cell(
        "fa:t_K:7-10_1-10_1-2_20",
        expected_interval={"lo": "2", "hi": "8"},
        expected_observed=8,
        scores=scores,
        predictions=predictions,
        fa_rows=fa_rows,
    )
    _assert_fa_pass_cell(
        "fa:t_peak:7-10_1-10_1-2_20",
        expected_interval={"lo": "12", "hi": "36"},
        expected_observed=35,
        scores=scores,
        predictions=predictions,
        fa_rows=fa_rows,
    )


def test_trap_has_expected_unobserved_interval_cell() -> None:
    cell = _score_cells_by_id()["trap:t_K:7-10_1-10_1-2_20"]

    assert cell["target_family"] == "trap"
    assert cell["verdict"] == "unobserved"
    assert cell["observed"] is None


def _assert_fa_pass_cell(
    cell_id: str,
    *,
    expected_interval: dict[str, str],
    expected_observed: int,
    scores: dict[str, dict[str, Any]],
    predictions: dict[str, dict[str, Any]],
    fa_rows: dict[tuple[str, str, str, int], dict[str, Any]],
) -> None:
    prediction = predictions[cell_id]
    row = fa_rows[_grid_key(prediction["grid_point"])]
    score = scores[cell_id]

    assert prediction["interval"] == expected_interval
    assert row[prediction["readout_id"]] == expected_observed
    assert score["observed"] == float(expected_observed)
    assert score["verdict"] == "pass"


def _builder():
    script_path = _repo_root() / "experiments" / "build_gt7_transfer_scores.py"
    spec = importlib.util.spec_from_file_location("build_gt7_transfer_scores", script_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _score_cells_by_id() -> dict[str, dict[str, Any]]:
    return {cell["cell_id"]: cell for cell in _load_scores_artifact()["payload"]["cells"]}


def _predictions_by_id() -> dict[str, dict[str, Any]]:
    return {
        prediction["cell_id"]: prediction
        for prediction in _load_json("registry/predictions_f5e2a3332a2191a2.json")["predictions"]
    }


def _target_rows_by_key(relative_path: str) -> dict[tuple[str, str, str, int], dict[str, Any]]:
    return {
        _grid_key(row): row for row in _load_json(relative_path)["payload"]["hump_surface_exact"]
    }


def _grid_key(cell: dict[str, Any]) -> tuple[str, str, str, int]:
    return (
        cell["epsilon_hi"],
        cell["epsilon_lo"],
        cell["epsilon_mid"],
        int(cell["t_w"]),
    )


def _load_scores_artifact() -> dict[str, Any]:
    return _load_json("artifacts/gt7_constants/gt7_transfer_scores.json")


def _load_json(relative_path: str) -> dict[str, Any]:
    with (_repo_root() / relative_path).open(encoding="utf-8") as handle:
        data = json.load(handle)
    assert isinstance(data, dict)
    return data


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]
