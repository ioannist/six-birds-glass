from fractions import Fraction

from sixbirds_glass.models.east import build_east_kernel, east_stationary
from sixbirds_glass.models.kernels import spin
from sixbirds_glass.pipeline.reflection_witness import (
    reflect_distribution,
    verify_reflection_energy_invariance,
)
from sixbirds_glass.protocols.evolution import dirac, expectation, hold


def test_reflection_preserves_energy_distribution_for_multiple_distributions() -> None:
    N = 8
    stationary = east_stationary(N, Fraction(1, 2))
    non_palindromic_dirac = dirac(0b00010011)
    real_evolved = hold(dirac(0), build_east_kernel(N, Fraction(1, 2)), 3)

    assert verify_reflection_energy_invariance(stationary, N)
    assert verify_reflection_energy_invariance(non_palindromic_dirac, N)
    assert verify_reflection_energy_invariance(real_evolved, N)


def test_real_evolved_reflection_witness_is_genuinely_asymmetric() -> None:
    N = 8
    mu = hold(dirac(0), build_east_kernel(N, Fraction(1, 2)), 3)
    h_prime = reflect_distribution(mu, N)

    n1_mu = expectation(mu, lambda state: int(spin(state, 1)))
    n_n_mu = expectation(mu, lambda state: int(spin(state, N)))
    n1_reflected = expectation(h_prime, lambda state: int(spin(state, 1)))

    assert n1_mu == Fraction(169, 1536)
    assert n_n_mu == Fraction(0)
    assert n1_mu != n_n_mu
    assert abs(n1_mu - n1_reflected) == Fraction(169, 1536)
