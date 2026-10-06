"""Fekete pressure closure for the GT6 base theory.

For a nonnegative tilted transfer matrix ``L_s``, define
``Phi_n(s) = max_x sum_y (L_s^n)(x, y)``. The closure route uses the classical
submultiplicativity argument:

``Phi_{n+m} = max_x sum_z (L^n)(x,z) * sum_y (L^m)(z,y)
             <= max_x sum_z (L^n)(x,z) * Phi_m
             = Phi_n * Phi_m``.

Thus ``log Phi_n`` is subadditive and Fekete's lemma gives the pressure
``P_T0(s) = lim_n n^{-1} log Phi_n(s) = inf_n n^{-1} log Phi_n(s)``.
The comparison-vector bounds certify that limit with exact rational
inequalities and exp/log enclosures. Finite ladders and spectral diagnostics
remain float64 approximations.
"""

from __future__ import annotations

import math
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from fractions import Fraction
from itertools import pairwise

from sixbirds_glass.io.exp_bounds import exp_bounds
from sixbirds_glass.io.log_bounds import log_bounds
from sixbirds_glass.models.kernels import Kernel, validate_kernel_rows

Observable = Callable[[int, int], int]


@dataclass(frozen=True)
class SubadditivityCheck:
    """One numerical check of ``log Phi_{n+m} <= log Phi_n + log Phi_m``."""

    n: int
    m: int
    log_phi_n_plus_m: float
    log_phi_n_plus_log_phi_m: float
    passed: bool
    tolerance: float


@dataclass(frozen=True)
class PressureBounds:
    """Certified bounds on the actual infinite-time normalized log growth."""

    vector: tuple[Fraction, ...]
    growth_lower: Fraction
    growth_upper: Fraction
    pressure_lower: Fraction
    pressure_upper: Fraction


def pressure_bounds(
    kernel: Kernel,
    g: Observable,
    N: int,
    s: Fraction,
    *,
    iterations: int = 64,
    vector: Sequence[Fraction] | None = None,
) -> PressureBounds:
    """Certify the Fekete limit with a positive comparison vector.

    If a*v <= L*v <= b*v, positivity implies a**n*v <= L**n*v <= b**n*v.
    Since v is strictly positive on a finite carrier, comparison with the
    all-ones vector bounds the limiting log growth by log(a), log(b).
    Float iteration only selects v; all inequalities use exact rational
    probabilities and outward exponential/logarithm enclosures.
    """
    validate_kernel_rows(kernel)
    if not isinstance(s, Fraction) or iterations < 0:
        raise ValueError("pressure bounds require a rational tilt and nonnegative iteration count")
    exponents = tuple(s * g(state, N) for state in range(kernel.state_count))
    if vector is None:
        tilt = [math.exp(float(x)) for x in exponents]
        candidate = [1.0] * kernel.state_count
        for _ in range(iterations):
            values = [
                sum(float(p) * tilt[target] * candidate[target] for target, p in row.items())
                for row in (kernel.rows[state] for state in range(kernel.state_count))
            ]
            scale = max(values)
            if not math.isfinite(scale) or scale <= 0:
                raise ValueError("positive comparison-vector iteration failed")
            candidate = [value / scale for value in values]
        vector = tuple(Fraction(value) for value in candidate)
    v = tuple(vector)
    if len(v) != kernel.state_count or any(not isinstance(x, Fraction) or x <= 0 for x in v):
        raise ValueError("comparison vector must be strictly positive Fractions on the carrier")
    exponent_bounds = {exponent: exp_bounds(exponent) for exponent in set(exponents)}
    ratios = []
    for state in range(kernel.state_count):
        lower = (
            sum(
                (
                    p * exponent_bounds[exponents[target]][0] * v[target]
                    for target, p in kernel.rows[state].items()
                ),
                Fraction(0),
            )
            / v[state]
        )
        upper = (
            sum(
                (
                    p * exponent_bounds[exponents[target]][1] * v[target]
                    for target, p in kernel.rows[state].items()
                ),
                Fraction(0),
            )
            / v[state]
        )
        ratios.append((lower, upper))
    growth_lower = min(lo for lo, _ in ratios)
    growth_upper = max(hi for _, hi in ratios)
    if growth_lower <= 0:
        raise ValueError("comparison certificate lacks a positive lower growth bound")
    return PressureBounds(
        v, growth_lower, growth_upper, log_bounds(growth_lower)[0], log_bounds(growth_upper)[1]
    )


