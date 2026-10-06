"""Construct and replay a full-energy-law strictness witness on the frozen N8 run."""

from __future__ import annotations

import hashlib
import json
import sys
from dataclasses import asdict
from fractions import Fraction
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from sixbirds_glass.extension.shell import (  # noqa: E402
    SPECTRAL_GAPS_PATH,
    check_config_shell_membership,
)
from sixbirds_glass.io.config import canonical_json_bytes, config_hash, load_config  # noqa: E402
from sixbirds_glass.lenses.catalog import l_energy  # noqa: E402
from sixbirds_glass.models.east import build_east_kernel, east_stationary  # noqa: E402
from sixbirds_glass.models.kernels import strongly_connected  # noqa: E402
from sixbirds_glass.models.unconstrained import build_unconstrained_kernel  # noqa: E402
from sixbirds_glass.pipeline.dimension import buyback_curve, declared_scalar_pool  # noqa: E402
from sixbirds_glass.pipeline.energy_witness import (  # noqa: E402
    build_energy_mixture_witness_from_config,
    separating_energy_values,
)
from sixbirds_glass.pipeline.foreclosure import foreclosure_sweep  # noqa: E402
from sixbirds_glass.pipeline.packaging import (  # noqa: E402
    gibbs_prototype_rule,
    packaging_endomap,
    retention_error,
)
from sixbirds_glass.protocols.evolution import Distribution, push  # noqa: E402

CONFIG_PATH = REPO_ROOT / "configs/gt6_shell_witness_n8.json"
OUTPUT_PATH = REPO_ROOT / "math/gt6_energy_mixture_witness.json"


