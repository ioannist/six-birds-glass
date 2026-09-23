"""Protocol-relative closure deficit for finite declared catalogs."""

from __future__ import annotations

import math
from collections.abc import Callable, Hashable, Sequence
from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations

from sixbirds_glass.models.kernels import Kernel, validate_kernel_rows
from sixbirds_glass.pipeline.cd import LumpabilityResult, LumpabilityViolation
from sixbirds_glass.pipeline.packaging import fiber_partition
from sixbirds_glass.protocols.evolution import Distribution, dirac, push

Lens = Callable[[int, int], Hashable]


@dataclass(frozen=True)
class ProtocolCell:
    """One declared protocol/time cell for GB2."""

    label: str
    weight: Fraction
    initial_distribution: Distribution
    kernels: Sequence[Kernel]


def protocol_relative_cd(
    catalog: Sequence[ProtocolCell],
    lens: Lens,
    N: int,
    tau: int,
    *,
    condition_on_r: bool,
) -> float:
    """Compute protocol-relative CD in float64 from the declared ensemble law."""

    _validate_catalog(catalog, N, tau)
    fibers = fiber_partition(N, lens)
    labels = tuple(fibers)
    if condition_on_r:
        return _windowed_protocol_cd(catalog, fibers, labels, lens, N)
    return _marginalized_protocol_cd(catalog, fibers, labels, lens, N)


def protocol_relative_lumpability_check(
    catalog: Sequence[ProtocolCell], lens: Lens, N: int, tau: int
) -> LumpabilityResult:
    """Check the exact GB2 cell-by-cell fiber-transition identity."""

    _validate_catalog(catalog, N, tau)
    fibers = fiber_partition(N, lens)
    for cell in catalog:
        macro_rows = _macro_transition_rows_for_sequence(cell.kernels, fibers)
        for source_label, states in fibers.items():
            realized = tuple(
                state for state in states if cell.initial_distribution.get(state, Fraction(0)) > 0
            )
            if not realized:
                continue
            for left_state, right_state in combinations(realized, 2):
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


def _windowed_protocol_cd(
    catalog: Sequence[ProtocolCell],
    fibers: dict[Hashable, tuple[int, ...]],
    labels: tuple[Hashable, ...],
    lens: Lens,
    N: int,
) -> float:
    cd = 0.0
    for cell in catalog:
        macro_rows_exact = _macro_transition_rows_for_sequence(cell.kernels, fibers)
        macro_rows = _float_macro_rows(macro_rows_exact, labels)
        fiber_masses = _fiber_masses(cell.initial_distribution, fibers)
        averaged_rows = _fiber_average_rows(
            fibers, cell.initial_distribution, fiber_masses, macro_rows, labels
        )
        for state, mass in cell.initial_distribution.items():
            if mass == 0:
                continue
            source_label = lens(state, N)
            cd += float(cell.weight * mass) * _kl_divergence(
                macro_rows[state], averaged_rows[source_label]
            )
    return float(cd)


def _marginalized_protocol_cd(
    catalog: Sequence[ProtocolCell],
    fibers: dict[Hashable, tuple[int, ...]],
    labels: tuple[Hashable, ...],
    lens: Lens,
    N: int,
) -> float:
    state_count = catalog[0].kernels[0].state_count
    state_mass = {state: Fraction(0) for state in range(state_count)}
    joint_state_future = {
        state: {label: Fraction(0) for label in labels} for state in range(state_count)
    }
    for cell in catalog:
        macro_rows = _macro_transition_rows_for_sequence(cell.kernels, fibers)
        for state, mass in cell.initial_distribution.items():
            weighted_mass = cell.weight * mass
            if weighted_mass == 0:
                continue
            state_mass[state] += weighted_mass
            for label in labels:
                joint_state_future[state][label] += weighted_mass * macro_rows[state][label]

    state_rows: dict[int, list[float]] = {}
    for state, mass in state_mass.items():
        if mass == 0:
            continue
        state_rows[state] = [float(joint_state_future[state][label] / mass) for label in labels]

    fiber_masses = {
        source_label: sum((state_mass[state] for state in states), start=Fraction(0))
        for source_label, states in fibers.items()
    }
    averaged_rows: dict[Hashable, list[float]] = {}
    for source_label, states in fibers.items():
        row = [0.0 for _ in labels]
        mass = fiber_masses[source_label]
        if mass == 0:
            averaged_rows[source_label] = row
            continue
        for state in states:
            if state_mass[state] == 0:
                continue
            conditional_weight = float(state_mass[state] / mass)
            for index, probability in enumerate(state_rows[state]):
                row[index] += conditional_weight * probability
        averaged_rows[source_label] = row

    cd = 0.0
    for state, mass in state_mass.items():
        if mass == 0:
            continue
        cd += float(mass) * _kl_divergence(state_rows[state], averaged_rows[lens(state, N)])
    return float(cd)


