from fractions import Fraction

from sixbirds_glass.models.east import build_east_kernel
from sixbirds_glass.pipeline.foreclosure import (
    enumerate_energy_predicates,
    foreclosure_sweep,
    predicate_expectation,
)
from sixbirds_glass.pipeline.reflection_witness import reflect_distribution
from sixbirds_glass.protocols.evolution import dirac, hold


def test_enumerate_energy_predicates_is_exhaustive_and_deterministic() -> None:
    predicates = enumerate_energy_predicates(3)

    assert len(predicates) == 16
    assert predicates[0] == frozenset()
    assert predicates[-1] == frozenset({0, 1, 2, 3})


def test_predicate_expectation_is_exact_energy_event_probability() -> None:
    distribution = {0b0011: Fraction(1, 3), 0b0111: Fraction(2, 3)}

    assert predicate_expectation(distribution, 4, frozenset({2})) == Fraction(1, 3)
    assert predicate_expectation(distribution, 4, frozenset({3})) == Fraction(2, 3)
    assert predicate_expectation(distribution, 4, frozenset({2, 3})) == Fraction(1)


def test_foreclosure_sweep_real_reflection_witness_checks_all_energy_predicates() -> None:
    N = 8
    mu = hold(dirac(0), build_east_kernel(N, Fraction(1, 2)), 3)
    h_prime = reflect_distribution(mu, N)

    result = foreclosure_sweep(mu, h_prime, N)

    assert result.total_predicates == 2**9
    assert result.agreeing_predicates == result.total_predicates
    assert result.all_agree
    assert result.first_disagreement is None
