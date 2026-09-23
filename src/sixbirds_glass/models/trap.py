"""Bouchaud-type uniform-reset trap model with declared rational weights.

Temperature dependence is represented by declared per-grid escape-weight
vectors, not by exponentiating base weights. The interpolation rule below is an
exact rational declaration: the coldest grid index uses half the base escape
weights, the hottest grid index uses the base weights, and intermediate grid
indices linearly interpolate between those two vectors.

Ann_Bridge note: this finite rational catalog is intended as a certificate-path
stand-in for the physical relation ``w_k(T) ~= w_k ** (beta / beta_ref)``. That
relation is informative only and is never evaluated here.

This module's declared per-epsilon interpolation deliberately departs from the
trap-model literature's standard convention: real trap models parametrize
temperature via a per-trap Arrhenius factor ``w_k(T) ∝ exp(±E_k/T)``
(Bouchaud 1992; Monthus & Bouchaud 1996, *J. Phys. A* 29, 3847,
arXiv:cond-mat/9601012), under which DIFFERENT traps rescale by DIFFERENT
temperature-dependent factors and the equilibrium genuinely shifts with
temperature -- this is exactly the mechanism Diezemann & Heuer (2011,
*Phys. Rev. E* 83, 031505, arXiv:1102.0411) and Bertin, Bouchaud, Drouffe &
Godreche (2003, *J. Phys. A* 36, 10701, arXiv:cond-mat/0306089) use to produce
genuine Kovacs memory effects in trap models. This module instead uses a
single scalar multiplier shared by
every trap at a given epsilon (to keep every computation exactly rational,
avoiding non-integer exponentiation) -- the epsilon-invariance documented below
and tested in ``tests/test_models_trap.py`` is the direct, elementary
consequence of that deliberate choice, not a claim about trap models in
general.

Note: because ``declared_trap_weights_by_epsilon`` scales every trap's base
weight by the same scalar multiplier per grid epsilon, ``trap_stationary`` is
epsilon-invariant: the multiplier cancels in the normalized ratio ``pi_k
proportional to 1 / w_k``. This model's declared temperature dependence
therefore governs relaxation rate only, not the relaxation target; readouts
that depend on a temperature-dependent equilibrium, such as the GT7 Kovacs-hump
signature, cannot be nonzero for this family under the current interpolation
rule. See ``tests/test_models_trap.py``'s
``test_trap_stationary_distribution_is_epsilon_invariant``.
"""

from __future__ import annotations

from collections.abc import Sequence
from fractions import Fraction
from typing import Literal

from sixbirds_glass.models.kernels import Kernel, SparseRows, validate_kernel_rows

DEFAULT_TRAP_BASE_WEIGHTS: tuple[Fraction, ...] = (
    Fraction(1, 2),
    Fraction(2, 5),
    Fraction(3, 10),
    Fraction(1, 5),
    Fraction(3, 20),
    Fraction(1, 10),
    Fraction(1, 20),
    Fraction(1, 50),
)


def declared_trap_weights_by_epsilon(
    epsilon_grid: Sequence[Fraction],
    base_weights: tuple[Fraction, ...] = DEFAULT_TRAP_BASE_WEIGHTS,
) -> dict[Fraction, tuple[Fraction, ...]]:
    """Return declared trap escape vectors for each grid epsilon.

    The rule is index-based over the caller's declared grid order. For a grid
    of length ``G > 1``, grid index ``i`` uses multiplier
    ``1/2 + i / (2 * (G - 1))``. Thus the first grid point is coldest/stickiest
    and the last is hottest/easiest to escape. A singleton grid uses multiplier
    ``1``.
    """

    _validate_weights(base_weights, label="base_weights")
    grid = tuple(epsilon_grid)
    if not grid:
        raise ValueError("epsilon_grid must be non-empty")
    if len(set(grid)) != len(grid):
        raise ValueError("epsilon_grid entries must be unique")

    denominator = len(grid) - 1
    weights_by_epsilon: dict[Fraction, tuple[Fraction, ...]] = {}
    for index, epsilon in enumerate(grid):
        if not isinstance(epsilon, Fraction):
            raise ValueError(f"epsilon_grid entry is not a Fraction: {epsilon!r}")
        multiplier = (
            Fraction(1) if denominator == 0 else Fraction(1, 2) + Fraction(index, 2 * denominator)
        )
        weights_by_epsilon[epsilon] = tuple(multiplier * weight for weight in base_weights)
    return weights_by_epsilon


