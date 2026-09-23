"""Float64 spectral diagnostics for exact finite kernels.

These helpers intentionally leave the certificate path: kernels are converted
from exact ``Fraction`` entries to ``float`` for diagnostic eigensolves used to
choose relaxation windows. Do not use this module for theorem certificates.
"""

from __future__ import annotations

import math
from fractions import Fraction

import numpy as np

from sixbirds_glass.io.rational import rational_to_str
from sixbirds_glass.models.east import build_east_kernel, east_stationary
from sixbirds_glass.models.kernels import Kernel


def spectral_gap(kernel: Kernel) -> float:
    """Return the diagnostic float64 spectral gap ``1 - |lambda_2|``.

    The leading stationary eigenvalue is identified as the eigenvalue whose
    modulus is closest to ``1.0`` and excluded by index before taking the next
    largest modulus. No ordering from ``numpy.linalg.eigvals`` is assumed.
    """

    if kernel.state_count <= 1:
        return 1.0

    matrix = np.array(
        [[float(entry) for entry in row] for row in kernel.to_dense()],
        dtype=float,
    )
    eigenvalues = np.linalg.eigvals(matrix)
    moduli = np.abs(eigenvalues)
    leading_index = int(np.argmin(np.abs(moduli - 1.0)))
    remaining = np.delete(moduli, leading_index)
    second_largest_modulus = float(np.max(remaining))
    return 1.0 - second_largest_modulus


def mixing_time_bound(gap: float, *, total_variation_target: float = 1e-3) -> float:
    """Return a standard spectral relaxation-time mixing proxy.

    Uses ``log(1 / (gap * target)) / gap``, a common spectral-gap bound form
    following the Levin-Peres-Wilmer relaxation-time estimates.
    """

    if gap <= 0:
        return float("inf")
    if total_variation_target <= 0:
        raise ValueError("total_variation_target must be positive")
    return math.log(1.0 / (gap * total_variation_target)) / gap


def spectral_gap_table_row(N: int, epsilon: Fraction) -> dict[str, int | str | float]:
    """Return one East spectral-gap diagnostic table row."""

    gap = _east_reversible_spectral_gap(N, epsilon)
    tau_rel = float("inf") if gap <= 0 else 1.0 / gap
    return {
        "N": N,
        "epsilon": rational_to_str(epsilon),
        "gap": gap,
        "tau_rel": tau_rel,
        "mixing_time_bound": mixing_time_bound(gap),
    }


def _east_reversible_spectral_gap(N: int, epsilon: Fraction) -> float:
    kernel = build_east_kernel(N, epsilon)
    matrix = np.array(
        [[float(entry) for entry in row] for row in kernel.to_dense()],
        dtype=float,
    )
    stationary = east_stationary(N, epsilon)
    pi = np.array([float(stationary[state]) for state in range(kernel.state_count)])
    sqrt_pi = np.sqrt(pi)

    symmetric = (sqrt_pi[:, np.newaxis] * matrix) / sqrt_pi[np.newaxis, :]
    symmetric = (symmetric + symmetric.T) / 2.0
    eigenvalues = np.linalg.eigvalsh(symmetric)
    moduli = np.abs(eigenvalues)
    leading_index = int(np.argmin(np.abs(moduli - 1.0)))
    remaining = np.delete(moduli, leading_index)
    return 1.0 - float(np.max(remaining))
