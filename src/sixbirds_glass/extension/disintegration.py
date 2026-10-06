"""Finite initial-law conditioning and separate killed-process diagnostics."""

from __future__ import annotations

import math
from collections.abc import Callable, Hashable, Sequence
from fractions import Fraction

from sixbirds_glass.extension.pressure import tilted_transfer_matrix
from sixbirds_glass.io.exp_bounds import exp_bounds
from sixbirds_glass.io.log_bounds import log_bounds
from sixbirds_glass.models.kernels import Kernel, validate_kernel_rows
from sixbirds_glass.pipeline.packaging import Lens, fiber_partition
from sixbirds_glass.protocols.evolution import Distribution

Observable = Callable[[int, int], int]


def stratum_conditioned_pressure(
    kernel: Kernel,
    g: Observable,
    N: int,
    s: float,
    stratum_states: frozenset[int],
    n_values: Sequence[int],
) -> float:
    """Legacy name for a killed-process survival-pressure estimate.

    Rows and columns outside ``stratum_states`` are zeroed before iterating the
    tilted transfer operator. This kills trajectories on stratum exit; it is
    not conditioning only the initial preparation and retaining the original
    dynamics. It does not establish the conditional-disintegration bridge.
    """

    matrix = tilted_transfer_matrix(kernel, g, N, s)
    restricted = [
        [
            value if source in stratum_states and target in stratum_states else 0.0
            for target, value in enumerate(row)
        ]
        for source, row in enumerate(matrix)
    ]
    ladder = _pressure_ladder_from_matrix(restricted, n_values)
    return ladder[max(ladder)]


def conditional_pressure_bounds(
    kernel: Kernel,
    distribution: Distribution,
    lens: Lens,
    g: Observable,
    N: int,
    s: Fraction,
    n: int,
) -> tuple[
    tuple[Fraction, Fraction], dict[Hashable, tuple[Fraction, Fraction]], tuple[Fraction, Fraction]
]:
    """Enclose the finite-time conditional pressure contrast on original paths.

    For Z_n(x) = (L_s**n 1)(x), use P_n=log(mu Z_n)/n and
    P_{n,f}=log(mu(.|f) Z_n)/n. The same original transfer matrix is used
    after every conditional preparation; no trajectory is killed on exit.
    Jensen gives P_n-sum_f mu(f)P_{n,f} >= 0. Zero-mass fibers are omitted.
    These are finite-time profiles, not multiple infinite-time pressures.
    """
    validate_kernel_rows(kernel)
    if n < 1 or kernel.state_count != 1 << N or not isinstance(s, Fraction):
        raise ValueError("invalid horizon, spin carrier, or rational tilt")
    if sum(distribution.values(), Fraction(0)) != 1 or any(
        not isinstance(mass, Fraction) or mass < 0 or not 0 <= state < kernel.state_count
        for state, mass in distribution.items()
    ):
        raise ValueError("initial ensemble must be a probability law on the carrier")
    factors = {s * g(state, N): exp_bounds(s * g(state, N)) for state in range(kernel.state_count)}
    lower = upper = [Fraction(1)] * kernel.state_count
    for _ in range(n):
        lower = [
            sum(
                (
                    p * factors[s * g(target, N)][0] * lower[target]
                    for target, p in kernel.rows[state].items()
                ),
                Fraction(0),
            )
            for state in range(kernel.state_count)
        ]
        upper = [
            sum(
                (
                    p * factors[s * g(target, N)][1] * upper[target]
                    for target, p in kernel.rows[state].items()
                ),
                Fraction(0),
            )
            for state in range(kernel.state_count)
        ]

    def profile(states: tuple[int, ...], mass: Fraction) -> tuple[Fraction, Fraction]:
        lo = sum((distribution.get(x, Fraction(0)) * lower[x] for x in states), Fraction(0)) / mass
        hi = sum((distribution.get(x, Fraction(0)) * upper[x] for x in states), Fraction(0)) / mass
        return log_bounds(lo)[0] / n, log_bounds(hi)[1] / n

    base = profile(tuple(range(kernel.state_count)), Fraction(1))
    fibers = fiber_partition(N, lens)
    weights = {
        label: sum((distribution.get(x, Fraction(0)) for x in states), Fraction(0))
        for label, states in fibers.items()
    }
    strata = {
        label: profile(states, weights[label])
        for label, states in fibers.items()
        if weights[label] > 0
    }
    gap_lower = base[0] - sum((weights[f] * bounds[1] for f, bounds in strata.items()), Fraction(0))
    gap_upper = base[1] - sum((weights[f] * bounds[0] for f, bounds in strata.items()), Fraction(0))
    return base, strata, (max(Fraction(0), gap_lower), gap_upper)


def disintegration_gap(
    P_T0: float,
    stratum_pressures: dict[Hashable, float],
    stratum_weights: dict[Hashable, Fraction],
) -> float:
    """Return ``P_T0 - sum_Sigma w_Sigma P_Sigma``."""

    weighted = sum(
        float(stratum_weights[label]) * pressure for label, pressure in stratum_pressures.items()
    )
    return P_T0 - weighted


def _pressure_ladder_from_matrix(
    matrix: list[list[float]], n_values: Sequence[int]
) -> dict[int, float]:
    if not n_values:
        raise ValueError("n_values must not be empty")
    sorted_n = tuple(sorted(n_values))
    vector = [1.0 for _row in matrix]
    ladder: dict[int, float] = {}
    for step in range(1, sorted_n[-1] + 1):
        vector = [sum(value * vector[index] for index, value in enumerate(row)) for row in matrix]
        if step in sorted_n:
            phi = max(vector)
            ladder[step] = float("-inf") if phi <= 0.0 else math.log(phi) / step
    return ladder
