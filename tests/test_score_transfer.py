from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

SCORER = None


def test_interval_pass_path() -> None:
    result = scorer().score_cell(_interval_prediction(), {"c1": 7.0})

    assert result["verdict"] == "pass"


def test_interval_fail_path_is_reachable() -> None:
    result = scorer().score_cell(_interval_prediction(), {"c1": 100.0})

    assert result["verdict"] == "fail"


def test_no_prediction_path() -> None:
    prediction = _base_prediction("c1") | {"prediction_type": "no_prediction"}

    result = scorer().score_cell(prediction, {})

    assert result["verdict"] == "no_prediction"
    assert result["predicted"] == "no_prediction"


@pytest.mark.parametrize("observations", [{}, {"c1": None}])
def test_unobserved_path(observations: dict[str, float | None]) -> None:
    result = scorer().score_cell(_interval_prediction(), observations)

    assert result["verdict"] == "unobserved"


def test_order_relation_pass_and_fail() -> None:
    prediction = _relation_prediction("<=")

    passed = scorer().score_cell(prediction, {"c1": 1.0, "c2": 2.0})
    failed = scorer().score_cell(prediction, {"c1": 3.0, "c2": 2.0})

    assert passed["verdict"] == "pass"
    assert failed["verdict"] == "fail"


def test_unrecognized_relation_raises() -> None:
    with pytest.raises(ValueError, match="unrecognized relation"):
        scorer().score_cell(_relation_prediction("~="), {"c1": 1.0, "c2": 2.0})


def test_aggregate_counts() -> None:
    predictions = [
        _interval_prediction("pass_cell"),
        _interval_prediction("fail_cell"),
        _base_prediction("nopred_cell") | {"prediction_type": "no_prediction"},
        _interval_prediction("missing_cell"),
        _relation_prediction("<=", "relation_pass", "compare_cell"),
        _relation_prediction(">", "relation_fail", "compare_cell"),
    ]
    observations = {
        "pass_cell": 7.0,
        "fail_cell": 100.0,
        "relation_pass": 1.0,
        "relation_fail": 1.0,
        "compare_cell": 2.0,
    }

    result = scorer().score_transfer(predictions, observations)

    assert result["aggregate"] == {
        "n_pass": 2,
        "n_fail": 2,
        "n_no_prediction": 1,
        "n_unobserved": 1,
        "total": 6,
    }


def test_score_cell_is_pure_for_same_inputs() -> None:
    prediction = _relation_prediction("<=")
    observations = {"c1": 1.0, "c2": 2.0}

    first = scorer().score_cell(prediction, observations)
    second = scorer().score_cell(prediction, observations)

    assert first == second


def scorer():
    global SCORER
    if SCORER is None:
        script_path = Path(__file__).resolve().parents[1] / "experiments" / "score_transfer.py"
        spec = importlib.util.spec_from_file_location("score_transfer", script_path)
        assert spec is not None
        assert spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        SCORER = module
    return SCORER


def _base_prediction(cell_id: str = "c1") -> dict:
    return {
        "cell_id": cell_id,
        "target_family": "fa1f",
        "readout_id": "t_peak",
    }


def _interval_prediction(cell_id: str = "c1") -> dict:
    return _base_prediction(cell_id) | {
        "prediction_type": "interval",
        "interval": {"lo": "5", "hi": "10"},
    }


def _relation_prediction(
    relation: str,
    cell_id: str = "c1",
    compare_to_cell_id: str = "c2",
) -> dict:
    return _base_prediction(cell_id) | {
        "prediction_type": "monotonicity",
        "relation": relation,
        "compare_to_cell_id": compare_to_cell_id,
    }