def _validate_catalog(catalog: Sequence[ProtocolCell], N: int, tau: int) -> None:
    if tau < 1:
        raise ValueError("tau must be at least 1")
    if not catalog:
        raise ValueError("catalog must contain at least one protocol cell")
    total_weight = sum((cell.weight for cell in catalog), start=Fraction(0))
    if total_weight != Fraction(1):
        raise ValueError(f"protocol weights must sum to 1; got {total_weight}")
    state_count = 1 << N
    for cell in catalog:
        if cell.weight <= 0:
            raise ValueError(f"protocol cell {cell.label!r} has non-positive weight")
        if len(cell.kernels) != tau:
            raise ValueError(f"protocol cell {cell.label!r} must declare exactly tau kernels")
        distribution_total = sum(cell.initial_distribution.values(), start=Fraction(0))
        if distribution_total != Fraction(1):
            raise ValueError(f"protocol cell {cell.label!r} initial distribution must sum to 1")
        for mass in cell.initial_distribution.values():
            if not isinstance(mass, Fraction):
                raise ValueError(f"protocol cell {cell.label!r} has non-Fraction mass")
            if mass < 0:
                raise ValueError(f"protocol cell {cell.label!r} has negative mass")
        for kernel in cell.kernels:
            if kernel.state_count != state_count:
                raise ValueError(
                    f"protocol cell {cell.label!r} kernel state_count does not match 2**N"
                )
            validate_kernel_rows(kernel, label=f"protocol cell {cell.label!r} kernel")


def _macro_transition_rows_for_sequence(
    kernels: Sequence[Kernel], fibers: dict[Hashable, tuple[int, ...]]
) -> dict[int, dict[Hashable, Fraction]]:
    rows: dict[int, dict[Hashable, Fraction]] = {}
    state_count = kernels[0].state_count
    for state in range(state_count):
        evolved = _apply_kernel_sequence(dirac(state), kernels)
        rows[state] = {
            label: _fiber_probability(evolved, states) for label, states in fibers.items()
        }
    return rows


def _apply_kernel_sequence(distribution: Distribution, kernels: Sequence[Kernel]) -> Distribution:
    result = distribution
    for kernel in kernels:
        result = push(result, kernel)
    return result


def _fiber_probability(distribution: Distribution, states: tuple[int, ...]) -> Fraction:
    return sum((distribution.get(state, Fraction(0)) for state in states), start=Fraction(0))


def _float_macro_rows(
    macro_rows_exact: dict[int, dict[Hashable, Fraction]], labels: tuple[Hashable, ...]
) -> dict[int, list[float]]:
    return {
        state: [float(row[label]) for label in labels] for state, row in macro_rows_exact.items()
    }


def _fiber_masses(
    distribution: Distribution, fibers: dict[Hashable, tuple[int, ...]]
) -> dict[Hashable, Fraction]:
    return {
        label: sum((distribution.get(state, Fraction(0)) for state in states), start=Fraction(0))
        for label, states in fibers.items()
    }


def _fiber_average_rows(
    fibers: dict[Hashable, tuple[int, ...]],
    distribution: Distribution,
    fiber_masses: dict[Hashable, Fraction],
    macro_rows: dict[int, list[float]],
    labels: tuple[Hashable, ...],
) -> dict[Hashable, list[float]]:
    averaged: dict[Hashable, list[float]] = {}
    for label, states in fibers.items():
        row = [0.0 for _ in labels]
        mass = fiber_masses[label]
        if mass == 0:
            averaged[label] = row
            continue
        for state in states:
            state_mass = distribution.get(state, Fraction(0))
            if state_mass == 0:
                continue
            conditional_weight = float(state_mass / mass)
            for index, probability in enumerate(macro_rows[state]):
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
