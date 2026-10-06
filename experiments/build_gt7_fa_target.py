"""Build the GT7 FA-1f target readout artifact."""

from __future__ import annotations

import json
import subprocess
import sys
from fractions import Fraction
from functools import cache
from pathlib import Path
from typing import Any

import numpy as np
from jsonschema import Draft202012Validator

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from sixbirds_glass.io.config import config_hash  # noqa: E402
from sixbirds_glass.io.rational import rational_to_str, str_to_rational  # noqa: E402
from sixbirds_glass.models.fa import build_fa_kernel, fa_energy, fa_stationary  # noqa: E402
from sixbirds_glass.models.grid import DEFAULT_EPSILON_GRID  # noqa: E402
from sixbirds_glass.models.mc_engine import (  # noqa: E402
    cross_validate_at_n10,
    seed_block_bands,
    simulate_trajectories,
)
from sixbirds_glass.pipeline.kovacs_hump import (  # noqa: E402
    analyze_hump_trace,
    run_kovacs_trace_exact,
)

REGISTRY_PATH = REPO_ROOT / "registry" / "readouts.json"
PREDICTIONS_PATH = REPO_ROOT / "registry" / "predictions_f5e2a3332a2191a2.json"
EAST_REFERENCE_PATH = REPO_ROOT / "artifacts" / "gt7_constants" / "east_reference.json"
OUTPUT_PATH = REPO_ROOT / "artifacts" / "gt7_constants" / "fa_target.json"
TAU_PROBE = 60
MC_N = 16
MC_N_TRAJ = 20_000


def main(output_path: Path = OUTPUT_PATH) -> None:
    artifact = build_artifact()
    _validate_artifact(artifact)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(artifact, indent=2, sort_keys=True), encoding="utf-8")
    print(
        "gt7_fa_target "
        f"exact_rows={len(artifact['payload']['hump_surface_exact'])} "
        f"mc_rows={len(artifact['payload']['hump_surface_mc_spotcheck']['rows'])} "
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
        "claim_id": "GT7.fa_target",
        "config_hash": readouts_hash,
        "config_path": str(REGISTRY_PATH.relative_to(REPO_ROOT)),
        "code_version": _code_version(),
        "claim_grade": "run_only_readout",
        "evidence_type": "monte_carlo_frozen_seeds",
        "readouts_freeze_hash": readouts_hash,
        "freeze_refs": [readouts_hash, predictions_hash],
        "tau_probe": TAU_PROBE,
        "scope_note": (
            "This implementation's cross-family transfer claim covers hump_surface readouts "
            "(t_K, t_peak, hump_height) only; memdim_profile and deficit_decay are computed "
            "for the East reference only, with no cross-family transfer prediction attempted "
            "in this pass."
        ),
        "quantifier_domain": {
            "model_families": ["fa1f"],
            "N_values": [10, MC_N],
            "epsilon_grid": epsilon_grid,
            "lens_catalog_hash": config_hash({"lens": "L_energy"}),
            "protocol_catalog_hash": config_hash(
                registry["grid_products"]["protocol_catalog_instances"]
            ),
        },
        "nonclaims": [
            "FA target run only; scoring is deferred to the frozen transfer scorer.",
            "memdim_profile and deficit_decay transfer are out of scope for this target artifact.",
        ],
        "payload": {
            "hump_surface_exact": _hump_surface_exact(registry),
            "hump_surface_mc_spotcheck": _mc_spotcheck(),
            "n10_cross_validation": _cross_validation_from_east_reference(),
        },
    }


