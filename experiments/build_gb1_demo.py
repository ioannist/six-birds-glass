"""Build the GB1 temperature-protocol-trap demonstration artifact."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from sixbirds_glass.io.config import config_hash  # noqa: E402
from sixbirds_glass.pipeline.protocol_trap import (  # noqa: E402
    FloatKernel,
    candidate_measure,
    epr,
    gibbs_measure,
    heat_bath_resample_kernel,
    lifted_kernel,
    mixed_square_affinity_from_energy,
    mixed_square_affinity_from_kernel,
    path_kl_enumerate,
    pseudo_epr_boundary_term,
    stationary_distribution,
)

OUTPUT_PATH = REPO_ROOT / "artifacts" / "gb1_demo.json"
OPEN_OBLIGATION = (
    "converting the clock-path expectation of the moving-reference telescoping boundary "
    "into the unconditional per-step KL envelope for arbitrary evolving state laws, "
    "without an additional domination or stationarity assumption"
)


def main(output_path: Path = OUTPUT_PATH) -> None:
    """Write the GB1 demo artifact."""

    artifact = build_artifact()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(artifact, indent=2, sort_keys=True), encoding="utf-8")
    payload = artifact["payload"]
    print(
        "gb1_demo "
        f"bound_rate={payload['three_state_demo']['bound_rate']:.15g} "
        f"stationary_epr={payload['three_state_demo']['stationary_epr']:.15g} "
        f"wrote={output_path}"
    )


def build_artifact() -> dict[str, Any]:
    """Return the GB1 demonstration payload."""

    energies = _demo_energies()
    temperatures = {0: 3.0, 1: 1.0}
    pis = {
        phase: gibbs_measure(energies, temperature) for phase, temperature in temperatures.items()
    }
    clock, clock_stationary = _reversible_clock()
    alpha = 1.0 / 3.0
    kernels = {phase: heat_bath_resample_kernel(pi) for phase, pi in pis.items()}
    lifted = lifted_kernel(kernels, clock, alpha)
    stationary = stationary_distribution(lifted)
    bound_rate = pseudo_epr_boundary_term(pis, clock_stationary, clock, alpha)
    candidate_epr = epr(lifted, candidate_measure(pis, clock_stationary))
    stationary_epr = epr(lifted, stationary)

    common_temperatures = {0: 2.0, 1: 2.0}
    common_pis = {
        phase: gibbs_measure(energies, temperature)
        for phase, temperature in common_temperatures.items()
    }
    common_kernels = {phase: heat_bath_resample_kernel(pi) for phase, pi in common_pis.items()}
    common_lifted = lifted_kernel(common_kernels, clock, alpha)
    common_stationary = stationary_distribution(common_lifted)

    energy_affinity = mixed_square_affinity_from_energy(
        energies, state=0, target_state=1, temperature=temperatures, phase=0, target_phase=1
    )
    kernel_affinity = mixed_square_affinity_from_kernel(
        lifted, state=0, target_state=1, phase=0, target_phase=1, state_count_x=3
    )

    payload = {
        "artifact_status": "phase2_math_demo",
        "note": "GB1 demonstration artifact; not a GT-claim certificate.",
        "math_note": "math/gb1_temperature_trap.md",
        "pseudo_epr_identity": {
            "candidate_epr": candidate_epr,
            "boundary_rate": bound_rate,
            "absolute_error": abs(candidate_epr - bound_rate),
        },
        "three_state_demo": {
            "energies": energies,
            "temperatures": temperatures,
            "alpha": alpha,
            "bound_rate": bound_rate,
            "stationary_epr": stationary_epr,
            "sigma_vs_bound": [
                _sigma_bound_row(lifted, stationary, horizon, bound_rate) for horizon in (1, 2, 3)
            ],
        },
        "common_temperature_recovery": {
            "temperatures": common_temperatures,
            "boundary_rate": pseudo_epr_boundary_term(common_pis, clock_stationary, clock, alpha),
            "stationary_epr": epr(common_lifted, common_stationary),
        },
        "mixed_square_affinity": {
            "energy_formula": energy_affinity,
            "kernel_log_ratio": kernel_affinity,
            "absolute_error": abs(energy_affinity - kernel_affinity),
        },
        "open_obligation": OPEN_OBLIGATION,
    }
    return {
        "artifact_kind": "math_demo",
        "claim_id": "GB1.temperature_protocol_trap.demo",
        "config_hash": config_hash(
            {"energies": energies, "temperatures": temperatures, "alpha": alpha}
        ),
        "code_version": _code_version(),
        "claim_grade": "recognition",
        "evidence_type": "float64_deterministic",
        "quantifier_domain": {
            "model_families": ["finite_protocol_trap_demo"],
            "N_values": [],
            "epsilon_grid": [],
            "lens_catalog_hash": config_hash({"lens": "identity_state_energy"}),
            "protocol_catalog_hash": config_hash({"clock_rows": clock.rows, "alpha": alpha}),
        },
        "nonclaims": [
            (
                "GB1 demo records a pseudo-EPR identity and finite numerical check, "
                "not a closed general theorem."
            ),
            (
                "The open obligation remains filed in the payload and is not "
                "discharged by this artifact."
            ),
        ],
        "payload": payload,
    }


def _code_version() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=REPO_ROOT,
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def _sigma_bound_row(
    lifted: FloatKernel, stationary: dict[int, float], horizon: int, bound_rate: float
) -> dict[str, float | int | bool]:
    sigma = path_kl_enumerate(lifted, stationary, horizon)
    bound = horizon * bound_rate
    return {"T": horizon, "sigma": sigma, "bound": bound, "holds": sigma <= bound + 1e-12}


def _demo_energies() -> dict[int, float]:
    return {0: 0.0, 1: 1.0, 2: 2.0}


def _reversible_clock() -> tuple[FloatKernel, dict[int, float]]:
    return (
        FloatKernel(
            state_count=2,
            rows={
                0: {0: 0.8, 1: 0.2},
                1: {0: 0.2, 1: 0.8},
            },
        ),
        {0: 0.5, 1: 0.5},
    )


if __name__ == "__main__":
    main()
