"""Build the frozen GT7 transfer predictions registry from East data only."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from sixbirds_glass.io.config import canonical_json_bytes
from sixbirds_glass.io.rational import str_to_rational
from sixbirds_glass.models.east import build_east_kernel
from sixbirds_glass.models.fa import build_fa_kernel
from sixbirds_glass.models.grid import DEFAULT_EPSILON_GRID
from sixbirds_glass.models.spectral import spectral_gap
from sixbirds_glass.models.trap import (
    DEFAULT_TRAP_BASE_WEIGHTS,
    build_trap_kernel,
    declared_trap_weights_by_epsilon,
)

ROOT = Path(__file__).resolve().parents[1]
EAST_REFERENCE_PATH = ROOT / "artifacts" / "gt7_constants" / "east_reference.json"
READOUTS_PATH = ROOT / "registry" / "readouts.json"
SCORER_PATH = ROOT / "experiments" / "score_transfer.py"
OUTPUT_DIR = ROOT / "registry"
FAMILIES = ("fa", "trap")
READOUTS = ("t_K", "t_peak", "hump_height")


def main(output_dir: Path = OUTPUT_DIR) -> None:
    registry = build_predictions_registry()
    output_dir.mkdir(parents=True, exist_ok=True)
    content_hash = registry["content_hash"]
    output_path = output_dir / f"predictions_{content_hash[:16]}.json"
    output_path.write_text(
        json.dumps(registry, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    print(f"wrote {output_path}")
    print(f"content_hash={content_hash}")


def build_predictions_registry() -> dict[str, Any]:
    east_reference = _load_json(EAST_REFERENCE_PATH)
    readouts = _load_json(READOUTS_PATH)
    source_hash = _sha256_file(EAST_REFERENCE_PATH)
    readouts_hash = str(readouts["content_hash"])
    scoring_hash = _sha256_file(SCORER_PATH)
    rescaling_maps = _rescaling_maps()
    predictions = _predictions(east_reference, rescaling_maps)
    registry: dict[str, Any] = {
        "registry_version": 1,
        "source_family": "east",
        "source_artifact_hash": source_hash,
        "readouts_freeze_hash": readouts_hash,
        "scoring_script_hash": scoring_hash,
        "rescaling_maps": rescaling_maps,
        "predictions": predictions,
    }
    _validate_registry(registry)
    registry["content_hash"] = hashlib.sha256(canonical_json_bytes(registry)).hexdigest()
    return registry


def _rescaling_maps() -> list[dict[str, Any]]:
    trap_weights = declared_trap_weights_by_epsilon(DEFAULT_EPSILON_GRID)
    fa_parameters: dict[str, float] = {}
    trap_parameters: dict[str, float] = {}
    for epsilon in DEFAULT_EPSILON_GRID:
        epsilon_key = _rational_text(epsilon)
        east_gap = spectral_gap(build_east_kernel(10, epsilon))
        fa_gap = spectral_gap(build_fa_kernel(10, epsilon))
        trap_gap = spectral_gap(build_trap_kernel(DEFAULT_TRAP_BASE_WEIGHTS, trap_weights[epsilon]))
        fa_parameters[epsilon_key] = fa_gap / east_gap
        trap_parameters[epsilon_key] = trap_gap / east_gap
    return [
        {
            "map_id": "spectral_gap_ratio_fa",
            "definition": (
                "spectral_gap(FA kernel, N=10, epsilon) / spectral_gap(East kernel, "
                "N=10, epsilon), evaluated at the cell's epsilon_mid"
            ),
            "parameters": fa_parameters,
        },
        {
            "map_id": "spectral_gap_ratio_trap",
            "definition": (
                "spectral_gap(trap kernel, declared M=8 weights at epsilon) / "
                "spectral_gap(East kernel, N=10, epsilon), evaluated at the cell's epsilon_mid"
            ),
            "parameters": trap_parameters,
        },
    ]


def _predictions(
    east_reference: dict[str, Any],
    rescaling_maps: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    ratio_by_family = {
        "fa": _map_by_id(rescaling_maps, "spectral_gap_ratio_fa")["parameters"],
        "trap": _map_by_id(rescaling_maps, "spectral_gap_ratio_trap")["parameters"],
    }
    predictions: list[dict[str, Any]] = []
    for row in east_reference["payload"]["hump_surface_exact"]:
        for family in FAMILIES:
            for readout_id in READOUTS:
                predictions.append(_prediction_for_row(row, family, readout_id, ratio_by_family))
    predictions.extend(_order_relation_predictions())
    return predictions


def _prediction_for_row(
    row: dict[str, Any],
    family: str,
    readout_id: str,
    ratio_by_family: dict[str, dict[str, float]],
) -> dict[str, Any]:
    cell_id = _cell_id(family, readout_id, row)
    base = {
        "cell_id": cell_id,
        "target_family": _target_family(family),
        "grid_point": _grid_point(row),
        "readout_id": readout_id,
    }
    if not row["found"]:
        return base | {"prediction_type": "no_prediction"}

    ratio = float(ratio_by_family[family][row["epsilon_mid"]])
    if readout_id in {"t_K", "t_peak"}:
        east_value = int(row[readout_id])
        center = round(east_value / ratio)
        lo = max(0, math.floor(center * 0.5))
        hi = math.ceil(center * 1.5)
    else:
        east_value = float(str_to_rational(row["hump_height"]))
        center = east_value / ratio
        lo = max(0.0, center * 0.5)
        hi = center * 1.5
    return base | {
        "prediction_type": "interval",
        "interval": {"lo": str(lo), "hi": str(hi)},
        "margin_rule": (
            "center * [0.5, 1.5], center = round(east_value / R) for times "
            "and east_hump_height / R for hump_height"
        ),
        "rescaling_map_id": f"spectral_gap_ratio_{family}",
    }


def _order_relation_predictions() -> list[dict[str, Any]]:
    rows = []
    for family in FAMILIES:
        grid_point = {
            "epsilon_hi": "7/10",
            "epsilon_lo": "1/10",
            "epsilon_mid": "3/5",
            "t_w": 20,
        }
        rows.append(
            {
                "cell_id": f"{family}:t_K_order:eps_mid_3-5_vs_1-2",
                "target_family": _target_family(family),
                "readout_id": "t_K",
                "prediction_type": "order_relation",
                "relation": ">=",
                "compare_to_cell_id": f"{family}:t_K:7-10_1-10_1-2_20",
                "grid_point": grid_point,
                "rescaling_map_id": f"spectral_gap_ratio_{family}",
            }
        )
    return rows


def _cell_id(family: str, readout_id: str, row: dict[str, Any]) -> str:
    parts = [
        _id_epsilon(row["epsilon_hi"]),
        _id_epsilon(row["epsilon_lo"]),
        _id_epsilon(row["epsilon_mid"]),
        str(row["t_w"]),
    ]
    return f"{family}:{readout_id}:{'_'.join(parts)}"


def _grid_point(row: dict[str, Any]) -> dict[str, str | int]:
    return {
        "epsilon_hi": row["epsilon_hi"],
        "epsilon_lo": row["epsilon_lo"],
        "epsilon_mid": row["epsilon_mid"],
        "t_w": row["t_w"],
    }


def _target_family(family: str) -> str:
    return "fa1f" if family == "fa" else family


def _id_epsilon(epsilon: str) -> str:
    return epsilon.replace("/", "-")


def _rational_text(value: Any) -> str:
    return f"{value.numerator}/{value.denominator}"


def _map_by_id(maps: list[dict[str, Any]], map_id: str) -> dict[str, Any]:
    for item in maps:
        if item["map_id"] == map_id:
            return item
    raise ValueError(f"missing rescaling map {map_id}")


def _load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise TypeError(f"{path} did not contain a JSON object")
    return data


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _validate_registry(registry: dict[str, Any]) -> None:
    schema = _load_json(ROOT / "design" / "schemas" / "predictions_registry.schema.json")
    Draft202012Validator(schema).validate(registry)


if __name__ == "__main__":
    main()
