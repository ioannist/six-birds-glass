from fractions import Fraction
from itertools import pairwise

import pytest

from sixbirds_glass.lenses.catalog import (
    fictive_temperature_index,
    l_energy,
    l_panel,
    l_panel_reflection_invariant,
    l_tf,
    reflect,
)
from sixbirds_glass.lenses.definability import lens_image_size
from sixbirds_glass.models.east import east_energy, east_stationary
from sixbirds_glass.models.grid import DEFAULT_EPSILON_GRID
from sixbirds_glass.models.kernels import spin


def test_default_epsilon_grid_is_strictly_ascending() -> None:
    assert all(lower < upper for lower, upper in pairwise(DEFAULT_EPSILON_GRID))


@pytest.mark.parametrize("N", (6, 8))
def test_lens_image_sizes_for_energy_and_panel(N: int) -> None:
    configs = range(1 << N)

    energy_image_size = lens_image_size(l_energy(config, N) for config in configs)
    panel_image_size = lens_image_size(l_panel(config, N) for config in range(1 << N))

    assert energy_image_size == N + 1
    assert panel_image_size <= (N + 1) * 2 * N
    assert panel_image_size > energy_image_size


def test_reflection_invariant_panel_and_reflect_involution() -> None:
    N = 8
    configs = range(1 << N)

    for config in configs:
        reflected = reflect(config, N)
        assert reflect(reflected, N) == config
        assert l_panel_reflection_invariant(config, N) == l_panel_reflection_invariant(reflected, N)


def test_first_spin_is_not_reflection_invariant() -> None:
    N = 8

    assert any(spin(config, 1) != spin(reflect(config, N), 1) for config in range(1 << N))


def test_fictive_temperature_index_uses_exact_east_mean_energy() -> None:
    N = 6
    grid = DEFAULT_EPSILON_GRID
    target_index = 2
    target_energy = east_equilibrium_mean_energy(grid[target_index], N)

    assert (
        fictive_temperature_index(
            target_energy, N, grid, equilibrium_mean_energy=east_equilibrium_mean_energy
        )
        == target_index
    )

    for target in (Fraction(0), Fraction(N, 2), Fraction(N)):
        index = fictive_temperature_index(
            target, N, grid, equilibrium_mean_energy=east_equilibrium_mean_energy
        )
        assert 0 <= index < len(grid)


def test_l_tf_returns_energy_and_fictive_temperature_index() -> None:
    N = 6
    config = 0b101011

    energy, index = l_tf(
        config,
        N,
        DEFAULT_EPSILON_GRID,
        equilibrium_mean_energy=east_equilibrium_mean_energy,
    )

    assert energy == east_energy(config, N)
    assert 0 <= index < len(DEFAULT_EPSILON_GRID)


def test_fictive_temperature_index_tie_breaks_to_smallest_grid_index() -> None:
    grid = (Fraction(3, 4), Fraction(1, 4))

    def synthetic_mean(epsilon: Fraction, _N: int) -> Fraction:
        means = {Fraction(3, 4): Fraction(3), Fraction(1, 4): Fraction(1)}
        return means[epsilon]

    assert (
        fictive_temperature_index(
            Fraction(2), N=6, grid=grid, equilibrium_mean_energy=synthetic_mean
        )
        == 0
    )


def east_equilibrium_mean_energy(epsilon: Fraction, N: int) -> Fraction:
    stationary = east_stationary(N, epsilon)
    return sum(probability * east_energy(config, N) for config, probability in stationary.items())
