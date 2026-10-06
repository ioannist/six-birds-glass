"""Build the GT7 East reference readout artifact."""

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
from sixbirds_glass.lenses.catalog import l_energy  # noqa: E402
from sixbirds_glass.models.east import build_east_kernel, east_stationary  # noqa: E402
from sixbirds_glass.models.grid import DEFAULT_EPSILON_GRID  # noqa: E402
from sixbirds_glass.models.mc_engine import (  # noqa: E402
    cross_validate_at_n10,
    seed_block_bands,
    simulate_trajectories,
)
from sixbirds_glass.pipeline.cd import closure_deficit_float  # noqa: E402
from sixbirds_glass.pipeline.dimension import (  # noqa: E402
    buyback_curve,
    declared_scalar_pool,
    fiber_histogram,
    max_fiber_size,
)
from sixbirds_glass.pipeline.kovacs_hump import (  # noqa: E402
    DEFAULT_DENOMINATOR_BIT_CAP,
    analyze_hump_trace,
)
from sixbirds_glass.pipeline.kovacs_witness import build_kovacs_moment_witness  # noqa: E402

ExactVector = list[Fraction]
KernelItems = list[list[tuple[int, Fraction]]]

REGISTRY_PATH = REPO_ROOT / "registry" / "readouts.json"
OUTPUT_PATH = REPO_ROOT / "artifacts" / "gt7_constants" / "east_reference.json"
TAU_PROBE = 60
MC_SPOTCHECK_N = 16
MC_SPOTCHECK_N_TRAJ = 20_000