def tilted_transfer_matrix(kernel: Kernel, g: Observable, N: int, s: float) -> list[list[float]]:
    """Return dense ``L_s(x,y) = K(x,y) * exp(s * g(y,N))``."""

    validate_kernel_rows(kernel)
    if not math.isfinite(s):
        raise ValueError("tilt must be finite")
    return [
        [
            float(kernel.rows[source].get(target, 0)) * math.exp(s * g(target, N))
            for target in range(kernel.state_count)
        ]
        for source in range(kernel.state_count)
    ]


def phi_n(matrix: list[list[float]], n: int) -> float:
    """Return ``Phi_n`` as ``max_x (L^n 1)(x)``."""

    if n < 1:
        raise ValueError("n must be at least 1")
    vector = [1.0 for _row in matrix]
    for _step in range(n):
        vector = _matvec(matrix, vector)
    return max(vector)


def pressure_ladder(
    kernel: Kernel,
    g: Observable,
    N: int,
    s: float,
    n_values: Sequence[int],
) -> dict[int, float]:
    """Return ``{n: n^{-1} log Phi_n(s)}`` for the declared ladder.

    The recurrence keeps the running vector ``L_s^n 1`` instead of recomputing
    powers from scratch.
    """

    if not n_values:
        raise ValueError("n_values must not be empty")
    sorted_n = tuple(sorted(n_values))
    if sorted_n[0] < 1:
        raise ValueError("n_values must be positive")
    matrix = tilted_transfer_matrix(kernel, g, N, s)
    vector = [1.0 for _row in matrix]
    ladder: dict[int, float] = {}
    for step in range(1, sorted_n[-1] + 1):
        vector = _matvec(matrix, vector)
        if step in sorted_n:
            ladder[step] = math.log(max(vector)) / step
    return ladder


def fekete_gap(ladder: dict[int, float], n_min: int) -> float:
    """Return max successive normalized-log difference beyond ``n_min``."""

    items = [(n, ladder[n]) for n in sorted(ladder) if n > n_min]
    if len(items) < 2:
        return 0.0
    return max(
        abs(right_value - left_value)
        for (_left_n, left_value), (_right_n, right_value) in pairwise(items)
    )


def verify_subadditivity(
    matrix: list[list[float]],
    pairs: Sequence[tuple[int, int]],
    *,
    tolerance: float = 1e-10,
) -> tuple[SubadditivityCheck, ...]:
    """Numerically verify the Fekete subadditivity inequality for selected pairs."""

    cache: dict[int, float] = {}

    def log_phi(n: int) -> float:
        if n not in cache:
            cache[n] = math.log(phi_n(matrix, n))
        return cache[n]

    checks: list[SubadditivityCheck] = []
    for n, m in pairs:
        left = log_phi(n + m)
        right = log_phi(n) + log_phi(m)
        checks.append(
            SubadditivityCheck(
                n=n,
                m=m,
                log_phi_n_plus_m=left,
                log_phi_n_plus_log_phi_m=right,
                passed=left <= right + tolerance,
                tolerance=tolerance,
            )
        )
    return tuple(checks)


def _matvec(matrix: list[list[float]], vector: list[float]) -> list[float]:
    result: list[float] = []
    for row in matrix:
        result.append(sum(value * vector[index] for index, value in enumerate(row)))
    return result
