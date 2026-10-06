"""Separate limiting pressure, true finite conditioning and killed diagnostics."""

from __future__ import annotations

import json
import sys
from dataclasses import asdict
from fractions import Fraction
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from sixbirds_glass.extension.disintegration import conditional_pressure_bounds  # noqa: E402
from sixbirds_glass.extension.pressure import pressure_bounds  # noqa: E402
from sixbirds_glass.io.config import config_hash, load_config  # noqa: E402
from sixbirds_glass.io.log_bounds import log_bounds  # noqa: E402
from sixbirds_glass.lenses.catalog import l_energy  # noqa: E402
from sixbirds_glass.models.east import build_east_kernel, east_stationary  # noqa: E402
from sixbirds_glass.models.kernels import strongly_connected  # noqa: E402

CONFIG_PATH = REPO_ROOT / "configs/gt6_shell_witness_n8.json"
OUTPUT_PATH = REPO_ROOT / "math/gt6_pressure_certificate.json"


def build_certificate(comparison_vector: tuple[Fraction, ...] | None = None) -> dict[str, Any]:
    config = load_config(CONFIG_PATH)
    N = int(config["model"]["N"])
    epsilon = Fraction(config["protocol"]["word"][2]["epsilon"])
    tilt = Fraction(1, 5)
    kernel = build_east_kernel(N, epsilon)
    pi = east_stationary(N, epsilon)
    limiting = pressure_bounds(kernel, l_energy, N, tilt, vector=comparison_vector)
    primitive = strongly_connected(kernel) and all(
        kernel.rows[x].get(x, 0) > 0 for x in range(kernel.state_count)
    )
    if not primitive:
        raise ValueError("source kernel does not verify the finite primitive comparison premise")
    killed_rows = []
    weighted_lower = weighted_upper = Fraction(0)
    for energy in range(N + 1):
        fiber = tuple(x for x in range(kernel.state_count) if l_energy(x, N) == energy)
        if any(
            source != target and probability > 0 and l_energy(target, N) == energy
            for source in fiber
            for target, probability in kernel.rows[source].items()
        ):
            raise ValueError("within-energy restriction is not diagonal")
        diagonal = max(kernel.rows[x][x] for x in fiber)
        weight = sum((pi[x] for x in fiber), Fraction(0))
        lo, hi = log_bounds(diagonal)
        lo, hi = lo + tilt * energy, hi + tilt * energy
        weighted_lower += weight * lo
        weighted_upper += weight * hi
        killed_rows.append(
            {
                "energy": energy,
                "weight": str(weight),
                "max_diagonal": str(diagonal),
                "limiting_pressure_interval": [str(lo), str(hi)],
            }
        )
    killed_gap = (
        limiting.pressure_lower - weighted_upper,
        limiting.pressure_upper - weighted_lower,
    )
    if killed_gap[0] <= Fraction(1, 2):
        raise ValueError("killed-pressure contrast lacks its declared strict margin")
    rows = []
    for n in range(1, 9):
        base, strata, gap = conditional_pressure_bounds(kernel, pi, l_energy, l_energy, N, tilt, n)
        if gap[0] < Fraction(1, 1000):
            raise ValueError("finite conditional contrast lacks the declared certified margin")
        rows.append(
            {
                "horizon": n,
                "ensemble_pressure_interval": [str(x) for x in base],
                "conditional_pressure_intervals": {
                    str(f): [str(x) for x in b] for f, b in strata.items()
                },
                "jensen_gap_interval": [str(x) for x in gap],
            }
        )
    limit_data = asdict(limiting)
    limit_data["vector"] = [str(x) for x in limiting.vector]
    for field in ("growth_lower", "growth_upper", "pressure_lower", "pressure_upper"):
        limit_data[field] = str(limit_data[field])
    return {
        "scope": {
            "N": N,
            "epsilon": str(epsilon),
            "tilt": str(tilt),
            "config_hash": config_hash(config),
            "ensemble": "stationary Gibbs comparison law, conditioned only at preparation",
        },
        "limiting_pressure": limit_data,
        "limiting_pressure_method": (
            "positive comparison vector; exact exp/log interval inequalities"
        ),
        "primitive_source_kernel_exact": primitive,
        "conditional_infinite_time_gap": "0",
        "killed_process_limiting_diagnostic": {
            "method": "diagonal principal restrictions; exact log intervals",
            "strata": killed_rows,
            "weighted_pressure_interval": [str(weighted_lower), str(weighted_upper)],
            "contrast_interval": [str(x) for x in killed_gap],
            "certified_margin": "1/2",
            "is_initial_law_conditioning": False,
        },
        "conditional_limit_reason": (
            "Finite primitive tilted transfer has the same limiting log growth for every "
            "nonzero conditional initial law; initial preparation does not change the limit."
        ),
        "finite_time_conditional_contrast": rows,
        "finite_margin": "1/1000",
        "original_killed_process_semantics": (
            "Zeroing transitions outside an energy fiber kills trajectories at exit. "
            "This is a survival-pressure diagnostic, not initial-law conditioning."
        ),
        "nonclaims": [
            "The finite Jensen contrast is already present for the stationary comparison ensemble.",
            "It is not a glass-specific strictness witness or a KL closure deficit.",
            "No positive infinite-time gap is claimed for initial-law conditioning.",
            "The original GT6 packaging-fixed-point obligation remains undischarged.",
            "The comparison vector can be selected numerically; only exact bounds certify it.",
        ],
    }


def verify_certificate(certificate: dict[str, Any]) -> None:
    # A positive comparison vector is a proof witness; its numerical selection
    # need not be reproduced. Check its exact inequalities against the source.
    vector = tuple(map(Fraction, certificate["limiting_pressure"]["vector"]))
    if certificate != build_certificate(vector):
        raise ValueError("pressure certificate differs from exact source replay")


if __name__ == "__main__":
    OUTPUT_PATH.write_text(json.dumps(build_certificate(), indent=2, sort_keys=True) + "\n")
    print("certified limiting pressure and finite conditioning; conditional limit gap is zero")