def main(output_path: Path = OUTPUT_PATH, *, registry_path: Path = REGISTRY_PATH) -> None:
    artifact = build_artifact(registry_path=registry_path)
    _validate_artifact(artifact)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(artifact, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    print(
        "gt7_east_reference "
        f"exact_rows={len(artifact['payload']['hump_surface_exact'])} "
        f"mc_rows={len(artifact['payload']['hump_surface_mc_spotcheck']['rows'])} "
        f"readouts_freeze_hash={artifact['readouts_freeze_hash']} "
        f"wrote={output_path}"
    )


def build_artifact(*, registry_path: Path = REGISTRY_PATH) -> dict[str, Any]:
    registry = _load_registry(registry_path)
    readouts_hash = str(registry["content_hash"])
    epsilon_grid = list(registry["grid_products"]["epsilon_grid"])
    print("building hump_surface_exact", flush=True)
    hump_surface_exact = _hump_surface_exact(registry)
    print("building hump_surface_mc_spotcheck", flush=True)
    hump_surface_mc_spotcheck = _hump_surface_mc_spotcheck()
    print("building n10_cross_validation", flush=True)
    n10_cross_validation = _n10_cross_validation()
    print("building memdim_profile", flush=True)
    memdim_profile = _memdim_profile(registry)
    print("building deficit_decay", flush=True)
    deficit_decay = _deficit_decay(registry)
    payload = {
        "hump_surface_exact": hump_surface_exact,
        "hump_surface_mc_spotcheck": hump_surface_mc_spotcheck,
        "n10_cross_validation": n10_cross_validation,
        "memdim_profile": memdim_profile,
        "deficit_decay": deficit_decay,
    }
    return {
        "artifact_kind": "constants_readout",
        "claim_id": "GT7.east_reference",
        "config_hash": readouts_hash,
        "config_path": str(registry_path.relative_to(REPO_ROOT)),
        "code_version": _code_version(),
        "claim_grade": "run_only_readout",
        "evidence_type": "monte_carlo_frozen_seeds",
        "readouts_freeze_hash": readouts_hash,
        "tau_probe": TAU_PROBE,
        "freeze_refs": [readouts_hash],
        "quantifier_domain": {
            "model_families": ["east"],
            "N_values": [10, MC_SPOTCHECK_N],
            "epsilon_grid": epsilon_grid,
            "lens_catalog_hash": config_hash({"lens": "L_energy"}),
            "protocol_catalog_hash": config_hash(
                registry["grid_products"]["protocol_catalog_instances"]
            ),
        },
        "nonclaims": [
            "run-only readouts, not a fitted scaling law",
            (
                "East reference only; no transfer claim without a scored FA/trap target run "
                "and a pre-registered prediction."
            ),
        ],
        "payload": payload,
    }


def _hump_surface_exact(registry: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    quench_cache: dict[tuple[Fraction, Fraction, int], tuple[ExactVector, str | None]] = {}
    cells = registry["grid_products"]["hump_surface_cells"]
    for index, cell in enumerate(cells, start=1):
        if index == 1 or index % 8 == 0 or index == len(cells):
            print(f"  exact cell {index}/{len(cells)}", flush=True)
        epsilon_hi = str_to_rational(cell["epsilon_hi"])
        epsilon_lo = str_to_rational(cell["epsilon_lo"])
        epsilon_mid = str_to_rational(cell["epsilon_mid"])
        t_w = int(cell["t_w"])
        quench_key = (epsilon_hi, epsilon_lo, t_w)
        if quench_key not in quench_cache:
            quench_cache[quench_key] = _exact_quench_distribution(epsilon_hi, epsilon_lo, t_w)
        quench_distribution, quench_abort = quench_cache[quench_key]
        result = _exact_probe_analysis(quench_distribution, quench_abort, epsilon_mid)
        rows.append(
            {
                "epsilon_hi": cell["epsilon_hi"],
                "epsilon_lo": cell["epsilon_lo"],
                "epsilon_mid": cell["epsilon_mid"],
                "t_w": t_w,
                "tau_probe": TAU_PROBE,
                "N": 10,
                "evidence_type": "exact_rational",
                "found": result["found"],
                "t_K": result["t_K"],
                "t_peak": result["t_peak"],
                "hump_height": (
                    None
                    if result["hump_height"] is None
                    else rational_to_str(result["hump_height"])
                ),
                "e_eq": rational_to_str(result["e_eq"]),
                "miss_reason": result["miss_reason"],
                "abort_reason": result["abort_reason"],
            }
        )
    return rows


def _exact_quench_distribution(
    epsilon_hi: Fraction,
    epsilon_lo: Fraction,
    t_w: int,
) -> tuple[ExactVector, str | None]:
    distribution = _stationary_vector(10, epsilon_hi)
    kernel_lo = _kernel_items(10, epsilon_lo)
    for step in range(1, t_w + 1):
        distribution = _push_vector(distribution, kernel_lo)
        abort_reason = _denominator_abort_reason(distribution, "quench", step)
        if abort_reason is not None:
            return distribution, abort_reason
    return distribution, None


def _exact_probe_analysis(
    quench_distribution: ExactVector,
    quench_abort: str | None,
    epsilon_mid: Fraction,
) -> dict[str, Any]:
    e_eq = _equilibrium_energy(10, epsilon_mid)
    if quench_abort is not None:
        return {
            "found": False,
            "t_K": None,
            "t_peak": None,
            "hump_height": None,
            "e_eq": e_eq,
            "miss_reason": None,
            "abort_reason": quench_abort,
        }

    distribution = list(quench_distribution)
    trace = [_energy_expectation_vector(distribution, 10)]
    kernel_mid = _kernel_items(10, epsilon_mid)
    for step in range(1, TAU_PROBE + 1):
        distribution = _push_vector(distribution, kernel_mid)
        abort_reason = _denominator_abort_reason(distribution, "probe", step)
        if abort_reason is not None:
            return {
                "found": False,
                "t_K": None,
                "t_peak": None,
                "hump_height": None,
                "e_eq": e_eq,
                "miss_reason": None,
                "abort_reason": abort_reason,
            }
        trace.append(_energy_expectation_vector(distribution, 10))

    analysis = analyze_hump_trace(trace, e_eq)
    return {
        "found": analysis.found,
        "t_K": analysis.t_k,
        "t_peak": analysis.t_peak,
        "hump_height": analysis.hump_height,
        "e_eq": e_eq,
        "miss_reason": analysis.miss_reason,
        "abort_reason": None,
    }


def _hump_surface_mc_spotcheck() -> dict[str, Any]:
    rows = []
    epsilon_hi = Fraction(7, 10)
    epsilon_lo = Fraction(1, 10)
    t_w = 20
    for index, epsilon_mid in enumerate(DEFAULT_EPSILON_GRID):
        seed = 70_000 + index
        row = _mc_spotcheck_row(epsilon_hi, epsilon_lo, epsilon_mid, t_w, seed)
        rows.append(row)
    return {
        "coverage": (
            "Fixed slice epsilon_hi=7/10, epsilon_lo=1/10, t_w=20, N=16, "
            "tau_probe=60; epsilon_mid sweeps all 7 grid points. Broader N=16/20 "
            "coverage across the full 56-cell grid is not computed in this F2 artifact."
        ),
        "rows": rows,
    }


def _mc_spotcheck_row(
    epsilon_hi: Fraction,
    epsilon_lo: Fraction,
    epsilon_mid: Fraction,
    t_w: int,
    seed: int,
) -> dict[str, Any]:
    rng = np.random.default_rng(seed)
    initial = _sample_east_stationary_configs(MC_SPOTCHECK_N, epsilon_hi, MC_SPOTCHECK_N_TRAJ, rng)
    quench = simulate_trajectories(
        "east", MC_SPOTCHECK_N, epsilon_lo, initial, t_w, seed + 1, record_every=t_w
    )
    mid = simulate_trajectories(
        "east",
        MC_SPOTCHECK_N,
        epsilon_mid,
        quench[-1],
        TAU_PROBE,
        seed + 2,
    )
    mean_trace, band = seed_block_bands(mid, MC_SPOTCHECK_N, n_blocks=10)
    e_eq = Fraction(MC_SPOTCHECK_N) * epsilon_mid / (Fraction(1) + epsilon_mid)
    analysis = analyze_hump_trace(
        [Fraction.from_float(float(value)) for value in mean_trace],
        e_eq,
    )
    return {
        "epsilon_mid": rational_to_str(epsilon_mid),
        "N": MC_SPOTCHECK_N,
        "evidence_type": "monte_carlo_frozen_seeds",
        "n_traj": MC_SPOTCHECK_N_TRAJ,
        "seed": seed,
        "found": analysis.found,
        "t_K": analysis.t_k,
        "t_peak": analysis.t_peak,
        "hump_height": None if analysis.hump_height is None else float(analysis.hump_height),
        "mc_band_at_peak": None if analysis.t_peak is None else float(band[analysis.t_peak]),
        "e_eq": float(e_eq),
    }


def _n10_cross_validation() -> list[dict[str, object]]:
    return [
        cross_validate_at_n10(
            "east",
            Fraction(7, 10),
            Fraction(1, 10),
            t_w=20,
            n_traj=5_000,
            seed=30_001,
        ),
        cross_validate_at_n10(
            "east",
            Fraction(3, 5),
            Fraction(1, 5),
            t_w=20,
            n_traj=5_000,
            seed=30_002,
        ),
    ]


def _memdim_profile(registry: dict[str, Any]) -> list[dict[str, Any]]:
    profiles: list[dict[str, Any]] = []
    for instance in registry["grid_products"]["protocol_catalog_instances"]:
        instance_id = instance["instance_id"]
        if instance["constructor"] == "p_quench":
            profiles.append(
                {
                    "instance_id": instance_id,
                    "status": "not_applicable",
                    "reason": (
                        "p_quench has no epsilon_mid probe leg; the current memory-dimension "
                        "witness pipeline requires a Kovacs-shaped crossing hump to construct "
                        "the split-pair witness. Extending it to plain quench protocols is out "
                        "of scope for this packet."
                    ),
                }
            )
            continue
        params = instance["params"]
        witness = build_kovacs_moment_witness(
            10,
            str_to_rational(params["epsilon_hi"]),
            str_to_rational(params["epsilon_lo"]),
            str_to_rational(params["epsilon_mid"]),
            int(params["t_w"]),
            int(params["tau_probe"]),
        )
        pool = declared_scalar_pool(witness.N, DEFAULT_EPSILON_GRID)
        curve = buyback_curve(
            witness.mu_k,
            witness.pi_eq,
            witness.N,
            witness.future_value_mu_k,
            witness.future_value_pi_eq,
            pool,
            max_budget=2,
        )
        profiles.append(
            {
                "instance_id": instance_id,
                "N": 10,
                "max_fiber_size": max_fiber_size(witness.package, "mid"),
                "fiber_histogram": {
                    _signature_key(signature): count
                    for signature, count in fiber_histogram(witness.package, "mid").items()
                },
                "buyback_envelope": {
                    str(budget): rational_to_str(value) for budget, value in curve.envelope.items()
                },
                "saturation_budget": curve.saturation_budget,
            }
        )
    return profiles


def _deficit_decay(registry: dict[str, Any]) -> dict[str, Any]:
    tau_ladder = [int(value) for value in registry["grid_products"]["tau_ladder"]]
    epsilon_mid = Fraction(2, 5)
    kernel = build_east_kernel(10, epsilon_mid)
    stationary = east_stationary(10, epsilon_mid)
    cd_values = {
        str(tau): closure_deficit_float(10, kernel, stationary, tau, l_energy) for tau in tau_ladder
    }
    secant_slope = (cd_values["8"] - cd_values["1"]) / 7.0
    return {
        "epsilon_mid": "2/5",
        "N": 10,
        "lens": "L_energy",
        "tau_ladder": tau_ladder,
        "cd_values": cd_values,
        "secant_slope": secant_slope,
        "evidence_type": "float64_deterministic",
    }


@cache
def _stationary_vector(N: int, epsilon: Fraction) -> ExactVector:
    stationary = east_stationary(N, epsilon)
    return [stationary[state] for state in range(1 << N)]


@cache
def _kernel_items(N: int, epsilon: Fraction) -> KernelItems:
    kernel = build_east_kernel(N, epsilon)
    return [list(kernel.rows[state].items()) for state in range(kernel.state_count)]


def _push_vector(distribution: ExactVector, rows: KernelItems) -> ExactVector:
    result = [Fraction(0) for _ in distribution]
    for source, mass in enumerate(distribution):
        if mass == 0:
            continue
        for target, probability in rows[source]:
            result[target] += mass * probability
    return result


def _equilibrium_energy(N: int, epsilon: Fraction) -> Fraction:
    return _energy_expectation_vector(_stationary_vector(N, epsilon), N)


def _energy_expectation_vector(distribution: ExactVector, N: int) -> Fraction:
    return sum(
        (mass * l_energy(state, N) for state, mass in enumerate(distribution)),
        start=Fraction(0),
    )


def _denominator_abort_reason(
    distribution: ExactVector,
    leg_name: str,
    step: int,
) -> str | None:
    observed = max((value.denominator.bit_length() for value in distribution), default=0)
    if observed > DEFAULT_DENOMINATOR_BIT_CAP:
        return (
            f"max_denominator_bits={observed} exceeded cap={DEFAULT_DENOMINATOR_BIT_CAP} "
            f"during {leg_name} step {step}"
        )
    return None


def _sample_east_stationary_configs(
    N: int,
    epsilon: Fraction,
    n_traj: int,
    rng: np.random.Generator,
) -> np.ndarray:
    stationary = east_stationary(N, epsilon)
    weights = np.array([float(stationary[state]) for state in range(1 << N)], dtype=np.float64)
    return rng.choice(1 << N, size=n_traj, p=weights).astype(np.uint32)


def _signature_key(signature: tuple[Fraction, ...]) -> str:
    return "|".join(rational_to_str(value) for value in signature)


def _load_registry(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        registry = json.load(handle)
    if not isinstance(registry, dict):
        raise TypeError(f"{path} did not contain a JSON object")
    return registry


def _validate_artifact(artifact: dict[str, Any]) -> None:
    schema = _schema("artifact_envelope.schema.json")
    Draft202012Validator(schema).validate(artifact)


def _schema(filename: str) -> dict[str, Any]:
    path = REPO_ROOT / "design" / "schemas" / filename
    with path.open(encoding="utf-8") as handle:
        schema = json.load(handle)
    if not isinstance(schema, dict):
        raise TypeError(f"{path} did not contain a JSON object")
    return schema


def _code_version() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return "unknown"
    return result.stdout.strip()


if __name__ == "__main__":
    main()
