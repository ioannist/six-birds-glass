"""GT5 memory-dimension diagnostics over route-transport packages."""

from __future__ import annotations

from collections import Counter
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations
from typing import TypedDict

from sixbirds_glass.lenses.catalog import (
    fictive_temperature_index,
    l_energy,
    l_panel_bond_count,
)
from sixbirds_glass.models.east import east_stationary
from sixbirds_glass.models.kernels import spin
from sixbirds_glass.pipeline.diagnostics import max_fiber_size as diagnostics_max_fiber_size
from sixbirds_glass.pipeline.package import RouteTransportPackage
from sixbirds_glass.pipeline.quotients import Signature, comparison_map
from sixbirds_glass.protocols.evolution import Distribution, expectation

CoordinateValue = Callable[[Distribution, int], Fraction]


class BuybackSubsetResult(TypedDict):
    coordinates: tuple[str, ...]
    loss: Fraction
    resolved: bool


@dataclass(frozen=True)
class BuybackCurveResult:
    """Raw subset losses plus the feasible-class envelope."""

    raw_by_budget: dict[int, list[BuybackSubsetResult]]
    envelope: dict[int, Fraction]
    saturation_budget: int | None


def fiber_histogram(package: RouteTransportPackage, interface: str) -> dict[Signature, int]:
    """Return predictive-class counts over each current class."""

    counts = Counter(comparison_map(package, interface).values())
    return dict(counts)


def max_fiber_size(package: RouteTransportPackage, interface: str) -> int:
    """Return GT5 ``MaxFiber`` for one package interface."""

    return diagnostics_max_fiber_size(package, interface)


def declared_scalar_pool(N: int, epsilon_grid: Sequence[Fraction]) -> dict[str, CoordinateValue]:
    """Return the declared scalar memory-coordinate pool for East at ``N``."""

    grid = tuple(epsilon_grid)
    equilibrium_means = {epsilon: _east_equilibrium_mean_energy(epsilon, N) for epsilon in grid}

    def equilibrium_mean_energy(epsilon: Fraction, _lens_N: int) -> Fraction:
        return equilibrium_means[epsilon]

    def t_f(distribution: Distribution, lens_N: int) -> Fraction:
        return expectation(
            distribution,
            lambda state: fictive_temperature_index(
                l_energy(state, lens_N),
                lens_N,
                grid,
                equilibrium_mean_energy=equilibrium_mean_energy,
            ),
        )

    def bond_count(distribution: Distribution, lens_N: int) -> Fraction:
        return expectation(distribution, lambda state: l_panel_bond_count(state, lens_N))

    def first_spin(distribution: Distribution, _lens_N: int) -> Fraction:
        return expectation(distribution, lambda state: int(spin(state, 1)))

    return {"T_f": t_f, "D": bond_count, "n_1": first_spin}


def two_point_squared_error(value_a: Fraction, value_b: Fraction, *, same_group: bool) -> Fraction:
    """Return exact two-point squared error under group-mean prediction."""

    if not same_group:
        return Fraction(0)
    return (value_a - value_b) ** 2 / 2


def buyback_curve(
    mu_k: Distribution,
    pi_eq: Distribution,
    N: int,
    future_value_mu_k: Fraction,
    future_value_pi_eq: Fraction,
    pool: dict[str, CoordinateValue],
    *,
    max_budget: int = 2,
) -> BuybackCurveResult:
    """Compute the raw subset table and monotone buyback envelope exactly."""

    if max_budget < 0:
        raise ValueError("max_budget must be non-negative")

    names = tuple(pool)
    max_size = min(max_budget, len(names))
    raw_by_budget: dict[int, list[BuybackSubsetResult]] = {}
    best_so_far: Fraction | None = None
    envelope: dict[int, Fraction] = {}
    saturation_budget: int | None = None

    for budget in range(max_size + 1):
        subset_rows: list[BuybackSubsetResult] = []
        subsets = ((),) if budget == 0 else combinations(names, budget)
        for subset in subsets:
            coordinates = tuple(subset)
            same_group = _same_coordinate_group(mu_k, pi_eq, N, pool, coordinates)
            loss = two_point_squared_error(
                future_value_mu_k, future_value_pi_eq, same_group=same_group
            )
            subset_rows.append(
                {
                    "coordinates": coordinates,
                    "loss": loss,
                    "resolved": loss == 0,
                }
            )
        raw_by_budget[budget] = subset_rows
        budget_best = min(row["loss"] for row in subset_rows)
        best_so_far = budget_best if best_so_far is None else min(best_so_far, budget_best)
        envelope[budget] = best_so_far
        if saturation_budget is None and best_so_far == 0:
            saturation_budget = budget

    return BuybackCurveResult(
        raw_by_budget=raw_by_budget,
        envelope=envelope,
        saturation_budget=saturation_budget,
    )


def _same_coordinate_group(
    mu_k: Distribution,
    pi_eq: Distribution,
    N: int,
    pool: dict[str, CoordinateValue],
    coordinates: tuple[str, ...],
) -> bool:
    return all(pool[name](mu_k, N) == pool[name](pi_eq, N) for name in coordinates)


def _east_equilibrium_mean_energy(epsilon: Fraction, N: int) -> Fraction:
    stationary = east_stationary(N, epsilon)
    return expectation(stationary, lambda state: l_energy(state, N))
