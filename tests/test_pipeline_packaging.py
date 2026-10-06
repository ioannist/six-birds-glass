from fractions import Fraction
from pathlib import Path

import pytest

from sixbirds_glass.lenses.catalog import l_energy
from sixbirds_glass.models.east import build_east_kernel, east_stationary
from sixbirds_glass.models.grid import DEFAULT_EPSILON_GRID
from sixbirds_glass.pipeline.packaging import (
    coarse_grain,
    fiber_partition,
    gibbs_prototype_rule,
    idempotence_defect,
    packaging_endomap,
    relift,
    uniform_prototype_rule,
)
from sixbirds_glass.protocols.evolution import push

pytestmark = pytest.mark.slow


def test_energy_fiber_partition_covers_all_states_once() -> None:
    fibers = fiber_partition(6, l_energy)
    covered = [state for states in fibers.values() for state in states]

    assert set(fibers) == set(range(7))
    assert len(covered) == 64
    assert sorted(covered) == list(range(64))


def test_prototype_rules_are_valid_on_every_energy_fiber() -> None:
    N = 6
    fibers = fiber_partition(N, l_energy)
    rules = (gibbs_prototype_rule(N, Fraction(1, 2)), uniform_prototype_rule())

    for rule in rules:
        for label, states in fibers.items():
            prototype = rule(label, states)
            assert set(prototype) <= set(states)
            assert all(mass >= 0 for mass in prototype.values())
            assert sum(prototype.values(), start=Fraction(0)) == Fraction(1)


def test_weighted_gibbs_style_rule_differs_from_uniform_when_fiber_weights_differ() -> None:
    fibers = {"x": (0, 1)}
    macro = coarse_grain({0: Fraction(1)}, fibers)

    def weighted_rule(_label, states):
        weights = {0: Fraction(3), 1: Fraction(1)}
        total = sum((weights[state] for state in states), start=Fraction(0))
        return {state: weights[state] / total for state in states}

    weighted = relift(macro, fibers, weighted_rule)
    uniform = relift(macro, fibers, uniform_prototype_rule())

    assert weighted == {0: Fraction(3, 4), 1: Fraction(1, 4)}
    assert uniform == {0: Fraction(1, 2), 1: Fraction(1, 2)}
    assert weighted != uniform


def test_packaging_endomap_rows_are_stochastic_for_both_prototype_rules() -> None:
    N = 6
    kernel = build_east_kernel(N, Fraction(1, 2))
    rules = (gibbs_prototype_rule(N, Fraction(1, 2)), uniform_prototype_rule())

    for rule in rules:
        endomap = packaging_endomap(N, kernel, 2, l_energy, rule)
        assert all(endomap.row_sum(state) == Fraction(1) for state in range(endomap.state_count))


def test_gibbs_prototype_equilibrium_fixed_point_identity_exact_for_n6() -> None:
    N = 6
    epsilons = (DEFAULT_EPSILON_GRID[0], DEFAULT_EPSILON_GRID[4], DEFAULT_EPSILON_GRID[-1])

    for epsilon in epsilons:
        stationary = east_stationary(N, epsilon)
        kernel = build_east_kernel(N, epsilon)
        for tau in (1, 2, 4):
            endomap = packaging_endomap(N, kernel, tau, l_energy, gibbs_prototype_rule(N, epsilon))
            assert push(stationary, endomap) == stationary


def test_gibbs_prototype_equilibrium_fixed_point_identity_exact_for_n8_smoke() -> None:
    N = 8
    epsilon = Fraction(1, 2)
    stationary = east_stationary(N, epsilon)
    kernel = build_east_kernel(N, epsilon)
    endomap = packaging_endomap(N, kernel, 1, l_energy, gibbs_prototype_rule(N, epsilon))

    assert push(stationary, endomap) == stationary


def test_relift_coarse_grain_equilibrium_identity_exact() -> None:
    N = 6
    epsilon = Fraction(3, 10)
    stationary = east_stationary(N, epsilon)
    fibers = fiber_partition(N, l_energy)
    macro = coarse_grain(stationary, fibers)

    assert relift(macro, fibers, gibbs_prototype_rule(N, epsilon)) == stationary


def test_idempotence_defect_is_bounded_fraction_not_required_zero() -> None:
    N = 6
    cases = (
        (1, Fraction(1, 5), "gibbs"),
        (2, Fraction(1, 2), "gibbs"),
        (1, Fraction(1, 5), "uniform"),
        (2, Fraction(1, 2), "uniform"),
    )

    for tau, epsilon, prototype_name in cases:
        kernel = build_east_kernel(N, epsilon)
        rule = (
            gibbs_prototype_rule(N, epsilon)
            if prototype_name == "gibbs"
            else uniform_prototype_rule()
        )
        delta = idempotence_defect(packaging_endomap(N, kernel, tau, l_energy, rule))
        assert isinstance(delta, Fraction)
        assert Fraction(0) <= delta <= Fraction(1)


def test_idempotence_defect_guardrail_is_in_code() -> None:
    from sixbirds_glass.pipeline import packaging

    source = Path(packaging.__file__).read_text(encoding="utf-8")

    assert "saturation diagnostic" in (packaging.idempotence_defect.__doc__ or "")
    assert "nontriviality witness" in (packaging.idempotence_defect.__doc__ or "")
    assert "multiple glass states" not in source