def build_trap_kernel(
    base_weights: tuple[Fraction, ...],
    escape_weights: tuple[Fraction, ...],
) -> Kernel:
    """Build the uniform-reset trap kernel.

    From trap ``k``, escape with probability ``w_k`` and choose the target trap
    uniformly from all ``M`` traps. With probability ``1 - w_k``, hold at ``k``.
    """

    _validate_weights(base_weights, label="base_weights")
    _validate_weights(escape_weights, label="escape_weights")
    if len(base_weights) != len(escape_weights):
        raise ValueError("base_weights and escape_weights must have the same length")

    trap_count = len(base_weights)
    rows: SparseRows = {}
    for source, escape_weight in enumerate(escape_weights):
        jump_probability = escape_weight / trap_count
        row = {target: jump_probability for target in range(trap_count)}
        row[source] += Fraction(1) - escape_weight
        rows[source] = row

    kernel = Kernel(N=trap_count, state_count=trap_count, rows=rows)
    validate_kernel_rows(kernel, label="trap kernel")
    return kernel


def trap_stationary(escape_weights: tuple[Fraction, ...]) -> dict[int, Fraction]:
    """Return the reversible stationary law ``pi_k proportional to 1 / w_k``."""

    _validate_weights(escape_weights, label="escape_weights")
    inverse_weights = tuple(Fraction(1) / weight for weight in escape_weights)
    normalizer = sum(inverse_weights, start=Fraction(0))
    return {
        trap: inverse_weight / normalizer for trap, inverse_weight in enumerate(inverse_weights)
    }


def trap_band(
    trap: int,
    base_weights: tuple[Fraction, ...] = DEFAULT_TRAP_BASE_WEIGHTS,
) -> Literal["shallow", "deep"]:
    """Return the median-split trap band for a trap index."""

    _validate_weights(base_weights, label="base_weights")
    if not 0 <= trap < len(base_weights):
        raise ValueError(f"trap index out of range: {trap}")

    sorted_weights = sorted(base_weights)
    midpoint = len(sorted_weights) // 2
    if len(sorted_weights) % 2 == 0:
        median = (sorted_weights[midpoint - 1] + sorted_weights[midpoint]) / 2
    else:
        median = sorted_weights[midpoint]
    return "shallow" if base_weights[trap] > median else "deep"


def trap_depth_observable(
    trap: int,
    base_weights: tuple[Fraction, ...] = DEFAULT_TRAP_BASE_WEIGHTS,
) -> Fraction:
    """Return the declared trap readout depth ``1 / base_weight``.

    This is the trap analogue of spin-count energy for East/FA: a fixed
    structural observable independent of epsilon. Smaller base escape weights
    produce larger declared depths.
    """

    _validate_weights(base_weights, label="base_weights")
    if not 0 <= trap < len(base_weights):
        raise ValueError(f"trap index out of range: {trap}")
    return Fraction(1) / base_weights[trap]


def _validate_weights(weights: tuple[Fraction, ...], *, label: str) -> None:
    if not weights:
        raise ValueError(f"{label} must be non-empty")
    for index, weight in enumerate(weights):
        if not isinstance(weight, Fraction):
            raise ValueError(f"{label}[{index}] is not a Fraction: {weight!r}")
        if not (Fraction(0) < weight <= Fraction(1)):
            raise ValueError(f"{label}[{index}] must lie in (0, 1]: {weight}")