def build_certificate(config_path: Path = CONFIG_PATH) -> dict[str, Any]:
    config = load_config(config_path)
    membership = check_config_shell_membership(config)
    if not membership.in_shell:
        raise ValueError("source run does not satisfy the frozen shell predicate")
    w = build_energy_mixture_witness_from_config(config)
    m = w.mixtures
    sweep = foreclosure_sweep(m.plus, m.minus, w.N)
    if not sweep.all_agree:
        raise ArithmeticError("energy-definable predicate sweep failed")
    horizons = tuple(w.future_values)
    control = separating_energy_values(
        m, w.N, build_unconstrained_kernel(w.N, w.epsilon_mid), horizons
    )
    if any(left != right for left, right in control.values()):
        raise ArithmeticError("unconstrained lumpable ablation did not erase the future split")
    gaps = {h: abs(left - right) for h, (left, right) in w.future_values.items()}
    if any(gap == 0 for gap in gaps.values()):
        raise ValueError("declared finite horizon set has an unseparated future")
    pool = declared_scalar_pool(w.N, tuple(map(Fraction, config["epsilon_grid"])))
    coordinate_deltas = {
        name: coordinate(m.plus, w.N) - coordinate(m.minus, w.N)
        for name, coordinate in pool.items()
    }
    if coordinate_deltas["T_f"] != 0:
        raise ArithmeticError("energy-derived fictive-temperature descriptor separated equal laws")
    future_plus, future_minus = w.future_values[5]
    curve = buyback_curve(m.plus, m.minus, w.N, future_plus, future_minus, pool)
    energy_law = [str(m.energy_law[level]) for level in range(w.N + 1)]
    endomap = packaging_endomap(
        w.N,
        build_east_kernel(w.N, w.epsilon_mid),
        1,
        l_energy,
        gibbs_prototype_rule(w.N, w.epsilon_mid),
    )
    pi = east_stationary(w.N, w.epsilon_mid)
    irreducible = strongly_connected(endomap)
    stationary = push(pi, endomap) == pi
    if not irreducible or not stationary:
        raise ArithmeticError("packaging fixed-point obstruction failed verification")
    return {
        "certificate_kind": "full_energy_law_predictive_split",
        "claim": "The predictive energy layer strictly extends the full current energy law.",
        "proof_route": "F-III T12/T13: actual same-source split pair implies nonfactorization.",
        "scope": {
            "family": "east",
            "N": w.N,
            "boundary": "wall_up",
            "config_path": str(config_path.relative_to(REPO_ROOT)),
            "config_hash": config_hash(config),
            "config_file_sha256": hashlib.sha256(config_path.read_bytes()).hexdigest(),
            "spectral_shell_table_sha256": hashlib.sha256(
                SPECTRAL_GAPS_PATH.read_bytes()
            ).hexdigest(),
            "epsilon_hi": str(w.epsilon_hi),
            "epsilon_lo": str(w.epsilon_lo),
            "epsilon_mid": str(w.epsilon_mid),
            "quench_steps": w.t_w,
            "probe_window": w.tau_probe,
            "stop_times": list(w.stop_times),
            "future_horizons": list(horizons),
            "all_operations_inside_declared_window": max(w.stop_times) + max(gaps) <= w.tau_probe,
        },
        "shell_membership": json.loads(json.dumps(asdict(membership))),
        "construction": {
            "selector": "RREF of current energy laws; first free column; positive/negative split",
            "selector_inputs": "current energy laws only; no future readout or equilibrium target",
            "rank": m.rank,
            "free_column": m.free_column,
            "signed_null_coefficients": [str(c) for c in m.coefficients],
            "positive_stopping_weights": [str(c) for c in m.plus_weights],
            "negative_stopping_weights": [str(c) for c in m.minus_weights],
            "source_energy_laws": [
                [
                    str(
                        sum(
                            (mass for state, mass in law.items() if l_energy(state, w.N) == level),
                            Fraction(0),
                        )
                    )
                    for level in range(w.N + 1)
                ]
                for law in w.source_laws
            ],
            "history_sha256": {"h_plus": _law_hash(m.plus), "h_minus": _law_hash(m.minus)},
        },
        "object_maps": {
            "carrier": ["h_plus", "h_minus"],
            "pi0": {"h_plus": energy_law, "h_minus": energy_law},
            "pi1": {
                "h_plus": {
                    "current": energy_law,
                    "future": [str(v[0]) for v in w.future_values.values()],
                },
                "h_minus": {
                    "current": energy_law,
                    "future": [str(v[1]) for v in w.future_values.values()],
                },
            },
            "retention": "pi0 is the current-coordinate projection of pi1",
            "factorization_defect": [["h_plus", "h_minus"]],
        },
        "energy_predicate_sweep": asdict(sweep),
        "energy_scalar_buyback": {
            "probe_horizon": 5,
            "loss_definition": "sum squared error of two unit-weight source histories",
            "coordinate_differences": {
                name: str(delta) for name, delta in coordinate_deltas.items()
            },
            "raw_by_budget": {
                str(b): [
                    {
                        "coordinates": list(row["coordinates"]),
                        "loss": str(row["loss"]),
                        "resolved": row["resolved"],
                    }
                    for row in rows
                ]
                for b, rows in curve.raw_by_budget.items()
            },
            "envelope": {str(b): str(loss) for b, loss in curve.envelope.items()},
            "saturation_budget": curve.saturation_budget,
            "scope": (
                "Every energy-law-derived descriptor fails on this pair; "
                "other scalars may resolve it. No general scalar-dimension lower bound."
            ),
        },
        "future_energy": {
            str(h): {
                "value_plus": str(left),
                "value_minus": str(right),
                "absolute_gap": str(gaps[h]),
                "tv_lower_bound": str(gaps[h] / w.N),
            }
            for h, (left, right) in w.future_values.items()
        },
        "finite_window_persistence": {
            "meaning": (
                "future-energy separation at each declared horizon; not packaging fixed points"
            ),
            "horizons": list(horizons),
            "minimum_energy_gap": str(min(gaps.values())),
            "minimum_future_energy_law_tv_lower_bound": str(min(gaps.values()) / w.N),
            "source_tv_perturbation_radius_for_half_gap": str(min(gaps.values()) / (4 * w.N)),
        },
        "unconstrained_probe_ablation": {
            "operation": "replace only the probe kernel by the unconstrained heat-bath kernel",
            "source_histories_and_current_map_preserved": True,
            "future_gaps": {str(h): str(abs(a - b)) for h, (a, b) in control.items()},
        },
        "packaging_fixed_point_obstruction": {
            "tau": 1,
            "epsilon": str(w.epsilon_mid),
            "irreducible_exact_graph_check": irreducible,
            "gibbs_stationary_exact": stationary,
            "conclusion": "The packaging kernel has a unique stationary probability law.",
            "maximum_prototype_retention_error": str(
                retention_error(
                    w.N,
                    build_east_kernel(w.N, w.epsilon_mid),
                    1,
                    l_energy,
                    gibbs_prototype_rule(w.N, w.epsilon_mid),
                )
            ),
        },
        "nonclaims": [
            "No macroscopic observable-gap size or experimental detectability is claimed.",
            "No multiple exact fixed-point strata of the packaging kernel are claimed.",
            (
                "The window result is on the declared finite horizon set, "
                "not all times or an asymptotic theorem."
            ),
            (
                "The stopping clock is randomized independently at preparation; "
                "a signed law is not a preparation."
            ),
            (
                "The shell window constants remain frozen spectral diagnostics, "
                "not a metastability theorem."
            ),
        ],
    }


def verify_certificate(certificate: dict[str, Any]) -> None:
    """Replay the actual source construction, ignoring no scientific fields."""

    if certificate != build_certificate():
        raise ValueError("full-energy witness differs from exact source replay")


def _law_hash(law: Distribution) -> str:
    return hashlib.sha256(
        canonical_json_bytes({str(s): str(p) for s, p in law.items()})
    ).hexdigest()


if __name__ == "__main__":
    certificate = build_certificate()
    OUTPUT_PATH.write_text(json.dumps(certificate, indent=2, sort_keys=True) + "\n")
    print("certified full current energy-law equality, future split, and finite-window persistence")
