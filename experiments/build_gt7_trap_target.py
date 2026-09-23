"""Build the GT7 trap target readout artifact."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from sixbirds_glass.io.config import config_hash  # noqa: E402
from sixbirds_glass.io.rational import rational_to_str, str_to_rational  # noqa: E402
from sixbirds_glass.models.grid import DEFAULT_EPSILON_GRID  # noqa: E402
from sixbirds_glass.models.trap import (  # noqa: E402
    DEFAULT_TRAP_BASE_WEIGHTS,
    build_trap_kernel,
    declared_trap_weights_by_epsilon,
    trap_depth_observable,
    trap_stationary,
)
from sixbirds_glass.pipeline.kovacs_hump import run_kovacs_trace_exact  # noqa: E402

REGISTRY_PATH = REPO_ROOT / "registry" / "readouts.json"
PREDICTIONS_PATH = REPO_ROOT / "registry" / "predictions_f5e2a3332a2191a2.json"
OUTPUT_PATH = REPO_ROOT / "artifacts" / "gt7_constants" / "trap_target.json"
TAU_PROBE = 60
TRAP_COUNT = len(DEFAULT_TRAP_BASE_WEIGHTS)
FINDING = (
    "The declared trap escape vectors scale every base trap weight by a common "
    "epsilon-dependent multiplier, so trap_stationary is exactly invariant across "
    "the epsilon grid: the multiplier cancels in pi_k proportional to 1 / w_k. "
    "Temperature changes relaxation rate but not the relaxation target here, so "
    "the Kovacs-hump precondition of a probe-dependent equilibrium cannot occur; "
    "the uniform found=false sweep is the expected result."
)


def main(output_path: Path = OUTPUT_PATH) -> None:
    artifact = build_artifact()
    _validate_artifact(artifact)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(artifact, indent=2, sort_keys=True), encoding="utf-8")
    print(
        "gt7_trap_target "
        f"exact_rows={len(artifact['payload']['hump_surface_exact'])} "
        f"wrote={output_path}"
    )


def build_artifact() -> dict[str, Any]:
    registry = _load_json(REGISTRY_PATH)
    predictions = _load_json(PREDICTIONS_PATH)
    readouts_hash = str(registry["content_hash"])
    predictions_hash = str(predictions["content_hash"])
    epsilon_grid = registry["grid_products"]["epsilon_grid"]
    return {
        "artifact_kind": "constants_readout",
        "claim_id": "GT7.trap_target",
        "config_hash": readouts_hash,
        "config_path": str(REGISTRY_PATH.relative_to(REPO_ROOT)),
        "code_version": _code_version(),
        "claim_grade": "run_only_readout",
        "evidence_type": "exact_rational",
        "readouts_freeze_hash": readouts_hash,
        "freeze_refs": [readouts_hash, predictions_hash],
        "tau_probe": TAU_PROBE,
        "trap_count": TRAP_COUNT,
        "note": "Trap target is exact over M=8 traps; no Monte Carlo spot-check is needed.",
        "finding": FINDING,
        "scope_note": (
            "This implementation's cross-family transfer claim covers hump_surface readouts "
            "(t_K, t_peak, hump_height) only; memdim_profile and deficit_decay are computed "
            "for the East reference only, with no cross-family transfer prediction attempted "
            "in this pass."
        ),
        "quantifier_domain": {
            "model_families": ["trap"],
            "N_values": [],
            "epsilon_grid": epsilon_grid,
            "lens_catalog_hash": config_hash({"lens": "L_trap_depth"}),
            "protocol_catalog_hash": config_hash(
                registry["grid_products"]["protocol_catalog_instances"]
            ),
        },
        "nonclaims": [
            "Trap target run only; scoring is deferred to the frozen transfer scorer.",
            "Trap uses a declared depth observable, not East/FA spin-count energy.",
        ],
        "payload": {"hump_surface_exact": _hump_surface_exact(registry)},
    }


def _hump_surface_exact(registry: dict[str, Any]) -> list[dict[str, Any]]:
    weights_by_epsilon = declared_trap_weights_by_epsilon(DEFAULT_EPSILON_GRID)
    rows = []
    for cell in registry["grid_products"]["hump_surface_cells"]:
        epsilon_hi = str_to_rational(cell["epsilon_hi"])
        epsilon_lo = str_to_rational(cell["epsilon_lo"])
        epsilon_mid = str_to_rational(cell["epsilon_mid"])
        analysis = run_kovacs_trace_exact(
            lambda epsilon: build_trap_kernel(
                DEFAULT_TRAP_BASE_WEIGHTS, weights_by_epsilon[epsilon]
            ),
            lambda epsilon: trap_stationary(weights_by_epsilon[epsilon]),
            trap_depth_observable,
            epsilon_hi,
            epsilon_lo,
            epsilon_mid,
            int(cell["t_w"]),
            TAU_PROBE,
        )
        rows.append(_analysis_row(cell, analysis))
    return rows


def _analysis_row(cell: dict[str, Any], analysis) -> dict[str, Any]:
    return {
        "epsilon_hi": cell["epsilon_hi"],
        "epsilon_lo": cell["epsilon_lo"],
        "epsilon_mid": cell["epsilon_mid"],
        "t_w": int(cell["t_w"]),
        "tau_probe": TAU_PROBE,
        "trap_count": TRAP_COUNT,
        "cell_id_prefix": "trap",
        "cell_ids": _cell_ids(cell),
        "evidence_type": "exact_rational",
        "found": analysis.found,
        "t_K": analysis.t_k,
        "t_peak": analysis.t_peak,
        "hump_height": None
        if analysis.hump_height is None
        else rational_to_str(analysis.hump_height),
        "e_eq": None if analysis.e_eq is None else rational_to_str(analysis.e_eq),
        "miss_reason": analysis.miss_reason,
        "abort_reason": analysis.abort_reason,
    }


def _cell_ids(cell: dict[str, Any]) -> dict[str, str]:
    suffix = "_".join(
        [
            _id_epsilon(cell["epsilon_hi"]),
            _id_epsilon(cell["epsilon_lo"]),
            _id_epsilon(cell["epsilon_mid"]),
            str(cell["t_w"]),
        ]
    )
    return {
        "t_K": f"trap:t_K:{suffix}",
        "t_peak": f"trap:t_peak:{suffix}",
        "hump_height": f"trap:hump_height:{suffix}",
    }


def _id_epsilon(epsilon: str) -> str:
    return epsilon.replace("/", "-")


def _load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise TypeError(f"{path} did not contain a JSON object")
    return data


def _validate_artifact(artifact: dict[str, Any]) -> None:
    Draft202012Validator(
        _load_json(REPO_ROOT / "design/schemas/artifact_envelope.schema.json")
    ).validate(artifact)


def _code_version() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    return "unknown" if result.returncode != 0 else result.stdout.strip()


if __name__ == "__main__":
    main()
