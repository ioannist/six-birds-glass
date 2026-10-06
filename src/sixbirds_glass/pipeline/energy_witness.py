"""Lawful stopping-time mixtures agreeing on the full current energy law.

The coefficients are computed from current energy laws alone. Future readouts
are evaluated only after this construction; they are not inputs to the selector.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from functools import cache
from typing import Any

from sixbirds_glass.models.east import build_east_kernel, east_energy, east_stationary
from sixbirds_glass.models.kernels import Kernel, validate_kernel_rows
from sixbirds_glass.pipeline.reflection_witness import energy_level_distribution
from sixbirds_glass.protocols.evolution import (
    Distribution,
    expectation,
    hold,
    max_denominator_bits,
    push,
)

PROBE_STEPS = 5


@dataclass(frozen=True)
class StoppingMixtures:
    """Two convex mixtures and their current-blind nullspace certificate."""

    rank: int
    free_column: int
    coefficients: tuple[Fraction, ...]
    plus_weights: tuple[Fraction, ...]
    minus_weights: tuple[Fraction, ...]
    plus: Distribution
    minus: Distribution
    energy_law: dict[int, Fraction]


@dataclass(frozen=True)
class EnergyMixtureWitness:
    """Actual East preparations and exact separating energy continuations."""

    N: int
    epsilon_hi: Fraction
    epsilon_lo: Fraction
    epsilon_mid: Fraction
    t_w: int
    tau_probe: int
    stop_times: tuple[int, ...]
    source_laws: tuple[Distribution, ...]
    mixtures: StoppingMixtures
    future_values: dict[int, tuple[Fraction, Fraction]]


def split_stopping_laws(laws: tuple[Distribution, ...], N: int) -> StoppingMixtures:
    """Split the first deterministic null vector of the energy-law columns.

    Each column has N+1 coordinates and mass one. More than N+1 columns
    therefore have a nonzero null vector whose entries sum to zero. Its
    positive and negative parts, normalized by their equal positive mass,
    are lawful probability weights on independently chosen stopping times.
    """

    if N < 1 or len(laws) <= N + 1:
        raise ValueError("need more than N+1 stopping laws on a positive-N carrier")
    for law in laws:
        if any(not isinstance(mass, Fraction) or mass < 0 for mass in law.values()):
            raise ValueError("source laws must have nonnegative Fraction masses")
        if any(not isinstance(state, int) or not 0 <= state < 1 << N for state in law):
            raise ValueError("source law has an out-of-range state")
        if sum(law.values(), Fraction(0)) != 1:
            raise ValueError("source laws must sum to one")
    columns = [energy_level_distribution(law, N) for law in laws]
    matrix = [[column[level] for column in columns] for level in range(N + 1)]
    rank, pivots = _rref(matrix)
    free = next(j for j in range(len(laws)) if j not in pivots)
    coefficients = [Fraction(0) for _ in laws]
    coefficients[free] = Fraction(1)
    for row, pivot in enumerate(pivots):
        coefficients[pivot] = -matrix[row][free]
    if sum(coefficients, Fraction(0)) != 0 or any(
        sum((c * column[e] for c, column in zip(coefficients, columns, strict=True)), Fraction(0))
        != 0
        for e in range(N + 1)
    ):
        raise ArithmeticError("nullspace certificate failed exact verification")
    positive_mass = sum((max(c, Fraction(0)) for c in coefficients), Fraction(0))
    if positive_mass <= 0:
        raise ArithmeticError("nonzero zero-total null vector has no positive part")
    plus_weights = tuple(max(c, Fraction(0)) / positive_mass for c in coefficients)
    minus_weights = tuple(max(-c, Fraction(0)) / positive_mass for c in coefficients)
    plus = _mix(laws, plus_weights, N)
    minus = _mix(laws, minus_weights, N)
    energy_law = energy_level_distribution(plus, N)
    if energy_law != energy_level_distribution(minus, N):
        raise ArithmeticError("constructed mixtures do not have identical current energy laws")
    return StoppingMixtures(
        rank, free, tuple(coefficients), plus_weights, minus_weights, plus, minus, energy_law
    )


def build_energy_mixture_witness_from_config(config: dict[str, Any]) -> EnergyMixtureWitness:
    """Build the frozen prefix 0..N+1 of the config's mid-temperature run."""

    if config["model"]["family"] != "east" or config["model"]["boundary"] != "wall_up":
        raise ValueError("energy witness requires the declared wall-up East model")
    word = config["protocol"]["word"]
    if len(word) != 3 or word[0]["steps"] != 0:
        raise ValueError("energy witness requires the frozen three-leg Kovacs preparation")
    witness = build_energy_mixture_witness(
        int(config["model"]["N"]),
        Fraction(word[0]["epsilon"]),
        Fraction(word[1]["epsilon"]),
        Fraction(word[2]["epsilon"]),
        int(word[1]["steps"]),
        int(word[2]["steps"]),
    )
    cap = int(config["arithmetic"]["max_denominator_bits"])
    observed = max(
        max_denominator_bits(law)
        for law in (*witness.source_laws, witness.mixtures.plus, witness.mixtures.minus)
    )
    observed = max(
        observed,
        *(
            value.denominator.bit_length()
            for value in (
                *witness.mixtures.coefficients,
                *witness.mixtures.plus_weights,
                *witness.mixtures.minus_weights,
                *(v for pair in witness.future_values.values() for v in pair),
            )
        ),
    )
    if observed > cap:
        raise ValueError(f"energy-mixture certificate denominator bits {observed} exceed cap {cap}")
    return witness


