"""Score frozen GT7 transfer predictions against observed target readouts."""

from __future__ import annotations

import argparse
import hashlib
import json
import operator
import subprocess
from collections.abc import Callable
from pathlib import Path
from typing import Any, Literal

Verdict = Literal["pass", "fail", "no_prediction", "unobserved"]

OPERATORS: dict[str, Callable[[float, float], bool]] = {
    "<=": operator.le,
    "<": operator.lt,
    ">=": operator.ge,
    ">": operator.gt,
}


def score_cell(prediction: dict[str, Any], observations: dict[str, float | None]) -> dict[str, Any]:
    """Score one prediction cell against a flat observation mapping."""

    prediction_type = prediction["prediction_type"]
    cell_id = prediction["cell_id"]
    observed = observations.get(cell_id)

    if prediction_type == "no_prediction":
        return _result(prediction, "no_prediction", "no_prediction", observed)

    if prediction_type == "interval":
        interval = prediction["interval"]
        predicted = f"[{interval['lo']}, {interval['hi']}]"
        if observed is None:
            return _result(prediction, "unobserved", predicted, observed)
        lo = float(interval["lo"])
        hi = float(interval["hi"])
        verdict: Verdict = "pass" if lo <= observed <= hi else "fail"
        return _result(prediction, verdict, predicted, observed)

    if prediction_type in {"order_relation", "monotonicity"}:
        relation = prediction["relation"]
        if relation not in OPERATORS:
            raise ValueError(f"unrecognized relation: {relation!r}")
        compare_to_cell_id = prediction["compare_to_cell_id"]
        predicted = f"{cell_id} {relation} {compare_to_cell_id}"
        compared = observations.get(compare_to_cell_id)
        if observed is None or compared is None:
            return _result(prediction, "unobserved", predicted, observed)
        verdict = "pass" if OPERATORS[relation](observed, compared) else "fail"
        return _result(prediction, verdict, predicted, observed)

    raise ValueError(f"unrecognized prediction_type: {prediction_type!r}")


def score_transfer(
    predictions: list[dict[str, Any]], observations: dict[str, float | None]
) -> dict[str, Any]:
    """Score every prediction and aggregate verdict counts."""

    cells = [score_cell(prediction, observations) for prediction in predictions]
    aggregate = {
        "n_pass": sum(1 for cell in cells if cell["verdict"] == "pass"),
        "n_fail": sum(1 for cell in cells if cell["verdict"] == "fail"),
        "n_no_prediction": sum(1 for cell in cells if cell["verdict"] == "no_prediction"),
        "n_unobserved": sum(1 for cell in cells if cell["verdict"] == "unobserved"),
        "total": len(cells),
    }
    return {"cells": cells, "aggregate": aggregate}


def main(predictions_path: Path, observations_path: Path, output_path: Path) -> None:
    """Score a predictions registry against flat observations and write an artifact."""

    predictions_registry = _load_json(predictions_path)
    observations = _load_observations(observations_path)
    scores = score_transfer(predictions_registry["predictions"], observations)
    artifact = {
        "artifact_kind": "transfer_scores",
        "claim_id": "GT7.transfer_scores",
        "config_hash": _sha256_file(predictions_path),
        "config_path": str(predictions_path),
        "code_version": _code_version(),
        "claim_grade": "run_only_readout",
        "evidence_type": "float64_deterministic",
        "quantifier_domain": {
            "model_families": sorted(
                {prediction["target_family"] for prediction in predictions_registry["predictions"]}
            ),
            "N_values": [],
            "epsilon_grid": [],
            "lens_catalog_hash": predictions_registry.get("readouts_freeze_hash", ""),
            "protocol_catalog_hash": predictions_registry.get("source_artifact_hash", ""),
        },
        "nonclaims": [
            "transfer scoring is mechanical comparison against pre-registered predictions",
            "score counts are not a fitted scaling law",
        ],
        "scoring_script_hash": _sha256_file(Path(__file__)),
        "predictions_source_hash": _sha256_file(predictions_path),
        "payload": scores,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(artifact, indent=2, sort_keys=True), encoding="utf-8")


def _result(
    prediction: dict[str, Any],
    verdict: Verdict,
    predicted: str,
    observed: float | None,
) -> dict[str, Any]:
    return {
        "cell_id": prediction["cell_id"],
        "target_family": prediction["target_family"],
        "readout_id": prediction["readout_id"],
        "prediction_type": prediction["prediction_type"],
        "verdict": verdict,
        "predicted": predicted,
        "observed": observed,
    }


def _load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise TypeError(f"{path} did not contain a JSON object")
    return data


def _load_observations(path: Path) -> dict[str, float | None]:
    data = _load_json(path)
    observations: dict[str, float | None] = {}
    for cell_id, value in data.items():
        observations[cell_id] = None if value is None else float(value)
    return observations


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _code_version() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=Path(__file__).resolve().parents[1],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return "unknown"
    return result.stdout.strip()


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("predictions_path", type=Path)
    parser.add_argument("observations_path", type=Path)
    parser.add_argument("output_path", type=Path)
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    main(args.predictions_path, args.observations_path, args.output_path)