def _hump_surface_exact(registry: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    cells = registry["grid_products"]["hump_surface_cells"]
    for index, cell in enumerate(cells, start=1):
        if index == 1 or index % 8 == 0 or index == len(cells):
            print(f"  fa exact cell {index}/{len(cells)}", flush=True)
        epsilon_hi = str_to_rational(cell["epsilon_hi"])
        epsilon_lo = str_to_rational(cell["epsilon_lo"])
        epsilon_mid = str_to_rational(cell["epsilon_mid"])
        t_w = int(cell["t_w"])
        analysis = run_kovacs_trace_exact(
            lambda epsilon: _cached_fa_kernel(10, epsilon),
            lambda epsilon: _cached_fa_stationary(10, epsilon),
            lambda state: fa_energy(state, 10),
            epsilon_hi,
            epsilon_lo,
            epsilon_mid,
            t_w,
            TAU_PROBE,
        )
        rows.append(_analysis_row("fa", cell, analysis, N=10))
    return rows


def _mc_spotcheck() -> dict[str, Any]:
    rows = []
    epsilon_hi = Fraction(7, 10)
    epsilon_lo = Fraction(1, 10)
    t_w = 20
    for index, epsilon_mid in enumerate(DEFAULT_EPSILON_GRID):
        seed = 80_000 + index
        rows.append(_mc_row(epsilon_hi, epsilon_lo, epsilon_mid, t_w, seed))
    return {
        "coverage": (
            "Fixed slice epsilon_hi=7/10, epsilon_lo=1/10, t_w=20, N=16, "
            "tau_probe=60; epsilon_mid sweeps all 7 grid points. Broader N=16/20 "
            "coverage across the full 56-cell grid is not computed in this F4 artifact."
        ),
        "rows": rows,
    }


def _mc_row(
    epsilon_hi: Fraction,
    epsilon_lo: Fraction,
    epsilon_mid: Fraction,
    t_w: int,
    seed: int,
) -> dict[str, Any]:
    rng = np.random.default_rng(seed)
    initial = _sample_fa_stationary_configs(MC_N, epsilon_hi, MC_N_TRAJ, rng)
    quench = simulate_trajectories("fa", MC_N, epsilon_lo, initial, t_w, seed + 1, record_every=t_w)
    mid = simulate_trajectories("fa", MC_N, epsilon_mid, quench[-1], TAU_PROBE, seed + 2)
    mean_trace, band = seed_block_bands(mid, MC_N, n_blocks=10)
    e_eq = Fraction(MC_N) * epsilon_mid / (Fraction(1) + epsilon_mid)
    analysis = analyze_hump_trace([Fraction.from_float(float(value)) for value in mean_trace], e_eq)
    cell = {
        "epsilon_hi": rational_to_str(epsilon_hi),
        "epsilon_lo": rational_to_str(epsilon_lo),
        "epsilon_mid": rational_to_str(epsilon_mid),
        "t_w": t_w,
    }
    return {
        "epsilon_mid": rational_to_str(epsilon_mid),
        "N": MC_N,
        "cell_ids": _cell_ids("fa", cell),
        "evidence_type": "monte_carlo_frozen_seeds",
        "n_traj": MC_N_TRAJ,
        "seed": seed,
        "found": analysis.found,
        "t_K": analysis.t_k,
        "t_peak": analysis.t_peak,
        "hump_height": None if analysis.hump_height is None else float(analysis.hump_height),
        "mc_band_at_peak": None if analysis.t_peak is None else float(band[analysis.t_peak]),
        "e_eq": float(e_eq),
    }


def _cross_validation_from_east_reference() -> list[dict[str, object]]:
    east = _load_json(EAST_REFERENCE_PATH)
    rows = []
    for index, entry in enumerate(east["payload"]["n10_cross_validation"]):
        rows.append(
            cross_validate_at_n10(
                "fa",
                str_to_rational(entry["epsilon_hi"]),
                str_to_rational(entry["epsilon_lo"]),
                int(entry["t_w"]),
                n_traj=5_000,
                seed=41_000 + index,
            )
        )
    return rows


def _sample_fa_stationary_configs(
    N: int, epsilon: Fraction, n_traj: int, rng: np.random.Generator
) -> np.ndarray:
    stationary = fa_stationary(N, epsilon)
    weights = np.array([float(stationary[state]) for state in range(1 << N)], dtype=np.float64)
    return rng.choice(1 << N, size=n_traj, p=weights).astype(np.uint32)


@cache
def _cached_fa_kernel(N: int, epsilon: Fraction):
    return build_fa_kernel(N, epsilon)


@cache
def _cached_fa_stationary(N: int, epsilon: Fraction):
    return fa_stationary(N, epsilon)


def _analysis_row(prefix: str, cell: dict[str, Any], analysis, *, N: int) -> dict[str, Any]:
    return {
        "epsilon_hi": cell["epsilon_hi"],
        "epsilon_lo": cell["epsilon_lo"],
        "epsilon_mid": cell["epsilon_mid"],
        "t_w": int(cell["t_w"]),
        "tau_probe": TAU_PROBE,
        "N": N,
        "cell_id_prefix": prefix,
        "cell_ids": _cell_ids(prefix, cell),
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


def _cell_ids(prefix: str, cell: dict[str, Any]) -> dict[str, str]:
    suffix = "_".join(
        [
            _id_epsilon(cell["epsilon_hi"]),
            _id_epsilon(cell["epsilon_lo"]),
            _id_epsilon(cell["epsilon_mid"]),
            str(cell["t_w"]),
        ]
    )
    return {
        "t_K": f"{prefix}:t_K:{suffix}",
        "t_peak": f"{prefix}:t_peak:{suffix}",
        "hump_height": f"{prefix}:hump_height:{suffix}",
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