@cache
def build_energy_mixture_witness(
    N: int,
    epsilon_hi: Fraction,
    epsilon_lo: Fraction,
    epsilon_mid: Fraction,
    t_w: int,
    tau_probe: int,
) -> EnergyMixtureWitness:
    """Compute actual preparations; never substitute a formal signed law for one."""

    if N < 1 or t_w < 0 or tau_probe < N + 1 + PROBE_STEPS:
        raise ValueError("all stopping times and continuation horizons must fit the probe window")
    kernel = build_east_kernel(N, epsilon_mid)
    initial = hold(east_stationary(N, epsilon_hi), build_east_kernel(N, epsilon_lo), t_w)
    laws = [initial]
    for _ in range(N + 1):
        laws.append(push(laws[-1], kernel))
    mixtures = split_stopping_laws(tuple(laws), N)
    horizons = tuple(range(1, tau_probe - (N + 1) + 1))
    values = separating_energy_values(mixtures, N, kernel, horizons)
    if values[PROBE_STEPS][0] == values[PROBE_STEPS][1]:
        raise ValueError("current-blind stopping mixtures do not split the declared energy probe")
    return EnergyMixtureWitness(
        N,
        epsilon_hi,
        epsilon_lo,
        epsilon_mid,
        t_w,
        tau_probe,
        tuple(range(N + 2)),
        tuple(laws),
        mixtures,
        values,
    )


def separating_energy_values(
    mixtures: StoppingMixtures,
    N: int,
    kernel: Kernel,
    horizons: tuple[int, ...],
) -> dict[int, tuple[Fraction, Fraction]]:
    """Evaluate actual continuations after the current-only selector is frozen."""

    validate_kernel_rows(kernel)
    if kernel.state_count != 1 << N or not horizons or min(horizons) < 1:
        raise ValueError("invalid carrier or continuation horizons")
    plus, minus = mixtures.plus, mixtures.minus
    values = {}
    for step in range(1, max(horizons) + 1):
        plus, minus = push(plus, kernel), push(minus, kernel)
        if step in horizons:
            values[step] = (
                expectation(plus, lambda state: east_energy(state, N)),
                expectation(minus, lambda state: east_energy(state, N)),
            )
    return values


def _mix(laws: tuple[Distribution, ...], weights: tuple[Fraction, ...], N: int) -> Distribution:
    if sum(weights, Fraction(0)) != 1 or any(w < 0 for w in weights):
        raise ArithmeticError("invalid stopping-time weights")
    return {
        state: value
        for state in range(1 << N)
        if (
            value := sum(
                (w * law.get(state, Fraction(0)) for w, law in zip(weights, laws, strict=True)),
                Fraction(0),
            )
        )
        != 0
    }


def _rref(matrix: list[list[Fraction]]) -> tuple[int, list[int]]:
    rank, pivots = 0, []
    for column in range(len(matrix[0])):
        pivot = next((row for row in range(rank, len(matrix)) if matrix[row][column]), None)
        if pivot is None:
            continue
        matrix[rank], matrix[pivot] = matrix[pivot], matrix[rank]
        divisor = matrix[rank][column]
        matrix[rank] = [value / divisor for value in matrix[rank]]
        for row in range(len(matrix)):
            if row != rank:
                factor = matrix[row][column]
                matrix[row] = [
                    a - factor * b for a, b in zip(matrix[row], matrix[rank], strict=True)
                ]
        pivots.append(column)
        rank += 1
        if rank == len(matrix):
            break
    return rank, pivots
