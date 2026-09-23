"""Fekete pressure closure for the GT6 base theory.

For a nonnegative tilted transfer matrix ``L_s``, define
``Phi_n(s) = max_x sum_y (L_s^n)(x, y)``. The closure route uses the classical
submultiplicativity argument:

``Phi_{n+m} = max_x sum_z (L^n)(x,z) * sum_y (L^m)(z,y)
             <= max_x sum_z (L^n)(x,z) * Phi_m
             = Phi_n * Phi_m``.

Thus ``log Phi_n`` is subadditive and Fekete's lemma gives the pressure
``P_T0(s) = lim_n n^{-1} log Phi_n(s) = inf_n n^{-1} log Phi_n(s)``.
The implementation below is a float64 diagnostic/growth-theory computation,
not part of the exact-rational certificate path.
"""

from __future__ import annotations

import math
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from itertools import pairwise

from sixbirds_glass.models.kernels import Kernel

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


def tilted_transfer_matrix(kernel: Kernel, g: Observable, N: int, s: float) -> list[list[float]]:
    """Return dense ``L_s(x,y) = K(x,y) * exp(s * g(y,N))``."""

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
