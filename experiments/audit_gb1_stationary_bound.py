"""Certify a Gibbs counterexample and the repaired stationary GB1 upper bound."""

from __future__ import annotations

import json
import sys
from fractions import Fraction as F
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from sixbirds_glass.io.log_bounds import log_bounds  # noqa: E402
from sixbirds_glass.models.kernels import Kernel, validate_kernel_rows  # noqa: E402
from sixbirds_glass.pipeline.protocol_trap_exact import (  # noqa: E402
    epr_bounds,
    stationary_measure_exact,
)
from sixbirds_glass.protocols.evolution import dirac, hold, push  # noqa: E402

OUTPUT_PATH = REPO_ROOT / "math" / "gb1_stationary_counterexample.json"


def counterexample_data() -> tuple[Kernel, dict[int, F], list[dict[int, F]], Kernel, F]:
    """E=(0,1,2), epsilon=exp(-beta), all probabilities exactly rational."""

    epsilons = [F(4, 25), F(4, 7), F(1, 60)]
    pis = [{x: e**x / (1 + e + e**2) for x in range(3)} for e in epsilons]
    s = {0: F(1, 100_000), 1: F(1, 20), 2: F(94999, 100_000)}
    edges = [(0, 1), (0, 2), (1, 2)]
    clock_rows: dict[int, dict[int, F]] = {a: {} for a in range(3)}
    for (a, b), flux in zip(edges, [F(4, 10**6), F(4, 10**6), F(9, 10**6)], strict=True):
        clock_rows[a][b] = flux / s[a]
        clock_rows[b][a] = flux / s[b]
    for a in range(3):
        clock_rows[a][a] = 1 - sum(clock_rows[a].values(), F(0))
    clock = Kernel(3, 3, clock_rows)
    proposals = [
        [F(1, 3), F(1, 100), F(1, 1000)],
        [F(1, 100), F(1, 10), F(1, 3)],
        [F(1, 3), F(1, 10), F(1, 10)],
    ]
    kernels = []
    for pi, proposal in zip(pis, proposals, strict=True):
        rows: dict[int, dict[int, F]] = {x: {} for x in range(3)}
        for (x, y), q in zip(edges, proposal, strict=True):
            rows[x][y] = q * min(F(1), pi[y] / pi[x])
            rows[y][x] = q * min(F(1), pi[x] / pi[y])
        for x in range(3):
            rows[x][x] = 1 - sum(rows[x].values(), F(0))
        kernel = Kernel(3, 3, rows)
        validate_kernel_rows(kernel)
        assert all(pi[x] * rows[x][y] == pi[y] * rows[y][x] for x, y in edges)
        kernels.append(kernel)
    validate_kernel_rows(clock)
    assert push(s, clock) == s
    assert all(s[a] * clock_rows[a][b] == s[b] * clock_rows[b][a] for a, b in edges)
    alpha = F(1, 5)
    lifted_rows = {}
    for a in range(3):
        for x in range(3):
            row: dict[int, F] = {}
            for b, p in clock_rows[a].items():
                row[3 * b + x] = alpha * p
            for y, p in kernels[a].rows[x].items():
                target = 3 * a + y
                row[target] = row.get(target, F(0)) + (1 - alpha) * p
            lifted_rows[3 * a + x] = row
    return Kernel(9, 9, lifted_rows), s, pis, clock, alpha


def build_certificate() -> dict:
    kernel, s, pis, clock, alpha = counterexample_data()
    candidate = {3 * a + x: s[a] * pis[a][x] for a in range(3) for x in range(3)}
    stationary = stationary_measure_exact(kernel)
    actual = epr_bounds(kernel, stationary)
    pseudo = epr_bounds(kernel, candidate)
    gap_lower = actual[0] - pseudo[1]
    assert gap_lower > 0
    k = kernel.state_count - 1
    powered_rows = [hold(dirac(x), kernel, k) for x in range(kernel.state_count)]
    delta = max(
        sum((abs(left.get(x, F(0)) - right.get(x, F(0))) for x in range(kernel.state_count)), F(0))
        / 2
        for left in powered_rows
        for right in powered_rows
    )
    assert delta < 1
    evolved = push(candidate, kernel)
    residual = sum((abs(evolved[x] - candidate[x]) for x in candidate), F(0)) / 2
    b_bounds = []
    for a in range(3):
        for x in range(3):
            lo, hi = F(0), F(0)
            for b, probability in clock.rows[a].items():
                log_lo, log_hi = log_bounds(pis[a][x] / pis[b][x])
                lo += alpha * probability * log_lo
                hi += alpha * probability * log_hi
            b_bounds.append((lo, hi))
    osc_upper = max(hi for lo, hi in b_bounds) - min(lo for lo, hi in b_bounds)
    correction_upper = osc_upper * k * residual / (1 - delta)
    repaired_upper = pseudo[1] + correction_upper
    assert actual[1] <= repaired_upper
    return {
        "claim": "the pseudo-EPR candidate is not a general stationary upper bound",
        "setting": "random-scan, reversible clock, per-phase Gibbs-reversible kernels",
        "energies": [0, 1, 2],
        "epsilons": ["4/25", "4/7", "1/60"],
        "alpha": str(alpha),
        "clock_stationary": {str(a): str(p) for a, p in s.items()},
        "clock_rows": _rows(clock),
        "lifted_rows": _rows(kernel),
        "candidate_measure": {str(x): str(p) for x, p in candidate.items()},
        "stationary_measure": {str(x): str(p) for x, p in stationary.items()},
        "stationarity_verified_exact": push(stationary, kernel) == stationary,
        "log_bound_terms": 32,
        "stationary_epr_bounds": [str(x) for x in actual],
        "candidate_epr_bounds": [str(x) for x in pseudo],
        "violation_lower_bound": str(gap_lower),
        "violation_certified_positive": gap_lower > 0,
        "repaired_budget": {
            "power": k,
            "dobrushin_coefficient": str(delta),
            "candidate_stationarity_residual_tv": str(residual),
            "boundary_oscillation_upper": str(osc_upper),
            "correction_upper": str(correction_upper),
            "epr_upper": str(repaired_upper),
            "verified_on_example": actual[1] <= repaired_upper,
            "scope": "upper budget, not a claim of sharpness",
        },
    }


def _rows(kernel: Kernel) -> dict[str, dict[str, str]]:
    return {str(x): {str(y): str(p) for y, p in row.items()} for x, row in kernel.rows.items()}


if __name__ == "__main__":
    certificate = build_certificate()
    OUTPUT_PATH.write_text(json.dumps(certificate, indent=2, sort_keys=True) + "\n")
    print("certified stationary pseudo-bound violation; repaired budget holds")
