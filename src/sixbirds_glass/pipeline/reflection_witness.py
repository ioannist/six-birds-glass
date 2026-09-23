"""Reflection-pair helpers for full-energy-lens witnesses."""

from __future__ import annotations

from fractions import Fraction

from sixbirds_glass.lenses.catalog import l_energy, reflect
from sixbirds_glass.protocols.evolution import Distribution


def reflect_distribution(distribution: Distribution, N: int) -> Distribution:
    """Return the reflected distribution ``h'(y) = mu(rho(y))`` exactly."""

    reflected: Distribution = {}
    for state, mass in distribution.items():
        reflected_state = reflect(state, N)
        reflected[reflected_state] = reflected.get(reflected_state, Fraction(0)) + mass
    return {state: mass for state, mass in reflected.items() if mass != 0}


def energy_level_distribution(distribution: Distribution, N: int) -> dict[int, Fraction]:
    """Return exact probability mass at each energy level ``0..N``."""

    levels = {energy: Fraction(0) for energy in range(N + 1)}
    for state, mass in distribution.items():
        levels[l_energy(state, N)] += mass
    return levels


def verify_reflection_energy_invariance(distribution: Distribution, N: int) -> bool:
    """Check exact preservation of the energy-level distribution under reflection."""

    return energy_level_distribution(distribution, N) == energy_level_distribution(
        reflect_distribution(distribution, N), N
    )
