"""Conditional disintegration gap for the GT6 filing."""

from __future__ import annotations

import math
from collections.abc import Callable, Hashable, Sequence
from fractions import Fraction

from sixbirds_glass.extension.pressure import tilted_transfer_matrix
from sixbirds_glass.models.kernels import Kernel

Observable = Callable[[int, int], int]


def stratum_conditioned_pressure(
    kernel: Kernel,
    g: Observable,
    N: int,
    s: float,
    stratum_states: frozenset[int],
    n_values: Sequence[int],
) -> float:
    """Return the pressure estimate with transfer restricted to one stratum.

    Rows and columns outside ``stratum_states`` are zeroed before iterating the
    tilted transfer operator. This is a fiber-conditioned pressure average, not
    a claim that the stratum is an autonomous thermodynamic subsystem.
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
