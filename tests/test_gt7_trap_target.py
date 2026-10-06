from __future__ import annotations

import glob
import hashlib
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

pytestmark = pytest.mark.slow


def test_trap_target_artifact_validates_against_envelope() -> None:
    artifact = _load_artifact()
    Draft202012Validator(_load_schema()).validate(artifact)

    assert artifact["artifact_kind"] == "constants_readout"
    assert artifact["claim_id"] == "GT7.trap_target"
    assert artifact["evidence_type"] == "exact_rational"
    assert artifact["trap_count"] == 8
    assert artifact["finding"]
    assert artifact["freeze_refs"] == [
        _content_hash("registry/readouts.json"),
        _content_hash("registry/predictions_f5e2a3332a2191a2.json"),
    ]


def test_trap_target_exact_rows_match_registry_cells() -> None:
    artifact = _load_artifact()
    registry = _load_json("registry/readouts.json")
    rows = artifact["payload"]["hump_surface_exact"]

    assert len(rows) == 56
    assert _cell_set(rows) == _cell_set(registry["grid_products"]["hump_surface_cells"])


def test_trap_target_cell_ids_match_predictions_registry() -> None:
    artifact = _load_artifact()
    predictions = _prediction_ids()
    sample_rows = [
        artifact["payload"]["hump_surface_exact"][0],
        next(
            row
            for row in artifact["payload"]["hump_surface_exact"]
            if row["epsilon_mid"] == "1/2" and row["t_w"] == 20
        ),
    ]

    for row in sample_rows:
        for readout_id, cell_id in row["cell_ids"].items():
            assert cell_id in predictions
            assert cell_id == _expected_cell_id("trap", readout_id, row)


def _load_artifact() -> dict:
    return _load_json("artifacts/gt7_constants/trap_target.json")


def _load_json(relative_path: str) -> dict:
    path = Path(__file__).resolve().parents[1] / relative_path
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    assert isinstance(data, dict)
    return data


def _load_schema() -> dict:
    return _load_json("design/schemas/artifact_envelope.schema.json")


def _content_hash(relative_path: str) -> str:
    data = _load_json(relative_path)
    expected = str(data["content_hash"])
    body = dict(data)
    body.pop("content_hash")
    encoded = json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode(
        "utf-8"
    )
    assert hashlib.sha256(encoded).hexdigest() == expected
    return expected


def _prediction_ids() -> set[str]:
    paths = sorted(
        glob.glob(str(Path(__file__).resolve().parents[1] / "registry/predictions_*.json"))
    )
    assert len(paths) == 1
    with Path(paths[0]).open(encoding="utf-8") as handle:
        registry = json.load(handle)
    return {prediction["cell_id"] for prediction in registry["predictions"]}


def _cell_set(rows: list[dict]) -> set[tuple[str, str, str, int]]:
    return {
        (row["epsilon_hi"], row["epsilon_lo"], row["epsilon_mid"], int(row["t_w"])) for row in rows
    }


def _expected_cell_id(prefix: str, readout_id: str, row: dict) -> str:
    suffix = "_".join(
        [
            row["epsilon_hi"].replace("/", "-"),
            row["epsilon_lo"].replace("/", "-"),
            row["epsilon_mid"].replace("/", "-"),
            str(row["t_w"]),
        ]
    )
    return f"{prefix}:{readout_id}:{suffix}"
