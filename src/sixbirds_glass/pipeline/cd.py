"""Stationary closure deficit and exact lumpability checks."""

from __future__ import annotations

import math
from collections.abc import Callable, Hashable
from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations

from sixbirds_glass.models.kernels import Kernel
from sixbirds_glass.pipeline.packaging import fiber_partition
from sixbirds_glass.protocols.evolution import Distribution, dirac, hold

Lens = Callable[[int, int], Hashable]


@dataclass(frozen=True)
class LumpabilityViolation:
    """First exact fiber-transition disagreement found in a tau-lumpability check."""

    source_fiber: Hashable
    target_fiber: Hashable
    left_state: int
    right_state: int
    left_probability: Fraction
    right_probability: Fraction


@dataclass(frozen=True)
class LumpabilityResult:
    """Exact tau-lumpability result with optional first violation detail."""

    is_lumpable: bool
    violation: LumpabilityViolation | None = None


def is_exactly_lumpable(N: int, kernel: Kernel, tau: int, lens: Lens) -> bool:
    """Return whether all same-fiber states have identical tau-step macro rows."""

    return lumpability_check_exact(N, kernel, tau, lens).is_lumpable


def lumpability_check_exact(N: int, kernel: Kernel, tau: int, lens: Lens) -> LumpabilityResult:
    """Check the exact Kemeny-Snell tau-lumpability identity over Fractions."""

    if tau < 1:
        raise ValueError("tau must be at least 1")
    state_count = 1 << N
    if kernel.state_count != state_count:
        raise ValueError(
            f"kernel state_count {kernel.state_count} does not match 2**N={state_count}"
        )

    fibers = fiber_partition(N, lens)
    macro_rows = _macro_transition_rows(kernel, tau, fibers)
    for source_label, states in fibers.items():
        for left_state, right_state in combinations(states, 2):
            left_row = macro_rows[left_state]
            right_row = macro_rows[right_state]
            for target_label in fibers:
                left_probability = left_row[target_label]
                right_probability = right_row[target_label]
                if left_probability != right_probability:
                    return LumpabilityResult(
                        is_lumpable=False,
                        violation=LumpabilityViolation(
                            source_fiber=source_label,
                            target_fiber=target_label,
                            left_state=left_state,
                            right_state=right_state,
                            left_probability=left_probability,
                            right_probability=right_probability,
                        ),
                    )
    return LumpabilityResult(is_lumpable=True)


def closure_deficit_float(
    N: int,
    kernel: Kernel,
    stationary: dict[int, Fraction],
    tau: int,
    lens: Lens,
) -> float:
    """Compute stationary ``CD_tau(Pi) = I(X_t; Y_{t+tau} | Y_t)`` in float64."""

    if tau < 1:
        raise ValueError("tau must be at least 1")
    fibers = fiber_partition(N, lens)
    labels = tuple(fibers)
    macro_rows_exact = _macro_transition_rows(kernel, tau, fibers)
    macro_rows = {
        state: [float(macro_rows_exact[state][label]) for label in labels]
        for state in range(kernel.state_count)
    }
    pi_macro = {
        label: sum((stationary.get(state, Fraction(0)) for state in states), start=Fraction(0))
        for label, states in fibers.items()
    }
    averaged_rows = _stationary_fiber_average_rows(fibers, stationary, pi_macro, macro_rows, labels)

    cd = 0.0
    for state in range(kernel.state_count):
        weight = float(stationary.get(state, Fraction(0)))
        if weight == 0.0:
            continue
        source_label = lens(state, N)
        cd += weight * _kl_divergence(macro_rows[state], averaged_rows[source_label])
    return float(cd)


def _macro_transition_rows(
    kernel: Kernel, tau: int, fibers: dict[Hashable, tuple[int, ...]]
) -> dict[int, dict[Hashable, Fraction]]:
    rows: dict[int, dict[Hashable, Fraction]] = {}
    for state in range(kernel.state_count):
        evolved = hold(dirac(state), kernel, tau)
        rows[state] = {
            label: _fiber_probability(evolved, states) for label, states in fibers.items()
        }
    return rows


def _fiber_probability(distribution: Distribution, states: tuple[int, ...]) -> Fraction:
    return sum((distribution.get(state, Fraction(0)) for state in states), start=Fraction(0))


def _stationary_fiber_average_rows(
    fibers: dict[Hashable, tuple[int, ...]],
    stationary: dict[int, Fraction],
    pi_macro: dict[Hashable, Fraction],
    macro_rows: dict[int, list[float]],
    labels: tuple[Hashable, ...],
) -> dict[Hashable, list[float]]:
    averaged: dict[Hashable, list[float]] = {}
    for label, states in fibers.items():
        row = [0.0 for _ in labels]
        mass = pi_macro[label]
        if mass == 0:
            averaged[label] = row
            continue
        for state in states:
            conditional_weight = float(stationary.get(state, Fraction(0)) / mass)
            state_row = macro_rows[state]
            for index, probability in enumerate(state_row):
                row[index] += conditional_weight * probability
        averaged[label] = row
    return averaged


def _kl_divergence(left: list[float], right: list[float]) -> float:
    value = 0.0
    for left_probability, right_probability in zip(left, right, strict=True):
        if left_probability <= 0.0:
            continue
        if right_probability <= 0.0:
            return math.inf
        value += left_probability * (math.log(left_probability) - math.log(right_probability))
    return value
