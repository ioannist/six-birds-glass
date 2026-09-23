"""Exact packaging endomaps and TV idempotence defects.

This module implements F-I D-IC-01/D-IC-02 over finite KCM state spaces.
The idempotence defect is only a saturation diagnostic: a small value says
that reapplying the packaging map changes little. It does not by itself
certify multiplicity; that reading requires a separate nontriviality witness.
"""

from __future__ import annotations

from collections.abc import Callable, Hashable
from fractions import Fraction

from sixbirds_glass.models.east import east_stationary
from sixbirds_glass.models.kernels import Kernel
from sixbirds_glass.protocols.evolution import Distribution, dirac, hold

Lens = Callable[[int, int], Hashable]
PrototypeRule = Callable[[Hashable, tuple[int, ...]], dict[int, Fraction]]


def fiber_partition(N: int, lens: Lens) -> dict[Hashable, tuple[int, ...]]:
    """Partition ``range(2**N)`` by a deterministic coarse lens."""

    if N < 1:
        raise ValueError("N must be positive")
    fibers: dict[Hashable, list[int]] = {}
    for state in range(1 << N):
        label = lens(state, N)
        fibers.setdefault(label, []).append(state)
    return {label: tuple(states) for label, states in fibers.items()}


def gibbs_prototype_rule(N: int, epsilon_ref: Fraction) -> PrototypeRule:
    """Return Gibbs-within-fiber prototypes at the declared reference epsilon.

    For East with the energy lens ``l_energy``, this rule provably degenerates
    to the uniform rule: ``pi_epsilon(n)`` depends only on ``E(n)``, so every
    state inside one energy fiber has exactly the same reference weight. This
    is a real model/lens fact, not a numerical accident or a limitation to fix.
    """

    stationary = east_stationary(N, epsilon_ref)

    def rule(_label: Hashable, states: tuple[int, ...]) -> dict[int, Fraction]:
        if not states:
            raise ValueError("prototype fiber must not be empty")
        fiber_mass = sum((stationary[state] for state in states), start=Fraction(0))
        if fiber_mass <= 0:
            raise ValueError("Gibbs prototype fiber mass must be positive")
        return {state: stationary[state] / fiber_mass for state in states}

    return rule


def uniform_prototype_rule() -> PrototypeRule:
    """Return uniform prototypes on each declared fiber."""

    def rule(_label: Hashable, states: tuple[int, ...]) -> dict[int, Fraction]:
        if not states:
            raise ValueError("prototype fiber must not be empty")
        mass = Fraction(1, len(states))
        return {state: mass for state in states}

    return rule


def coarse_grain(
    distribution: Distribution, fibers: dict[Hashable, tuple[int, ...]]
) -> dict[Hashable, Fraction]:
    """Apply ``Q_f`` by summing a distribution over each lens fiber."""

    return {
        label: sum((distribution.get(state, Fraction(0)) for state in states), start=Fraction(0))
        for label, states in fibers.items()
    }


def relift(
    macro: dict[Hashable, Fraction],
    fibers: dict[Hashable, tuple[int, ...]],
    prototype_rule: PrototypeRule,
) -> Distribution:
    """Apply ``U_f`` by replacing each macro label with its prototype."""

    result: Distribution = {}
    for label, states in fibers.items():
        macro_mass = macro.get(label, Fraction(0))
        if macro_mass == 0:
            continue
        prototype = prototype_rule(label, states)
        _validate_prototype(label, states, prototype)
        for state, prototype_mass in prototype.items():
            value = macro_mass * prototype_mass
            if value != 0:
                result[state] = result.get(state, Fraction(0)) + value
    return result


def packaging_endomap(
    N: int,
    kernel: Kernel,
    tau: int,
    lens: Lens,
    prototype_rule: PrototypeRule,
) -> Kernel:
    """Build the row-stochastic kernel for ``E_{tau,f} = U_f Q_f P^tau``."""

    if tau < 1:
        raise ValueError("tau must be at least 1")
    state_count = 1 << N
    if kernel.state_count != state_count:
        raise ValueError(
            f"kernel state_count {kernel.state_count} does not match 2**N={state_count}"
        )

    fibers = fiber_partition(N, lens)
    rows: dict[int, dict[int, Fraction]] = {}
    for state in range(state_count):
        evolved = hold(dirac(state), kernel, tau)
        macro = coarse_grain(evolved, fibers)
        row = relift(macro, fibers, prototype_rule)
        row_total = sum(row.values(), start=Fraction(0))
        if row_total != Fraction(1):
            raise ValueError(f"packaging row {state} must sum to 1; got {row_total}")
        rows[state] = row
    return Kernel(N=N, state_count=state_count, rows=rows)


def idempotence_defect(endomap: Kernel) -> Fraction:
    """Return the exact TV defect ``1/2 * max_i ||(E^2 - E)[i,*]||_1``.

    Per F-I D-IC-02, this value is a saturation diagnostic only. It must not be
    read as multiplicity or as a glass-state count without a separate
    nontriviality witness.
    """

    matrix = endomap.to_dense()
    square = _dense_matrix_multiply(matrix, matrix)
    max_l1 = Fraction(0)
    for state, row in enumerate(square):
        row_l1 = sum(
            (abs(square_value - matrix[state][target]) for target, square_value in enumerate(row)),
            start=Fraction(0),
        )
        max_l1 = max(max_l1, row_l1)
    return Fraction(1, 2) * max_l1


def _validate_prototype(
    label: Hashable, states: tuple[int, ...], prototype: dict[int, Fraction]
) -> None:
    fiber = set(states)
    total = sum(prototype.values(), start=Fraction(0))
    if total != Fraction(1):
        raise ValueError(f"prototype for fiber {label!r} must sum to 1; got {total}")
    for state, mass in prototype.items():
        if state not in fiber:
            raise ValueError(f"prototype for fiber {label!r} has outside state {state}")
        if mass < 0:
            raise ValueError(
                f"prototype for fiber {label!r} has negative mass at state {state}: {mass}"
            )


def _dense_matrix_multiply(
    left: list[list[Fraction]], right: list[list[Fraction]]
) -> list[list[Fraction]]:
    size = len(left)
    result = [[Fraction(0) for _ in range(size)] for _ in range(size)]
    for row_index, left_row in enumerate(left):
        result_row = result[row_index]
        for middle, left_value in enumerate(left_row):
            if left_value == 0:
                continue
            right_row = right[middle]
            for column, right_value in enumerate(right_row):
                if right_value != 0:
                    result_row[column] += left_value * right_value
    return result
