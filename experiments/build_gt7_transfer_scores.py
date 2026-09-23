"""Build GT7 transfer observations and run the frozen scorer."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from sixbirds_glass.io.rational import str_to_rational  # noqa: E402

FROZEN_SCORER_HASH = "beb83ce759f656ae1b60fdecd22dc736fe682440eba338e279dab9199ad21b22"
PREDICTIONS_PATH = REPO_ROOT / "registry" / "predictions_f5e2a3332a2191a2.json"
FA_TARGET_PATH = REPO_ROOT / "artifacts" / "gt7_constants" / "fa_target.json"
TRAP_TARGET_PATH = REPO_ROOT / "artifacts" / "gt7_constants" / "trap_target.json"
OBSERVATIONS_PATH = REPO_ROOT / "registry" / "gt7_observations.json"
SCORES_PATH = REPO_ROOT / "artifacts" / "gt7_constants" / "gt7_transfer_scores.json"
SCORER_PATH = REPO_ROOT / "experiments" / "score_transfer.py"


def main(
    predictions_path: Path = PREDICTIONS_PATH,
    fa_target_path: Path = FA_TARGET_PATH,
    trap_target_path: Path = TRAP_TARGET_PATH,
    observations_path: Path = OBSERVATIONS_PATH,
    scores_path: Path = SCORES_PATH,
) -> None:
    """Write observations and score them with the frozen transfer scorer."""

    _assert_frozen_scorer()
    predictions_registry = _load_json(predictions_path)
    observations = build_observations(
        predictions_registry["predictions"],
        _load_json(fa_target_path),
        _load_json(trap_target_path),
    )
    observations_path.parent.mkdir(parents=True, exist_ok=True)
    observations_path.write_text(
        json.dumps(observations, indent=2, sort_keys=True), encoding="utf-8"
    )

    scorer = _load_scorer()
    scorer.main(predictions_path.resolve().relative_to(REPO_ROOT), observations_path, scores_path)

    scores = _load_json(scores_path)
    aggregate = scores["payload"]["aggregate"]
    print(
        "gt7_transfer_scores "
        f"observations={len(observations)} "
        f"pass={aggregate['n_pass']} fail={aggregate['n_fail']} "
        f"no_prediction={aggregate['n_no_prediction']} "
        f"unobserved={aggregate['n_unobserved']} total={aggregate['total']} "
        f"wrote={scores_path}"
    )


def build_observations(
    predictions: list[dict[str, Any]],
    fa_target: dict[str, Any],
    trap_target: dict[str, Any],
) -> dict[str, float | None]:
    """Resolve every prediction cell from target-family rows and grid metadata."""

    row_indexes = {
        "fa1f": _row_index(fa_target),
        "trap": _row_index(trap_target),
    }
    observations: dict[str, float | None] = {}
    for prediction in predictions:
        family = prediction["target_family"]
        if family not in row_indexes:
            raise ValueError(f"unsupported target_family: {family!r}")
        key = _grid_key(prediction["grid_point"])
        try:
            row = row_indexes[family][key]
        except KeyError as error:
            raise ValueError(f"no target row for {family} grid point {key}") from error
        observations[prediction["cell_id"]] = _readout_value(row, prediction["readout_id"])
    return observations


def _row_index(target: dict[str, Any]) -> dict[tuple[str, str, str, int], dict[str, Any]]:
    rows = target["payload"]["hump_surface_exact"]
    index: dict[tuple[str, str, str, int], dict[str, Any]] = {}
    for row in rows:
        key = _grid_key(row)
        if key in index:
            raise ValueError(f"duplicate target row for grid point {key}")
        index[key] = row
    return index


def _grid_key(cell: dict[str, Any]) -> tuple[str, str, str, int]:
    return (
        cell["epsilon_hi"],
        cell["epsilon_lo"],
        cell["epsilon_mid"],
        int(cell["t_w"]),
    )


def _readout_value(row: dict[str, Any], readout_id: str) -> float | None:
    value = row[readout_id]
    if value is None:
        return None
    if readout_id in {"t_K", "t_peak"}:
        return float(value)
    if readout_id == "hump_height":
        return float(str_to_rational(value))
    raise ValueError(f"unsupported readout_id: {readout_id!r}")


def _assert_frozen_scorer() -> None:
    actual_hash = _sha256_file(SCORER_PATH)
    if actual_hash != FROZEN_SCORER_HASH:
        raise RuntimeError(
            f"score_transfer.py hash mismatch: expected {FROZEN_SCORER_HASH}, got {actual_hash}"
        )


def _load_scorer() -> ModuleType:
    spec = importlib.util.spec_from_file_location("score_transfer", SCORER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load scorer module from {SCORER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise TypeError(f"{path} did not contain a JSON object")
    return data


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


if __name__ == "__main__":
    main()
